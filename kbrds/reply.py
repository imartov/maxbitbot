'''
This module contains reply buttons
'''

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить задачу"),
            KeyboardButton(text="Посмотреть задачи"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберете действие",
    selective=True
)
