from aiogram import types

import sqlite3

from aiogram.dispatcher import FSMContext

from configs.bot_configs import main_menu_message, dp
from interface.get_saved_questionnaires import favourites_display_favourites, interview_display_interview, \
    employment_display_interview, employee_display_employee
from configs.db_configs import session
from interface.custom_filter import custom_filter
from interface.database.create_db import User
from interface.get_questionnaires_list import get_questionnaires_count, get_questionnaires_list
from interface.signup import user_password_waiting


def is_registered(message):
    user_id = message.from_user.id
    user = session.query(User).filter(User.user_id == user_id).first()

    if user:
        return user
    else:
        return False


@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    result = is_registered(message)
    if result:
        await main_menu_message(message,
                                f"👋Здравствуйте, {result.first_name} {result.last_name}\n"
                                f"Что Вас интересует?")
    else:
        await message.answer("👋Здравствуйте\n\n"
                             "❌<b>Вы ещё не зарегистрированы.</b>\n"
                             "Для продолжения работы пройдите регистрацию")
        await user_password_waiting(message, state)


@dp.message_handler(text=['📚Получить анкеты'])
async def get_questionnaires(message: types.Message, state: FSMContext):
    if is_registered(message):
        filter_choose_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ['💿Базовый фильтр', '📀Кастомный фильтр']
        filter_choose_menu.add(*buttons)
        await message.answer('☑️Выберите фильтр для поиска анкет', reply_markup=filter_choose_menu)
    else:
        await start(message, state)


@dp.message_handler(text=['💿Базовый фильтр'])
async def get_questionnaires(message: types.Message, state: FSMContext):
    if is_registered(message):
        await get_questionnaires_list(message, state, 1)
    else:
        await start(message, state)


@dp.message_handler(text=['📀Кастомный фильтр'])
async def get_questionnaires(message: types.Message, state: FSMContext):
    if is_registered(message):
        await custom_filter(message, state)
    else:
        await start(message, state)


@dp.message_handler(text=["💼Сохранённые анкеты"])
async def get_saved_questionnaires(message: types.Message, state: FSMContext):
    if is_registered(message):
        get_saved_questionnaires_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = ['⭐️Избранное', 'На собеседовании', 'На трудоустройстве', 'Сотрудники', 'Вернуться в главное меню']
        get_saved_questionnaires_keyboard.add(*buttons)
        await message.answer('Какие анкеты вас интересуют?', reply_markup=get_saved_questionnaires_keyboard)
    else:
        await start(message, state)


@dp.message_handler(text=['⭐️Избранное'])
async def get_questionnaires(message: types.Message, state: FSMContext):
    if is_registered(message):
        await favourites_display_favourites(message)
    else:
        await start(message, state)


@dp.message_handler(text=['На собеседовании'])
async def get_interview(message: types.Message, state: FSMContext):
    if is_registered(message):
        await interview_display_interview(message)
    else:
        await start(message, state)


@dp.message_handler(text=['На трудоустройстве'])
async def get_interview(message: types.Message, state: FSMContext):
    if is_registered(message):
        await employment_display_interview(message)
    else:
        await start(message, state)


@dp.message_handler(text=['Сотрудники'])
async def get_interview(message: types.Message, state: FSMContext):
    if is_registered(message):
        await employee_display_employee(message)
    else:
        await start(message, state)


@dp.message_handler(text=['Вернуться в главное меню'])
async def back_main_menu(message: types.Message, state: FSMContext):
    if is_registered(message):
        await main_menu_message(message, "Что Вас интересует?")
    else:
        await start(message, state)


@dp.message_handler(text=['🛠Помощь'])
async def get_questionnaires(message: types.Message, state: FSMContext):
    if is_registered(message):
        await message.answer("<b>🛠Помощь по боту</b>\n\n"
                             "🔶<b>Получить анкеты</b> - поиск анкет по выбранному фильтру\n"
                             "      🔸<b>Базовый фильтр</b> - поиск анкет по базовому фильтру\n"
                             "      🔸<b>Кастомный фильтр</b> - создание или выбор кастомного фильтра\n\n"
                             "🔶<b>Избранное</b> - отображение избранных анкет\n\n"
                             "🔶<b>Помощь</b> - помощь по боту\n\n"
                             "🔶<b>Настройки</b> - настройки бота")
    else:
        await start(message, state)
