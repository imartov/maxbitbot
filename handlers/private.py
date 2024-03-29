'''
This module contains event handlers for the user's private messages
'''

import os

from aiogram import Router, types, F, Bot
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update, delete

from kbrds.inline import inline_kb_full_task, inline_kb_name_task
from kbrds.reply import main_kb
from service import get_id_from_message
from handlers.fsm import AddTask, AddUser
import database.sql_query as db
# import post_db


bot = Bot(os.getenv("TG_ROKEN"))
user_router = Router()


@user_router.message(StateFilter(None), CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    """ This handler receives messages with `/start` command """
    if not await db.check_exist_chat_id(message.from_user.id):
        await message.answer(text="Введите свое имя",
                             reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(AddUser.user_name)
    else:
        await message.answer(text="Вы уже зарегистрированы в системе",
                             reply_markup=main_kb)
        

@user_router.message(AddUser.user_name, F.text)
async def input_user_name(message: Message, state: FSMContext) -> None:
    """ This handler receives messages with `/start` command """
    await state.update_data(user_name=message.text)
    await message.answer(text="Введите уникальный логин")
    await state.set_state(AddUser.login)


@user_router.message(AddUser.login, F.text)
async def input_login(message: Message, state: FSMContext) -> None:
    """ This handler receives messages with `/start` command """
    if not await db.check_exist_login(login=message.text):
        await state.update_data(login=message.text)
        data = await state.get_data()
        data["chat_id"] = message.from_user.id
        await db.insert_user(data=data)
        await message.answer(text=f'Вы успешно зарегистрированы\n\
        Ваше имя: {data["user_name"]},\n\
        Ваш логин: {data["login"]}')
        await state.clear()
    else:
        await message.answer(text="Логин уже существует\n\
                             Пожалуйста, повторите попытку")
        await state.set_state(AddUser.login)


@user_router.message(or_f(Command("menu"), (F.text.lower() == "меню")))
async def menu_cmd(message: Message):
    ''' This handler receives messages with `/menu` command '''
    await message.answer(text="Вот меню", reply_markup=main_kb)


@user_router.message(StateFilter(None), F.text.lower() == "добавить задачу")
async def add_task(message: Message, state: FSMContext) -> None:
    ''' This handler receives messages with `/добавить задачу` command '''
    await message.answer(text="Введите имя задачи",
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddTask.name)


@user_router.message(AddTask.name, F.text)
async def add_description(message: Message, state: FSMContext) -> None:
    ''' The handler receives the task name and waits for the task description '''
    await state.update_data(name=message.text)
    data = await state.get_data()
    if "task_id" not in data:
        await message.answer(text="Введите описание задачи",
                             reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer(text="Введите новое описание задачи",
                             reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddTask.description)
    

@user_router.message(AddTask.description, F.text)
async def finish_add_task(message: Message, state: FSMContext) -> None:
    ''' The handler receives the task description and completes adding the task '''
    await state.update_data(description=message.text)
    data = await state.get_data()
    if "task_id" not in data:
        data["chat_id"] = message.from_user.id
        await db.insert_task(data=data)
        await message.answer(text="Задача успешно добавлена",
                             reply_markup=main_kb)
    else:
        await db.update_task(task_id=data["task_id"], data=data)
        await message.answer(text="Задача успешно обновлена",
                             reply_markup=main_kb)
    await state.clear()


@user_router.message(F.text.lower() == "посмотреть задачи")
async def show_tasks(message: Message) -> None:
    ''' This handler receives messages with `/посмотреть задачи` command '''
    tasks = await db.select_tasks(chat_id=message.from_user.id)
    if not tasks:
        await message.answer(text="У Вас отсутствуют задачи",
                             reply_markup=main_kb)
    else:
        await message.answer(text="Вот список Ваших задач")
        for task in tasks:
            await message.answer(text=f"{task['name']}\nid - {task['id']}",
                                reply_markup=inline_kb_name_task)


@user_router.callback_query(F.data == "detail")
async def detail_task(callback: types.CallbackQuery):
    ''' This handler receives messages with '/detail' command '''
    task_id = get_id_from_message(text=callback.message.text)
    task = await db.select_detail_tasks(chat_id=callback.from_user.id, task_id=task_id)
    await bot.send_message(chat_id=callback.from_user.id,
                           text="Имя - {}\nОписание - {}\nid - {}"\
                            .format(task["name"], task["description"], task["id"]),
                            reply_markup=inline_kb_full_task)


# @user_router.callback_query(F.data == "complete")
# async def complete_task(callback: types.CallbackQuery):
#     ''' This handler receives messages with '/complete_task' command '''
#     task_id = get_id_from_message(text=callback.message.text)
#     with post_db.engine.connect() as connection:
#         stmt = select(post_db.tasks)\
#             .where(post_db.tasks.c.id==task_id)
#         task_name = list(connection.execute(stmt))[0][2]
#     with post_db.engine.connect() as connection:
#         stmt = (
#             delete(post_db.tasks).
#             where(post_db.tasks.c.id == task_id)
#         )
#         connection.execute(stmt)
#         connection.commit()
#     with open('messages//complete_task.txt', "r", encoding="utf-8") as file:
#         text = file.read().format(name=task_name)
#     await bot.send_message(chat_id=callback.from_user.id, text=text, reply_markup=main_kb)


@user_router.callback_query(StateFilter(None), F.data == "update")
async def update_task(callback: types.CallbackQuery, state: FSMContext):
    ''' This handler receives messages with '/update' command '''
    task_id = get_id_from_message(text=callback.message.text)
    await state.update_data(task_id=task_id)
    with open('messages//update_task_name.txt', "r", encoding="utf-8") as file:
        text = file.read()
    await bot.send_message(chat_id=callback.from_user.id,
                           text=text,
                           reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddTask.name)


# @user_router.callback_query(F.data == "delete")
# async def delete_task(callback: types.CallbackQuery):
#     ''' This handler receives messages with '/delete' command '''
#     task_id = get_id_from_message(text=callback.message.text)
#     with post_db.engine.connect() as connection:
#         stmt = select(post_db.tasks)\
#             .where(post_db.tasks.c.id==task_id)
#         task_name = list(connection.execute(stmt))[0][2]
#         stmt = (
#                 delete(post_db.tasks).
#                 where(post_db.tasks.c.id == task_id)
#         )
#         connection.execute(stmt)
#         connection.commit()
#     with open('messages//delete_task.txt', "r", encoding="utf-8") as file:
#         text = file.read().format(name=task_name)
#     await bot.send_message(chat_id=callback.from_user.id,
#                            text=text, reply_markup=main_kb)


@user_router.message()
async def error_command(message: Message) -> None:
    ''' This handler receives messages with any command '''
    with open('messages//error_command.txt', "r", encoding="utf-8") as file:
        text = file.read()
    await message.answer(text=text, reply_markup=main_kb)
    