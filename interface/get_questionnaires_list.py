import json

import numpy as np
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy import update

from configs.bot_configs import dp, main_menu_message, bot
from configs.db_configs import session
from interface.database.create_db import Filter, Questionnaire, User
from catboost import CatBoostRegressor, Pool


class QuestionnairesGetting(StatesGroup):
    count = State()
    filter_id = State()


coefficients = {
    'Желаемая_должность': 1500,
    'Опыт_работы': 1000,
    'Требуемая_ЗП': 100,
    'Валюта': 100,
    'Возраст': 10,
    'Год_окончания': 1,
    'Город_проживания': 2500,
    'Дата_обновления': 1,
    'Дата_создания': 1,
    'Предыдущая_должность': 100,
    'Запрашиваемая_ЗП': -1,
    'Имя': 1,
    'Название_организации': 100,
    'Название_уч_зав': 1,
    'Начало_работы': 1,
    'Отчество': 1,
    'Отрасль_компании': 100,
    'Окончание_работы': 1,
    'Пол_соискателя': 1000,
    'Почта': 1,
    'Регион_расположения_организации': 10,
    'Сертификаты_соискателя': 1,
    'Специальность': 100,
    'Телефон': 1,
    'Тип_уч_зав': 1,
    'Образование': 2000,
    'Фамилия': 1
}

# Загрузка сохраненной модели
loaded_model = CatBoostRegressor()
loaded_model.load_model('configs/catboost_model.bin')
feature_importances = loaded_model.get_feature_importance()


async def filter_questionnaires(filter_id):
    filter_description = session.query(Filter).filter(Filter.filter_id == filter_id).first().filter_description
    result = []
    for line in filter_description.split('\n'):
        result.append({line.split()[0]: line.split()[1]})
    return result


async def sort_resumes(state: FSMContext):
    async with state.proxy() as proxy_data:
        filter_id = proxy_data.get('filter_id')
        filter_params = await filter_questionnaires(filter_id)

    resumes = []

    questionnaires = session.query(Questionnaire).all()
    for row in questionnaires:
        item = row.__dict__
        resume = {
            'ID': item.get('id'),
            'Фамилия': item.get('last_name'),
            'Имя': item.get('first_name'),
            'Желаемая_должность': item.get('title'),
            'Предыдущая_должность': item.get('position'),
            'Опыт_работы': item.get('total_experience'),
            'Требуемая_ЗП': item.get('amount'),
            'Валюта': item.get('currency'),
            'Возраст': item.get('age'),
            'Город_проживания': item.get('area'),
            'Сертификаты': item.get('certificate'),
            'Год_окончания': item.get('education_primary_year'),
            'Дата_обновления': item.get('updated_at'),
            'Дата_создания': item.get('created_at'),
            'Должность': item.get('position'),
            'Запрашиваемая_ЗП': item.get('salary_amount'),
            'Название_организации': item.get('company'),
            'Название_уч_зав': item.get('education_primary_organization'),
            'Начало_работы': item.get('start'),
            'Отчество': item.get('middle_name'),
            'Отрасль_компании': item.get('industry'),
            'Окончание_работы': item.get('end'),
            'Пол_соискателя': item.get('gender'),
            'Почта': item.get('email'),
            'Регион_расположения_организации': item.get('area'),
            'Сертификаты_соискателя': item.get('certificate'),
            'Специальность': item.get('education_primary_result'),
            'Телефон': item.get('phone'),
            'Тип_уч_зав': item.get('education_primary_name'),
            'Образование': item.get('level')
        }
        resumes.append(resume)

    sorted_resumes = []

    for resume in resumes:
        total_score = 0
        for filter_param in filter_params:
            param_key = list(filter_param.keys())[0]
            param_value = list(filter_param.values())[0]
            if param_key == 'Требуемая_ЗП':
                total_score -= int(resume.get(param_key))
            elif param_key == 'Опыт_работы':
                total_score += int(resume.get(param_key)) * coefficients[param_key]
            else:
                if resume.get(param_key) == param_value:
                    total_score += coefficients[param_key]
        sorted_resumes.append((resume, total_score))

    sorted_resumes.sort(key=lambda x: x[1], reverse=True)
    sorted_resumes = [resume[0] for resume in sorted_resumes]

    return sorted_resumes


async def get_questionnaires_list(message: types.Message, state: FSMContext, filter_id):
    print(filter_id)
    await state.update_data(filter_id=filter_id)
    await message.answer('Выберите количество анкет для поиска', reply_markup=ReplyKeyboardRemove())
    await state.set_state(QuestionnairesGetting.count)


