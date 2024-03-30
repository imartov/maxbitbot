'''
The model contains database schemas
At the developer's choice, two approaches can be used:
standard (T-SQL) - using the asyncpg library
ORM - SQLAlchemy
'''

from sqlalchemy import String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey


# ORM approach
class Base(DeclarativeBase):
    ''' This class is the parent class for other table classes '''
    pass


class Users(Base):
    ''' The class is the users table '''
    __tablename__ = 'users'

    chat_id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(String(100))
    login: Mapped[str] = mapped_column(String(100), unique=True)


class Task(Base):
    ''' The class is the task table '''
    __tablename__ = 'task'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("users.chat_id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text)


class CompletedTask(Base):
    ''' The class is the completedtask table '''
    __tablename__ = 'completedtask'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("users.chat_id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text)


# standart SQL approach
async def create_sql_tables() -> None:
    ''' The method creates tables using SQL-query and asyncpg '''
    from database.conn import create_conn
    conn = await create_conn()
    with open ("database\\sql_query\\create_tables.sql", "r", encoding="utf-8") as file:
        sql_query = file.read()
    await conn.execute(sql_query)


if __name__ == "__main__":
    ...
