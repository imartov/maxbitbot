import os
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
    

async def update_task(**kwargs):
    conn = await create_conn()
    await conn.execute('''
        UPDATE task SET name = $1, description = $2
        WHERE chat_id = $3''',
        data["name"], data["description"], task_id)
    await conn.close()
    

async def select_tasks(chat_id: int):
    conn = await create_conn()
    rows = await conn.fetch('SELECT id, name FROM task WHERE chat_id = $1', chat_id)
    await conn.close()
    if not rows:
        return None
    data = [dict(row) for row in rows]
    return data


async def select_detail_tasks(chat_id: int, task_id: int):
    conn = await create_conn()
    row = await conn.fetchrow('''SELECT id, name, description FROM task
                              WHERE chat_id = $1 AND id = $2''', chat_id, task_id)
    await conn.close()
    return dict(row)



if __name__ == "__main__":
    data = {
        "name": "New Name",
        "description": "New  description"
    }
    asyncio.run(update_task(task_id=1, data=data))
