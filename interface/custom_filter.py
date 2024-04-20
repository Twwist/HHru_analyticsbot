import json
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from configs.bot_configs import dp, main_menu_message
from configs.custom_filter_configs import filter_param_dict
from configs.db_configs import session
from interface.database.create_db import Filter
from interface.get_questionnaires_list import get_questionnaires_list


class CustomFilter(StatesGroup):
    name = State()
    description = State()


async def custom_filter(message: types.Message, state: FSMContext):
    filters = session.query(Filter).filter(Filter.filter_author_id == message.from_user.id).all()
    custom_filter_choose_menu_inline_menu = types.InlineKeyboardMarkup()
    row1_button = [types.InlineKeyboardButton(text="✏️Создать новый фильтр", callback_data="new_custom_filter")]
    if filters:
        for f in filters:
            custom_filter_choose_menu_inline_menu.add(
                types.InlineKeyboardButton(text=f"🔹{f.filter_id}) {f.filter_name}",
                                           callback_data=f"choose_filter_{f.filter_id}_{f.filter_name}")
            )
        custom_filter_choose_menu_inline_menu.row(*row1_button)
        await message.answer('☑️Выберите фильтр для поиска анкет', reply_markup=custom_filter_choose_menu_inline_menu)
    else:
        custom_filter_choose_menu_inline_menu.row(*row1_button)
        await message.answer("У вас нет кастомных фильтров.\n"
                             "Создайте новый или выберите базовый фильтр в прошлом меню",
                             reply_markup=custom_filter_choose_menu_inline_menu)


@dp.callback_query_handler(text_contains="new_custom_filter")
async def create_new_custom_filter(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите название нового фильтра")
    await callback_query.message.delete()
    await state.set_state(CustomFilter.name)


@dp.message_handler(state=CustomFilter.name)
async def handle_fiter_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    text = '<b>Список доступных параметров:</b>\n\n'
    for k in filter_param_dict.keys():
        text += f"🔸<code>{k}</code> \n"

    await message.answer(
        'Принято, теперь напишите какие критерии будет учитывать фильтр и через пробел выберите значение параметра\n\n' + text)
    await state.set_state(CustomFilter.description)


@dp.message_handler(state=CustomFilter.description)
async def handle_fiter_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)

    data = await state.get_data()
    new_filter = Filter(filter_author_id=message.from_user.id, filter_name=data['name'],
                        filter_description=data['description'])
    session.add(new_filter)
    session.commit()

    await main_menu_message(message, f'✅Фильтр <b>{data["name"]}</b> успешно создан')
    await state.finish()


@dp.callback_query_handler(text_contains="choose_filter_")
async def choose_filter(callback_query: types.CallbackQuery, state: FSMContext):
    filter_name = callback_query.data.split('_')[-1]
    filter_id = callback_query.data.split('_')[-2]
    await callback_query.message.delete()
    await callback_query.message.answer(f"✅Филтьтр «{filter_name}» успешно выбран")
    await get_questionnaires_list(callback_query.message, state, filter_id)
