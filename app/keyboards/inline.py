from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Создание инлайн кнопок
def get_callback_btns(
    *,
    btns: dict[str, str],
    sizes: tuple[int] = (2,)
):
    
    keyboard = InlineKeyboardBuilder()
    
    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
    
    return keyboard.adjust(*sizes).as_markup()


# Создание инлайн кнопок c url
def get_url_btns(
    *,
    btns: dict[str, str],
    sizes: tuple[int] = (2,)
):
    
    keyboard = InlineKeyboardBuilder()
    
    for text, url in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, url=url))
    
    return keyboard.adjust(*sizes).as_markup()


# Cоздание инлайн кнопок c url и callback
def get_inline_mix_btns(
    *,
    btns: dict[str, str],
    sizes: tuple[int] = (2,)
):
    
    keyboard = InlineKeyboardBuilder()
    
    for text, value in btns.items():
        if "://" in value:
            keyboard.add(InlineKeyboardButton(text=text, url=value))
        else:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=value))
    
    return keyboard.adjust(*sizes).as_markup()