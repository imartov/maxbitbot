'''
This module contains methods for connecting to the database
'''

import os
import asyncpg
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from database.models import Base

# ORM approach
load_dotenv()

engine = create_async_engine(f'postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}', echo=True)

async def create_orm_tables():
    ''' The method creates tables in the database using ORM '''
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_orm_tables():
    ''' The method drops tables in the database using ORM '''
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# standart SQL approach
async def create_conn():
    ''' The method creates and returns a database connection object using asyncpg '''
    conn = await asyncpg.connect(f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}')
    return conn


if __name__ == "__main__":
    pass
