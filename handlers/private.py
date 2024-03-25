'''
This module contains event handlers for the user's private messages
'''

import os

from aiogram import Router, types, F, Bot
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update, delete

from kbrds.inline import inline_kb_full_task, inline_kb_name_task
from kbrds.reply import main_kb
from service import get_id_from_message
import post_db


bot = Bot(os.getenv("TG_ROKEN"))
user_router = Router()


class AddTask(StatesGroup):
    ''' The class defines properties for the Finite State Machine
        about adding a new task and changing an existing one '''
    name = State()
    description = State()
    task_id = State()


@user_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """ This handler receives messages with `/start` command """
    data = {
        "chat_id": message.from_user.id,
        "user_name": message.from_user.username
    }
    try:
        await post_db.insert_data(data=data, table_name=post_db.users)
        with open('messages//start.txt', "r", encoding="utf-8") as file:
            text = file.read()
        await message.answer(text=text.format(user_name=message.from_user.full_name),
                            reply_markup=main_kb)
    except IntegrityError:
        with open('messages//start_exist.txt', "r", encoding="utf-8") as file:
            text = file.read()
        await message.answer(text=text.format(user_name=message.from_user.full_name),
                            reply_markup=main_kb)


@user_router.message(or_f(Command("menu"), (F.text.lower() == "меню")))
async def menu_cmd(message: Message):
    ''' This handler receives messages with `/menu` command '''
    with open('messages//show_menu.txt', "r", encoding="utf-8") as file:
        text = file.read()
    await message.answer(text=text, reply_markup=main_kb)


@user_router.message(StateFilter(None), F.text.lower() == "добавить задачу")
async def add_task(message: Message, state: FSMContext) -> None:
    ''' This handler receives messages with `/добавить задачу` command '''
    with open('messages//add_tasks.txt', "r", encoding="utf-8") as file:
        text = file.read()
    await message.answer(text=text, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddTask.name)


@user_router.message(AddTask.name, F.text)
async def add_description(message: Message, state: FSMContext) -> None:
    ''' The handler receives the task name and waits for the task description '''
    await state.update_data(name=message.text)
    data = await state.get_data()
    if "task_id" not in data:
        with open('messages//add_description.txt', "r", encoding="utf-8") as file:
            text = file.read()
        await message.answer(text=text, reply_markup=types.ReplyKeyboardRemove())
    else:
        with open('messages//update_description.txt', "r", encoding="utf-8") as file:
            text = file.read()
        await message.answer(text=text, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddTask.description)
    

@user_router.message(AddTask.description, F.text)
async def finish_add_task(message: Message, state: FSMContext) -> None:
    ''' The handler receives the task description and completes adding the task '''
    await state.update_data(description=message.text)
    data = await state.get_data()
    if "task_id" not in data:
        with open('messages//finish_add_task.txt', "r", encoding="utf-8") as file:
            text = file.read()
        data["chat_id"] = message.from_user.id
        await post_db.insert_data(data=data, table_name=post_db.tasks)
        await message.answer(text=text, reply_markup=main_kb)
    else:
        with post_db.engine.connect() as connection:    
            stmt = (
                update(post_db.tasks).
                where(post_db.tasks.c.id == data["task_id"]).
                values(name=data["name"], description=data["description"])
            )
            connection.execute(stmt)
            connection.commit()
        with open('messages//update_finish.txt', "r", encoding="utf-8") as file:
            text = file.read()
        await message.answer(text=text, reply_markup=main_kb)
    await state.clear()


@user_router.message(F.text.lower() == "посмотреть задачи")
async def show_tasks(message: Message) -> None:
    ''' This handler receives messages with `/посмотреть задачи` command '''
    with open('messages//show_tasks.txt', "r", encoding="utf-8") as file:
        text = file.read()
    await message.answer(text=text)
    with post_db.engine.connect() as connection:
        stmt = select(post_db.tasks)\
            .where(post_db.tasks.c.chat_id==message.from_user.id)
        tasks = list(connection.execute(stmt))
    with open('messages//name_task.txt', "r", encoding="utf-8") as file:
        text = file.read()
    for task in tasks:
        print(task, text)
        await message.answer(text=text.format(name=task[2], id=task[0]),
                             reply_markup=inline_kb_name_task)


@user_router.callback_query(F.data == "detail")
async def detail_task(callback: types.CallbackQuery):
    ''' This handler receives messages with '/detail' command '''
    task_id = get_id_from_message(text=callback.message.text)
    with post_db.engine.connect() as connection:
        stmt = select(post_db.tasks)\
            .where(post_db.tasks.c.id==task_id)
        task = list(connection.execute(stmt))[0]
    with open('messages//full_task.txt', "r", encoding="utf-8") as file:
        text = file.read().format(name=task[2], description=task[3], id=task[0])
    await bot.send_message(chat_id=callback.from_user.id,
                           text=text, reply_markup=inline_kb_full_task)


@user_router.callback_query(F.data == "complete")
async def complete_task(callback: types.CallbackQuery):
    ''' This handler receives messages with '/complete_task' command '''
    task_id = get_id_from_message(text=callback.message.text)
    with post_db.engine.connect() as connection:
        stmt = select(post_db.tasks)\
            .where(post_db.tasks.c.id==task_id)
        task_name = list(connection.execute(stmt))[0][2]
    with post_db.engine.connect() as connection:
        stmt = (
            delete(post_db.tasks).
            where(post_db.tasks.c.id == task_id)
        )
        connection.execute(stmt)
        connection.commit()
    with open('messages//complete_task.txt', "r", encoding="utf-8") as file:
        text = file.read().format(name=task_name)
    await bot.send_message(chat_id=callback.from_user.id, text=text, reply_markup=main_kb)


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


@user_router.callback_query(F.data == "delete")
async def delete_task(callback: types.CallbackQuery):
    ''' This handler receives messages with '/delete' command '''
    task_id = get_id_from_message(text=callback.message.text)
    with post_db.engine.connect() as connection:
        stmt = select(post_db.tasks)\
            .where(post_db.tasks.c.id==task_id)
        task_name = list(connection.execute(stmt))[0][2]
        stmt = (
                delete(post_db.tasks).
                where(post_db.tasks.c.id == task_id)
        )
        connection.execute(stmt)
        connection.commit()
    with open('messages//delete_task.txt', "r", encoding="utf-8") as file:
        text = file.read().format(name=task_name)
    await bot.send_message(chat_id=callback.from_user.id,
                           text=text, reply_markup=inline_kb_full_task)


@user_router.message()
async def error_command(message: Message) -> None:
    ''' This handler receives messages with any command '''
    with open('messages//error_command.txt', "r", encoding="utf-8") as file:
        text = file.read()
    await message.answer(text=text, reply_markup=main_kb)
    