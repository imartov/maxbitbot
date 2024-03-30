from aiogram.fsm.state import StatesGroup, State


class AddUser(StatesGroup):
    user_name = State()
    choose_login = State()
    login_key = State()
    login_value = State()

    texts = {
        'AddUser:user_name':'Введите Ваше имя заново:',
    }


class AddTask(StatesGroup):
    ''' The class defines properties for the Finite State Machine
        about adding a new task and changing an existing one '''
    name = State()
    description = State()
    task_id = State()

    texts = {
        'AddTask:name':'Введите имя задачи заново:',
    }
