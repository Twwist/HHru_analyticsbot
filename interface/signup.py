from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from configs.bot_configs import dp, main_menu_message
from configs.db_configs import session
from interface.database.create_db import User


class SignUp(StatesGroup):
    password = State()
    name = State()


async def user_password_waiting(message: types.Message, state: FSMContext):
    await message.answer("🔐<b>Подтвердите, что вы сотрудник 'AMBITY'.</b>\n\n"
                         "Введите пароль:")
    await state.set_state(SignUp.password)


@dp.message_handler(state=SignUp.password)
async def handle_user_password(message: types.Message, state: FSMContext):
    password = '1234'
    if message.text == password:
        await sign_up_user(message, state)
    else:
        await state.update_data(password=message.text)
        await user_password_waiting(message, state)
        await message.answer("❌<b>Неправильный пароль.</b> Попробуйте ещё раз.")


async def sign_up_user(message: types.Message, state: FSMContext):
    await message.answer('✅<b>Пароль введён верно.</b>\n\n'
                         '👤Введите вашу <b>Фамилию и Имя</b> через пробел\n'
                         'Пример корректных данных: <b>Нигматуллин Айдар</b>')
    await state.set_state(SignUp.name)


@dp.message_handler(state=SignUp.name)
async def users_su(message: types.Message, state: FSMContext):
    if len(message.text.split()) != 2:
        await message.answer(
            '❌<b>Фамилия или имя введены неверно.</b> Пример корректных данных: <b>Нигматуллин Айдар</b>')
    else:
        first_name, last_name = message.text.split()
        new_user = User(user_id=message.chat.id, first_name=first_name, last_name=last_name)
        session.add(new_user)
        session.commit()
        await main_menu_message(message, f'👋Здравствуйте, {first_name} {last_name},\n Вы успешно зарегистрировались')
        await state.finish()
