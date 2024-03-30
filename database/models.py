from sqlalchemy import String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey

class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'users'

    chat_id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(String(100))
    login: Mapped[str] = mapped_column(String(100), unique=True)


class Task(Base):
    __tablename__ = 'task'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("users.chat_id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text)


class CompletedTask(Base):
    __tablename__ = 'completedtask'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("users.chat_id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text)


async def create_sql_tables():
    from database.conn import create_conn
    conn = await create_conn()

    await conn.execute('''
        CREATE TABLE users (
            chat_id SERIAL NOT NULL,
            user_name VARCHAR(100) NOT NULL,
            login VARCHAR(100) NOT NULL,
            PRIMARY KEY (chat_id),
            UNIQUE (login)
        )
    ''')

    await conn.execute('''
        CREATE TABLE task (
            id SERIAL NOT NULL,
            chat_id INTEGER NOT NULL,
            name VARCHAR(256) NOT NULL,
            description TEXT NOT NULL,
            PRIMARY KEY (id)
            FOREIGN KEY(chat_id) REFERENCES users (chat_id) ON DELETE CASCADE
        )
    ''')

    await conn.execute('''
        CREATE TABLE completedtask (
            id SERIAL NOT NULL,
            chat_id INTEGER NOT NULL,
            name VARCHAR(256) NOT NULL,
            description TEXT NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(chat_id) REFERENCES users (chat_id) ON DELETE CASCADE
        )
    ''')


async def drop_sql_tables():
    pass