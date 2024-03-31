'''
This module contains event handlers for the user's private messages
'''

from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import asyncpg

from kbrds.inline import get_callback_btns
from kbrds.reply import main_kb
from handlers.fsm import AddTask, AddUser
import database.sql_query as db


user_router = Router()


@user_router.message(StateFilter(None), CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    """ The handler receives messages with `/start` command """
    if not await db.check_exist_chat_id(message.from_user.id):
        with open("messages/start.txt", "r", encoding="utf-8") as file:
            hello_text = file.read().format(user_name=message.from_user.full_name)
        await message.answer(text=hello_text)
        await message.answer(text="Введите свое имя",
                             reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(AddUser.user_name)
    else:
        await message.answer(text="Вы уже зарегистрированы в системе",
                             reply_markup=main_kb)


@user_router.message(StateFilter('*'), Command("отмена"))
@user_router.message(StateFilter('*'), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    ''' The handler processes "отмена" message with FSM active '''
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("Действия отменены", reply_markup=main_kb)


@user_router.message(StateFilter('*'), Command("назад"))
@user_router.message(StateFilter('*'), F.text.casefold() == "назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:
    ''' The handler processes "отмена" message with FSM active '''
    current_state = await state.get_state()
    using_state = AddTask if "AddTask" in str(current_state) else AddUser
    if current_state == AddTask.name or current_state == AddUser.user_name:
        await message.answer('Предыдущего шага нет\nВведите "отмена", чтобы оменить действия')
        return
    elif current_state == AddUser.login_value:
        await message.answer("Ок, выберите, каким будет Ваш логин",
                             reply_markup=get_callback_btns(btns={
                                 "username телеграма": "tgusername",
                                 "Собственный": "enteryourself"
                             }))
        await state.set_state(AddUser.login_key)
        return
    previous = None
    for step in using_state.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            with open("messages/prev_step.txt", "r", encoding="utf-8") as file:
                text = file.read().format(step=using_state.texts[previous.state])
            await message.answer(text=text)
            return
        previous = step


@user_router.message(AddUser.user_name, F.text)
async def choose_login(message: Message, state: FSMContext) -> None:
    ''' The handler processes the message when Add User.choose_login is active in FSM '''
    await state.update_data(user_name=message.text)
    with open("messages/choose_login.txt", "r", encoding="utf-8") as file:
        text = file.read()
    await message.answer(text=text,
                         reply_markup=get_callback_btns(btns={
                             "username телеграма": "tgusername",
                             "Собственный": "enteryourself"
                         }))
    await state.set_state(AddUser.login_key)


@user_router.callback_query(AddUser.login_key, F.data == "tgusername")
async def choose_tgusername(callback: types.CallbackQuery, state: FSMContext):
    ''' The handler processes the "username телеграма" inline-button
        when Add User.login_key is active in FSM '''
    await state.update_data(login_value=callback.from_user.username)
    data = await state.get_data()
    data["chat_id"] = callback.from_user.id
    await db.insert_user(data=data)
    with open("messages/success_register.txt", "r", encoding="utf-8") as file:
        text = file.read().format(user_name=data["user_name"], login=data["login_value"])
    await callback.message.answer(text=text, reply_markup=main_kb)
    await state.clear()


@user_router.callback_query(AddUser.login_key, F.data == "enteryourself")
async def choose_enteryourself(callback: types.CallbackQuery, state: FSMContext):
    ''' The handler processes the "Собственный" inline-button
        when Add User.login_key is active in FSM '''
    await callback.message.answer(text="Введите уникальный логин",
                                  reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddUser.login_value)


@user_router.message(AddUser.login_value, F.text)
async def input_user_name(message: Message, state: FSMContext) -> None:
    ''' The handler processes the message when Add User.login_value is active in FSM
        and takes the username value for the user when registering '''
    if not await db.check_exist_login(login=message.text):
        await state.update_data(login_value=message.text)
        data = await state.get_data()
        data["chat_id"] = message.from_user.id
        await db.insert_user(data=data)
        with open("messages/success_register.txt", "r", encoding="utf-8") as file:
            text = file.read().format(user_name=data["user_name"], login=data["login_value"])
        await message.answer(text=text, reply_markup=main_kb)
        await state.clear()
    else:
        await message.answer(text="Логин уже существует\n\
                                Пожалуйста, повторите попытку")
        await state.set_state(AddUser.login_value)


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
    ''' The handler receives the task name and waits for the task description
        in FSM when Add AddTask.name is active in FSM '''
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
    ''' The handler receives the task description
        in FSM when Add AddTask.description is active in FSM
        and completes adding the task '''
    try:
        await state.update_data(description=message.text)
        data = await state.get_data()
        if "task_id" not in data:
            data["chat_id"] = message.from_user.id
            await db.insert_task(data=data)
            await message.answer(text="Задача успешно добавлена",
                                reply_markup=main_kb)
        else:
            await db.update_task(data=data, task_id=data["task_id"])
            await message.answer(text="Задача успешно обновлена",
                                reply_markup=main_kb)
    except asyncpg.exceptions.ForeignKeyViolationError:
        with open("messages/no_register.txt", "r", encoding="utf-8") as file:
            text = file.read()
        await message.answer(text=text, reply_markup=types.ReplyKeyboardRemove())
    finally:
        await state.clear()


@user_router.message(F.text.lower() == "посмотреть задачи")
async def show_tasks(message: Message) -> None:
    ''' This handler receives `/посмотреть задачи` inline-button command '''
    tasks = await db.select_tasks(chat_id=message.from_user.id)
    if not tasks:
        await message.answer(text="У Вас отсутствуют задачи",
                             reply_markup=main_kb)
    else:
        await message.answer(text="Вот список Ваших задач")
        for task in tasks:
            await message.answer(text=f"{task['name']}",
                                reply_markup=get_callback_btns(btns={
                                        "Подробнее": f"detail_{task['id']}",
                                        "Выполнить": f"complete_{task['id']}"
                                }))


@user_router.callback_query(F.data.startswith("detail_"))
async def detail_task(callback: types.CallbackQuery):
    ''' This handler receives '/detail' inline-button command '''
    task_id = int(callback.data.split("_")[-1])
    task = await db.select_detail_tasks(task_id=task_id)
    await callback.message.answer(text=f"Имя - {task['name']}\nОписание - {task['description']}",
                                  reply_markup=get_callback_btns(btns={
                                          "Изменить": f"update_{task_id}",
                                          "Удалить": f"delete_{task_id}",
                                          "Выполнить": f"complete_{task_id}",
                                  }))


@user_router.callback_query(F.data.startswith("complete_"))
async def complete_task(callback: types.CallbackQuery):
    ''' This handler receives '/complete_task' inline-button command '''
    task_id = task_id = int(callback.data.split("_")[-1])
    task_name = await db.complete_task(task_id=task_id)
    await callback.message.answer(text=f"Задача - {task_name} - выполнена",
                                  reply_markup=main_kb)


@user_router.callback_query(StateFilter(None), F.data.startswith("update_"))
async def update_task(callback: types.CallbackQuery, state: FSMContext):
    ''' This handler receives '/update' inline-button command '''
    task_id = task_id = int(callback.data.split("_")[-1])
    await state.update_data(task_id=task_id)
    await callback.message.answer(text="Введите новое имя задачи",
                                  reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddTask.name)


@user_router.callback_query(F.data.startswith("delete_"))
async def delete_task(callback: types.CallbackQuery):
    ''' This handler receives '/delete' inline-button command '''
    task_id = int(callback.data.split("_")[-1])
    task_name = await db.delete_task(task_id=task_id)
    await callback.message.answer(text=f"Задача - {task_name} - удалена",
                                  reply_markup=main_kb)


@user_router.message()
async def error_command(message: Message) -> None:
    ''' This handler receives messages with any command '''
    await message.answer(text="Некорректная команда\nПожалуйста, повторите ввод",
                         reply_markup=main_kb)
    