@dp.message_handler(state=QuestionnairesGetting.count)
async def get_questionnaires_count(message: types.Message, state: FSMContext):
    try:
        count = int(message.text)
        await get_questionnaire_list(message, count, state)
        await state.update_data(count=count)
    except ValueError:
        await message.answer("❌<b>Неправильный формат данных.</b> Пожалуйста, введите целое число.")


async def get_questionnaire_list(message: types.Message, count: int, state: FSMContext):
    async with state.proxy() as proxy_data:
        filter_id = proxy_data.get('filter_id')
        filter_params = await filter_questionnaires(filter_id)

    questionnaires_list = await sort_resumes(state)
    questionnaires_list = questionnaires_list[:count]

    questionnaires_settings_inline_keyboard = types.InlineKeyboardMarkup(row_width=2)

    row1_button = [types.InlineKeyboardButton(text="⚙️Редактировать фильтр", callback_data="filter_edit")]
    row2_button = [types.InlineKeyboardButton(text="📤Выгрузить все анкеты", callback_data="get_all_questionnaires")]
    row3_button = [types.InlineKeyboardButton(text="🔎Получить данные про конкретную анкету",
                                              callback_data="get_specifically_questionnaire"), ]
    row4_button = [types.InlineKeyboardButton(text="⤴️Главное меню", callback_data="back_main_menu")]

    questionnaires_settings_inline_keyboard.row(*row1_button)
    questionnaires_settings_inline_keyboard.row(*row2_button)
    questionnaires_settings_inline_keyboard.row(*row3_button)
    questionnaires_settings_inline_keyboard.row(*row4_button)

    text = ''
    for i in questionnaires_list:
        resume_info = []
        for param_dict in filter_params:
            for param, value in param_dict.items():
                if param in i:
                    resume_info.append(f"<b>{param}:</b> {i[param]}")
        title, experience, sal_t = i.get('Желаемая_должность', ''), i.get('Опыт_работы', ''), i.get('Требуемая_ЗП', '')
        data_for_model = np.array([title, experience]).reshape(1, -1)
        predict = str(loaded_model.predict(data_for_model) + experience * 5000).split(".")[0][1::]
        resume_info.append("<b>Достойная зарплата на рынке:</b> " + predict)
        text += (f"ID: {i.get('ID', '')} <b>👤{i.get('Фамилия', '')} {i.get('Имя', '')}</b>\n" +
                 "\n".join(resume_info) + "\n\n")

    await message.answer(f'🔎Найденные по данному фильтру анкеты:\n\n {text}',
                         reply_markup=questionnaires_settings_inline_keyboard)
    await state.finish()
    await state.update_data(count=count)
    await state.update_data(filter_id=filter_id)


# Обработчик для кнопки "Редактировать фильтр"
@dp.callback_query_handler(text="filter_edit")
async def filter_edit(call: types.CallbackQuery):
    filter_edit_text = '⚙️Редактировать текущий фильтр:\n\n'
    filter_edit_inline_keyboard = types.InlineKeyboardMarkup()
    filter_edit_inline_keyboard.add(
        types.InlineKeyboardButton(text="📌Сохранить изменения", callback_data="save_filter_edit"),
        types.InlineKeyboardButton(text="⬅️Назад", callback_data="back_to_get_questionnaire_list_menu")
    )
    await call.message.edit_text(filter_edit_text, reply_markup=filter_edit_inline_keyboard)


@dp.callback_query_handler(text="get_all_questionnaires")
async def get_all_questionnaires(call: types.CallbackQuery):
    await call.message.answer('⏳Загружаю анкеты...')


