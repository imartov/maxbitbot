'''
The model contains Finite State Machine objects of aiogram
'''

from aiogram.fsm.state import StatesGroup, State


class AddUser(StatesGroup):
    ''' The class of Finite State Machine object is used when registering a user '''
    user_name = State()
    choose_login = State()
    login_key = State()
    login_value = State()

    texts = {
        'AddUser:user_name':'Введите Ваше имя заново:',
    }


class AddTask(StatesGroup):
    ''' The class of Finite State Machine object is used when adding a task '''
    name = State()
    description = State()
    task_id = State()

    texts = {
        'AddTask:name':'Введите имя задачи заново:',
    }

if __name__ == "__main__":
    pass
