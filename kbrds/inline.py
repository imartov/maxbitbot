'''
This module contains inline buttons
'''

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


inline_kb_full_task = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Изменить", callback_data="update"),
            InlineKeyboardButton(text="Удалить", callback_data="delete")
        ],
        [
            InlineKeyboardButton(text="Выполнить", callback_data="complete")
        ]
    ]
)

inline_kb_name_task = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Подробнее", callback_data="detail"),
            InlineKeyboardButton(text="Выполнить", callback_data="complete")
        ]
    ]
)