@dp.callback_query_handler(text="get_specifically_questionnaire")
async def get_specifically_questionnaire(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        count = data.get('count')

    get_specifically_questionnaire_text = '<b>🔖Выберите анкету</b>\n\n'

    get_specifically_questionnaire_inline_keyboard = types.InlineKeyboardMarkup()

    for i in range(1, count + 1):
        get_specifically_questionnaire_inline_keyboard.add(
            types.InlineKeyboardButton(text=f"🔹Анкета N{i}", callback_data=f"get_specifically_questionnaire_number_{i}")
        )

    get_specifically_questionnaire_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️Назад", callback_data="back_to_get_questionnaire_list_menu"))

    await call.message.edit_text(get_specifically_questionnaire_text,
                                 reply_markup=get_specifically_questionnaire_inline_keyboard)


@dp.callback_query_handler(text_contains="get_specifically_questionnaire_number_")
async def get_specifically_questionnaire_number_(call: types.CallbackQuery, state: FSMContext):
    i = await sort_resumes(state)
    i = i[int(call.data.split("_")[-1]) - 1]
    await state.update_data(r_id=i['ID'])

    title, experience, sal_t = i.get('Желаемая_должность', ''), i.get('Опыт_работы', ''), i.get('Требуемая_ЗП', '')
    data_for_model = np.array([title, experience]).reshape(1, -1)
    predict = str(loaded_model.predict(data_for_model) + experience * 5000).split(".")[0][1::]
    s = predict

    text = f'<b>🔹Данные по анкете N{call.data.split("_")[-1]}</b>\n\n\n'
    text += (f"🔹 <b>ID: {i['ID']}\n\n</b>"
             f"👤 <b>{i['Фамилия']} {i['Имя']}</b>\n\n"
             f"🎯 <b>Желаемая_должность:</b> {i['Желаемая_должность']}\n\n"
             f"👨‍🏫 <b>Предыдущая_должность:</b> {i['Предыдущая_должность']}\n\n"
             f"📅 <b>Опыт_работы:</b> {i['Опыт_работы']}\n\n"
             f"💰 <b>Требуемая_ЗП:</b> {i['Требуемая_ЗП']} {i['Валюта']}\n"
             f"<b>Достойная_зарплата: </b> {s}\n\n"
             f"👴 <b>Возраст:</b> {i['Возраст']}\n\n"
             f"🏙️ <b>Город_проживания:</b> {i['Город_проживания']}\n\n"
             f"📜 <b>Сертификаты:</b> {i['Сертификаты']}\n\n"
             f"🎓 <b>Образование:</b> {i['Образование']}")

    back_to_get_questionnaire_list_inline_keyboard = types.InlineKeyboardMarkup()

    questionnaire_id = i['ID']
    is_favourite = session.query(Questionnaire).filter(Questionnaire.id == questionnaire_id).first().favourites
    if is_favourite:
        back_to_get_questionnaire_list_inline_keyboard.add(
            types.InlineKeyboardButton(text="🌕 Удалить из избранного", callback_data="delete_to_favorites"), )
    else:
        back_to_get_questionnaire_list_inline_keyboard.add(
            types.InlineKeyboardButton(text="🌑 Добавить в избранное", callback_data="add_to_favorites"), )

    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="🛎Статус", callback_data=f"status_{call.data.split('_')[-1]}"), )

    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_get_choose_list_menu"))

    # Редактирование сообщения с кнопками и обновленным текстом
    await call.message.edit_text(text, reply_markup=back_to_get_questionnaire_list_inline_keyboard)


@dp.callback_query_handler(text="add_to_favorites")
async def add_to_favorites(call: types.CallbackQuery):
    questionnaire_id = call.message.text.split("\n\n\n")[1].split("\n\n")[0].split(": ")[1]
    session.execute(update(Questionnaire).where(Questionnaire.id == questionnaire_id).values(favourites=True))
    session.commit()

    back_to_get_questionnaire_list_inline_keyboard = types.InlineKeyboardMarkup()
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="🌕Удалить из избранных", callback_data="delete_to_favorites"), )
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️Назад", callback_data="back_to_get_choose_list_menu"))

    await call.message.edit_text(call.message.text, reply_markup=back_to_get_questionnaire_list_inline_keyboard)


@dp.callback_query_handler(text="delete_to_favorites")
async def delete_from_favorites(call: types.CallbackQuery):
    questionnaire_id = call.message.text.split("\n\n\n")[1].split("\n\n")[0].split(": ")[1]
    session.execute(update(Questionnaire).where(Questionnaire.id == questionnaire_id).values(favourites=False))
    session.commit()

    back_to_get_questionnaire_list_inline_keyboard = types.InlineKeyboardMarkup()
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="🌑Добавить в избранное", callback_data="add_to_favorites"), )
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️Назад", callback_data="back_to_get_choose_list_menu"))

    # Отправка обновленного текста сообщения с кнопками и подтверждением удаления из избранного
    await call.message.edit_text(call.message.text,
                                 reply_markup=back_to_get_questionnaire_list_inline_keyboard)


