from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


# Создание reply кнопок

def get_keyboard(
    *btns: str,
    placeholder: str = None,
    request_contact: int = None,
    request_location: int = None,
    sizes: tuple[int] = (2,),
):
    '''
    Parameters request_contact and request_location must be as indexes of btns args for buttons you need.
    Example:
    get_keyboard(
            "Меню",
            "О магазине",
            "Варианты оплаты",
            "Варианты доставки",
            "Отправить номер телефона",
            placeholder="Что вас интересует?",
            request_contact=4,
            sizes=(2, 2, 1)
        )
    '''
    
    keyboard = ReplyKeyboardBuilder()
    
    for index, text in enumerate(btns, start=0):
        
        if request_contact is not None and index == request_contact:
            keyboard.add(KeyboardButton(text=text, request_contact=True))
            
        elif request_location is not None and index == request_location:
            keyboard.add(KeyboardButton(text=text, request_location=True))
            
        else:
            keyboard.add(KeyboardButton(text=text))
            
    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True,
        input_field_placeholder=placeholder
    )