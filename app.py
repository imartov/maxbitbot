'''
This module is the main module for launching and managing a telegram bot
'''

import os
import sys

import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy

from handlers.private import user_router
from common.bot_cmds_list import private
from database.conn import create_orm_tables, drop_orm_tables


bot = Bot(os.getenv("TG_ROKEN"))
dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.USER_IN_CHAT)
dp.include_router(user_router)


async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_orm_tables()
    else:
        await create_orm_tables()

async def on_shutdown(bot):
    print('бот лег')


async def main() -> None:
    ''' This method implements a sequence of commands to launch a telegram bot '''
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