@dp.callback_query_handler(text_contains="status_")
async def status(call: types.CallbackQuery, state: FSMContext):
    i = call.data.split("_")[-1]
    get_status_keyboard = types.InlineKeyboardMarkup()
    get_status_keyboard.add(types.InlineKeyboardButton(text="Собеседование", callback_data="interview_status"))
    get_status_keyboard.add(types.InlineKeyboardButton(text="Трудоустройство", callback_data="employment_status"))
    get_status_keyboard.add(types.InlineKeyboardButton(text="Сотрудник", callback_data="employee_status"))
    get_status_keyboard.add(
        types.InlineKeyboardButton(text="🔙Назад", callback_data=f"get_specifically_questionnaire_number_{i}"))
    text = call.message.text + f"\n\nВыберите статус для анкеты:"
    await call.message.edit_text(text, reply_markup=get_status_keyboard)


@dp.callback_query_handler(text_contains="_status")
async def get_status(call: types.CallbackQuery, state: FSMContext):
    new_status_name = call.data.split("_")[0]
    async with state.proxy() as proxy_data:
        r_id = proxy_data.get('r_id')
    session.execute(
        update(Questionnaire).where(Questionnaire.id == r_id).values(status=new_status_name)
    )
    session.commit()
    await bot.answer_callback_query(call.id, text='✅Статус изменён', show_alert=True)


@dp.callback_query_handler(text='back_to_get_questionnaire_list_menu')
async def back_to_get_questionnaire_list_menu(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as proxy_data:
        filter_id = proxy_data.get('filter_id')
        filter_params = await filter_questionnaires(filter_id)
        count = proxy_data['count']

    questionnaires_list = await sort_resumes(state)
    questionnaires_list = questionnaires_list[:count]

    questionnaires_settings_inline_keyboard = types.InlineKeyboardMarkup(row_width=2)  # Установите ширину строк

    # Создайте кнопки для каждой строки
    row1_button = [types.InlineKeyboardButton(text="⚙️Редактировать фильтр", callback_data="filter_edit")]
    row2_button = [types.InlineKeyboardButton(text="📤Выгрузить все анкеты", callback_data="get_all_questionnaires")]
    row3_button = [types.InlineKeyboardButton(text="🔎Получить данные про конкретную анкету",
                                              callback_data="get_specifically_questionnaire"), ]
    row4_button = [types.InlineKeyboardButton(text="⤴️Главное меню", callback_data="back_main_menu")]

    # Добавьте кнопки в клавиатуру
    questionnaires_settings_inline_keyboard.row(*row1_button)
    questionnaires_settings_inline_keyboard.row(*row2_button)
    questionnaires_settings_inline_keyboard.row(*row3_button)
    questionnaires_settings_inline_keyboard.row(*row4_button)

    text = ''
    for i in questionnaires_list:
        resume_info = []
        for param_dict in filter_params:
            for param, value in param_dict.items():
                if param in i:
                    resume_info.append(f"<b>{param}:</b> {i[param]}")
        title, experience, sal_t = i.get('Желаемая_должность', ''), i.get('Опыт_работы', ''), i.get('Требуемая_ЗП', '')
        data_for_model = np.array([title, experience]).reshape(1, -1)
        predict = str(loaded_model.predict(data_for_model) + experience * 5000).split(".")[0][1::]
        resume_info.append("<b>Достойная зарплата на рынке:</b> " + predict)
        text += (f"ID: {i.get('ID', '')} <b>👤{i.get('Фамилия', '')} {i.get('Имя', '')}</b>\n" +
                 "\n".join(resume_info) + "\n\n")

    await call.message.edit_text(f'🔎Найденные по данному фильтру анкеты:\n\n {text}',
                                 reply_markup=questionnaires_settings_inline_keyboard)


@dp.callback_query_handler(text='back_to_get_choose_list_menu')
async def back_to_get_questionnaire_list_menu(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        count = data.get('count')

    get_specifically_questionnaire_text = '<b>🔖Выберите анкету</b>\n\n'

    get_specifically_questionnaire_inline_keyboard = types.InlineKeyboardMarkup()

    for i in range(1, count + 1):
        get_specifically_questionnaire_inline_keyboard.add(
            types.InlineKeyboardButton(text=f"🔹Анкета N{i}", callback_data=f"get_specifically_questionnaire_number_{i}")
        )

    get_specifically_questionnaire_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️Назад", callback_data="back_to_get_questionnaire_list_menu"))

    await call.message.edit_text(get_specifically_questionnaire_text,
                                 reply_markup=get_specifically_questionnaire_inline_keyboard)


@dp.callback_query_handler(text='back_main_menu')
async def back_to_get_questionnaire_list_menu(call: types.CallbackQuery, state: FSMContext):
    await main_menu_message(call, "💬Вы в главном меню")
