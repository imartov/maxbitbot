'''
The model contains methods for interacting with the database using SQL
'''

from typing import Any
from database.conn import create_conn


async def check_exist_chat_id(chat_id: int):
    ''' The method checks for the presence of the passed chat_id in the users table,
        if there is, it returns True, otherwise None '''
    conn = await create_conn()
    row = await conn.fetchrow('SELECT chat_id FROM users WHERE chat_id = $1', chat_id)
    await conn.close()
    return bool(row)


async def check_exist_login(login: str):
    ''' The method checks for the presence of the passed login in the users table,
    if there is, it returns True, otherwise None '''
    conn = await create_conn()
    row = await conn.fetchrow('SELECT login FROM users WHERE login = $1', login)
    await conn.close()
    return bool(row)


async def insert_user(data: dict):
    ''' The method inserts data into the users table '''
    conn = await create_conn()
    await conn.execute('''
        INSERT INTO users(chat_id, user_name, login) VALUES($1, $2, $3)''',
        data["chat_id"], data["user_name"], data["login_value"])


async def insert_task(data: dict):
    ''' The method inserts data into the task table '''
    conn = await create_conn()
    await conn.execute('''
        INSERT INTO task(chat_id, name, description) VALUES($1, $2, $3)''',
        data["chat_id"], data["name"], data["description"])


async def update_task(data: dict, **kwargs: Any):
    ''' The method updates the data in the task table '''
    conn = await create_conn()
    await conn.execute('''
        UPDATE task SET name = $1, description = $2
        WHERE id = $3''',
        data["name"], data["description"], kwargs.get("task_id"))
    await conn.close()


async def select_tasks(chat_id: int) -> list:
    ''' The method extracts a list of records from the task table
        by the passed chat_id and returns them as a list from dictionaries '''
    conn = await create_conn()
    rows = await conn.fetch('SELECT id, name FROM task WHERE chat_id = $1', chat_id)
    await conn.close()
    if not rows:
        return None
    data = [dict(row) for row in rows]
    return data


async def select_detail_tasks(task_id: int) -> dict:
    ''' The method extracts an entry in the task table
        by the passed id and returns it as a dictionary '''
    conn = await create_conn()
    row = await conn.fetchrow('''SELECT id, name, description FROM task
                                 WHERE id = $1''', task_id)
    await conn.close()
    return dict(row)


async def complete_task(**kwargs: Any) -> str:
    ''' The method deletes an row in the task table by the passed id
        and inserts the entry into the completedtask table and returns the task name '''
    conn = await create_conn()
    row = await conn.fetchrow('''SELECT chat_id, name, description FROM task
                                 WHERE id = $1
                              ''', kwargs.get("task_id"))
    completed_task = dict(row)
    task_name = completed_task["name"]
    await conn.execute('''INSERT INTO completedtask(chat_id, name, description)
                          VALUES($1, $2, $3)
                       ''', completed_task["chat_id"], completed_task["name"],
                       completed_task["description"])
    await conn.execute('''DELETE FROM task
                          WHERE id = $1''', kwargs.get("task_id"))
    await conn.close()
    return task_name


async def delete_task(**kwargs: Any) -> str:
    ''' The method deletes an row in the task table by the passed id
        and returns the task name '''
    conn = await create_conn()
    row = await conn.fetchrow('''SELECT name FROM task
                                 WHERE id = $1''', kwargs.get("task_id"))
    task_name = dict(row)["name"]
    await conn.execute('''DELETE FROM task
                          WHERE id = $1''', kwargs.get("task_id"))
    return task_name


if __name__ == "__main__":
    pass
