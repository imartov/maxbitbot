import os
from typing import Any
import asyncio
import asyncpg
from dotenv import load_dotenv

load_dotenv()

async def create_conn():
    conn = await asyncpg.connect(f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}')
    return conn


async def check_exist_chat_id(chat_id: int):
    conn = await create_conn()
    row = await conn.fetchrow('SELECT * FROM users WHERE chat_id = $1', chat_id)
    await conn.close()
    return bool(row)


async def check_exist_login(login: str):
    conn = await create_conn()
    row = await conn.fetchrow('SELECT login FROM users WHERE login = $1', login)
    await conn.close()
    return bool(row)


async def insert_user(data: dict):
    conn = await create_conn()
    await conn.execute('''
        INSERT INTO users(chat_id, user_name, login) VALUES($1, $2, $3)''',
        data["chat_id"], data["user_name"], data["login"])
    

async def insert_task(data: dict):
    conn = await create_conn()
    await conn.execute('''
        INSERT INTO task(chat_id, name, description) VALUES($1, $2, $3)''',
        data["chat_id"], data["name"], data["description"])
    

async def update_task(data: dict, **kwargs: Any):
    conn = await create_conn()
    await conn.execute('''
        UPDATE task SET name = $1, description = $2
        WHERE id = $3''',
        data["name"], data["description"], kwargs.get("task_id"))
    await conn.close()
    

async def select_tasks(chat_id: int) -> list:
    conn = await create_conn()
    rows = await conn.fetch('SELECT id, name FROM task WHERE chat_id = $1', chat_id)
    await conn.close()
    if not rows:
        return None
    data = [dict(row) for row in rows]
    return data


async def select_detail_tasks(chat_id: int, task_id: int) -> dict:
    conn = await create_conn()
    row = await conn.fetchrow('''SELECT id, name, description FROM task
                              WHERE chat_id = $1 AND id = $2''', chat_id, task_id)
    await conn.close()
    return dict(row)


async def complete_task(**kwargs: Any) -> str:
    conn = await create_conn()
    row = await conn.fetchrow('''SELECT chat_id, name, description FROM task
                                 WHERE id = $1
                              ''', kwargs.get("task_id"))
    completed_task = dict(row)
    task_name = completed_task["name"]
    await conn.execute('''INSERT INTO completedtask(chat_id, name, description)
                          VALUES($1, $2, $3)
                       ''', completed_task["chat_id"], completed_task["name"], completed_task["description"])
    await conn.execute('''DELETE FROM task
                          WHERE id = $1''', kwargs.get("task_id"))
    await conn.close()
    return task_name


async def delete_task(**kwargs: Any) -> str:
    conn = await create_conn()
    row = await conn.fetchrow('''SELECT name FROM task
                                 WHERE id = $1''', kwargs.get("task_id"))
    task_name = dict(row)["name"]
    await conn.execute('''DELETE FROM task
                          WHERE id = $1''', kwargs.get("task_id"))
    return task_name


if __name__ == "__main__":
    pass
