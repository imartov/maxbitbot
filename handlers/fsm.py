from aiogram.fsm.state import StatesGroup, State


class AddUser(StatesGroup):
    user_name = State()
    login = State()


class AddTask(StatesGroup):
    ''' The class defines properties for the Finite State Machine
        about adding a new task and changing an existing one '''
    name = State()
    description = State()
    task_id = State()
