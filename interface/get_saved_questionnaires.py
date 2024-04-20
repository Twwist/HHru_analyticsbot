from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from catboost import CatBoostRegressor
from sqlalchemy import update

from configs.bot_configs import dp
from configs.bot_token import token
from configs.db_configs import session
from interface.database.create_db import Questionnaire


#
#
#
#
#

async def favourites_display_favourites(message: types.Message):
    favourites = session.query(Questionnaire).filter(Questionnaire.favourites == True).all()

    if favourites:
        questionnaires_settings_inline_keyboard = types.InlineKeyboardMarkup(row_width=2)

        row2_button = [
            types.InlineKeyboardButton(text="📤Выгрузить все избранные",
                                       callback_data="get_all_favourites_questionnaires")]
        row3_button = [types.InlineKeyboardButton(text="🔎Получить данные про конкретную анкету",
                                                  callback_data="get_specifically_favourites_questionnaire"), ]
        row4_button = [types.InlineKeyboardButton(text="⤴️Главное меню", callback_data="back_main_menu")]

        questionnaires_settings_inline_keyboard.row(*row2_button)
        questionnaires_settings_inline_keyboard.row(*row3_button)
        questionnaires_settings_inline_keyboard.row(*row4_button)

        text = ''
        for favourite in favourites:
            text += (f"🔹<b>ID:</b> {favourite.id}\n"
                     f"👤 {favourite.first_name} {favourite.last_name}\n"
                     f"🎯 <b>Желаемая_должность:</b> {favourite.title}\n"
                     f"👨‍🏫 <b>Предыдущая_должность:</b> {favourite.position}\n"
                     f"📅 <b>Опыт_работы:</b> {favourite.total_experience}\n\n")

        await message.answer(f'⭐️<b>Избранные анкеты:</b>\n\n'
                             f'{text}', reply_markup=questionnaires_settings_inline_keyboard)
    else:
        text = "У вас пока нет избранных анкет."
        await message.answer(text)


@dp.callback_query_handler(text="get_specifically_favourites_questionnaire")
async def favourites_get_specifically_questionnaire(call: types.CallbackQuery):
    favourites = session.query(Questionnaire).filter(Questionnaire.favourites == True).all()
    count = len(favourites)
    get_specifically_questionnaire_text = '<b>🔖Выберите избранную анкету</b>\n\n'

    get_specifically_questionnaire_inline_keyboard = types.InlineKeyboardMarkup()

    for i in range(1, count + 1):
        get_specifically_questionnaire_inline_keyboard.add(
            types.InlineKeyboardButton(text=f"🔹Анкета N{i}",
                                       callback_data=f"get_specifically_favourites_questionnaire_number_{i}")
        )

    get_specifically_questionnaire_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️Назад", callback_data="back_to_get_favourites_questionnaire_list_menu"))

    await call.message.edit_text(get_specifically_questionnaire_text,
                                 reply_markup=get_specifically_questionnaire_inline_keyboard)


@dp.callback_query_handler(text_contains="get_specifically_favourites_questionnaire_number_")
async def favourites_get_specifically_favourites_questionnaire_number_(call: types.CallbackQuery):
    favourites = session.query(Questionnaire).filter(Questionnaire.favourites == True).all()
    i = favourites[int(call.data.split("_")[-1]) - 1]

    back_to_get_questionnaire_list_inline_keyboard = types.InlineKeyboardMarkup()
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="🌕 Удалить из избранного", callback_data="favorites_delete_to_favorites"), )

    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️ Назад", callback_data="get_specifically_favourites_questionnaire"))

    # Если есть анкеты в избранном, формируем текст для вывода
    text = "<b>⭐️Избранные анкеты:</b>\n\n"
    for favourite in [i]:
        text += (f"🔹<b>ID:</b> {favourite.id}\n\n"
                 f"👤 {favourite.first_name} {favourite.last_name}\n\n"
                 f"🎯 <b>Желаемая_должность:</b> {favourite.title}\n\n"
                 f"👨‍🏫 <b>Предыдущая_должность:</b> {favourite.position}\n\n"
                 f"📅 <b>Опыт_работы:</b> {favourite.total_experience}\n\n"
                 f"💰 <b>Требуемая_ЗП:</b> {favourite.amount} {favourite.currency}\n\n"
                 f"👴 <b>Возраст:</b> {favourite.age}\n\n"
                 f"🏙️ <b>Город_проживания:</b> {favourite.area}\n\n"
                 f"📜 <b>Сертификаты:</b> {favourite.certificate}\n\n"
                 f"🎓 <b>Образование:</b> {favourite.level}\n\n"
                 )
        text += "\n"
    await call.message.edit_text(text, reply_markup=back_to_get_questionnaire_list_inline_keyboard)


@dp.callback_query_handler(text="favorites_add_to_favorites")
async def favourites_add_to_favorites(call: types.CallbackQuery):
    questionnaire_id = call.message.text.split("\n\n")[1].split(": ")[1]
    session.execute(update(Questionnaire).where(Questionnaire.id == questionnaire_id).values(favourites=True))
    session.commit()

    back_to_get_questionnaire_list_inline_keyboard = types.InlineKeyboardMarkup()
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="🌕Удалить из избранных", callback_data="favorites_delete_to_favorites"), )
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️Назад", callback_data="get_specifically_favourites_questionnaire"))

    await call.message.edit_text(call.message.text, reply_markup=back_to_get_questionnaire_list_inline_keyboard)


@dp.callback_query_handler(text="favorites_delete_to_favorites")
async def favourites_delete_from_favorites(call: types.CallbackQuery):
    questionnaire_id = int(call.message.text.split('\n\n')[1].split('\n')[0].split(': ')[1])
    session.execute(update(Questionnaire).where(Questionnaire.id == questionnaire_id).values(favourites=False))
    session.commit()

    back_to_get_questionnaire_list_inline_keyboard = types.InlineKeyboardMarkup()
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="🌑Добавить в избранное", callback_data="favorites_add_to_favorites"), )
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️Назад", callback_data="get_specifically_favourites_questionnaire"))

    # Отправка обновленного текста сообщения с кнопками и подтверждением удаления из избранного
    await call.message.edit_text(call.message.text,
                                 reply_markup=back_to_get_questionnaire_list_inline_keyboard)


@dp.callback_query_handler(text="back_to_get_favourites_questionnaire_list_menu")
async def favourites_back_to_get_favourites_questionnaire_list_menu(call: types.CallbackQuery):
    favourites = session.query(Questionnaire).filter(Questionnaire.favourites == True).all()

    if favourites:
        questionnaires_settings_inline_keyboard = types.InlineKeyboardMarkup(row_width=2)

        row2_button = [
            types.InlineKeyboardButton(text="📤Выгрузить все избранные",
                                       callback_data="get_all_favourites_questionnaires")]
        row3_button = [types.InlineKeyboardButton(text="🔎Получить данные про конкретную анкету",
                                                  callback_data="get_specifically_favourites_questionnaire"), ]
        row4_button = [types.InlineKeyboardButton(text="⤴️Главное меню", callback_data="back_main_menu")]

        questionnaires_settings_inline_keyboard.row(*row2_button)
        questionnaires_settings_inline_keyboard.row(*row3_button)
        questionnaires_settings_inline_keyboard.row(*row4_button)

        text = ''
        for favourite in favourites:
            text += (f"🔹<b>ID:</b> {favourite.id}\n"
                     f"👤 {favourite.first_name} {favourite.last_name}\n"
                     f"🎯 <b>Желаемая_должность:</b> {favourite.title}\n"
                     f"👨‍🏫 <b>Предыдущая_должность:</b> {favourite.position}\n"
                     f"📅 <b>Опыт_работы:</b> {favourite.total_experience}\n\n")

        await call.message.edit_text(f'⭐️<b>Избранные анкеты:</b>\n\n'
                                     f'{text}', reply_markup=questionnaires_settings_inline_keyboard)
    else:
        text = "У вас пока нет избранных анкет."
        await call.message.edit_text(text)


#
#
#
#
#

async def interview_display_interview(message: types.Message):
    interviews = session.query(Questionnaire).filter(Questionnaire.status == 'interview').all()

    if interviews:
        questionnaires_settings_inline_keyboard = types.InlineKeyboardMarkup(row_width=2)

        row2_button = [
            types.InlineKeyboardButton(text="📤Выгрузить все на собеседовании",
                                       callback_data="get_all_interview_questionnaires")]
        row3_button = [types.InlineKeyboardButton(text="🔎Получить данные про конкретную анкету",
                                                  callback_data="get_specifically_interview_questionnaire"), ]
        row4_button = [types.InlineKeyboardButton(text="⤴️Главное меню", callback_data="back_main_menu")]

        questionnaires_settings_inline_keyboard.row(*row2_button)
        questionnaires_settings_inline_keyboard.row(*row3_button)
        questionnaires_settings_inline_keyboard.row(*row4_button)

        text = ''
        for interview in interviews:
            text += (f"🔹<b>ID:</b> {interview.id}\n"
                     f"👤 {interview.first_name} {interview.last_name}\n"
                     f"🎯 <b>Желаемая_должность:</b> {interview.title}\n"
                     f"👨‍🏫 <b>Предыдущая_должность:</b> {interview.position}\n"
                     f"📅 <b>Опыт_работы:</b> {interview.total_experience}\n\n")

        await message.answer(f'<b>Анкеты на собеседовании:</b>\n\n'
                             f'{text}', reply_markup=questionnaires_settings_inline_keyboard)
    else:
        text = "У вас пока нет анкет на собеседовании."
        await message.answer(text)


@dp.callback_query_handler(text="get_specifically_interview_questionnaire")
async def interview_get_specifically_questionnaire(call: types.CallbackQuery):
    interviews = session.query(Questionnaire).filter(Questionnaire.status == 'interview').all()
    count = len(interviews)
    get_specifically_questionnaire_text = '<b>🔖Выберите избранную анкету</b>\n\n'

    get_specifically_questionnaire_inline_keyboard = types.InlineKeyboardMarkup()

    for i in range(1, count + 1):
        get_specifically_questionnaire_inline_keyboard.add(
            types.InlineKeyboardButton(text=f"🔹Анкета N{i}",
                                       callback_data=f"get_specifically_interview_questionnaire_number_{i}")
        )

    get_specifically_questionnaire_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️Назад", callback_data="back_to_get_interview_questionnaire_list_menu"))

    await call.message.edit_text(get_specifically_questionnaire_text,
                                 reply_markup=get_specifically_questionnaire_inline_keyboard)


@dp.callback_query_handler(text_contains="get_specifically_interview_questionnaire_number_")
async def interview_get_specifically_favourites_questionnaire_number_(call: types.CallbackQuery):
    interviews = session.query(Questionnaire).filter(Questionnaire.status == 'interview').all()
    i = interviews[int(call.data.split("_")[-1]) - 1]

    back_to_get_questionnaire_list_inline_keyboard = types.InlineKeyboardMarkup()
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="🌕 Удалить из анкет собеседования",
                                   callback_data="interview_delete_to_interview"), )

    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️ Назад", callback_data="get_specifically_interview_questionnaire"))

    # Если есть анкеты в избранном, формируем текст для вывода
    text = "<b>Анкеты на собеседовании:</b>\n\n"
    for interview in [i]:
        text += (f"🔹<b>ID:</b> {interview.id}\n\n"
                 f"👤 {interview.first_name} {interview.last_name}\n\n"
                 f"🎯 <b>Желаемая_должность:</b> {interview.title}\n\n"
                 f"👨‍🏫 <b>Предыдущая_должность:</b> {interview.position}\n\n"
                 f"📅 <b>Опыт_работы:</b> {interview.total_experience}\n\n"
                 f"💰 <b>Требуемая_ЗП:</b> {interview.amount} {interview.currency}\n\n"
                 f"👴 <b>Возраст:</b> {interview.age}\n\n"
                 f"🏙️ <b>Город_проживания:</b> {interview.area}\n\n"
                 f"📜 <b>Сертификаты:</b> {interview.certificate}\n\n"
                 f"🎓 <b>Образование:</b> {interview.level}\n\n"
                 )
        text += "\n"
    await call.message.edit_text(text, reply_markup=back_to_get_questionnaire_list_inline_keyboard)


@dp.callback_query_handler(text="interview_delete_to_interview")
async def interview_delete_from_interview(call: types.CallbackQuery):
    questionnaire_id = int(call.message.text.split('\n\n')[1].split('\n')[0].split(': ')[1])
    session.execute(update(Questionnaire).where(Questionnaire.id == questionnaire_id).values(status=''))
    session.commit()

    back_to_get_questionnaire_list_inline_keyboard = types.InlineKeyboardMarkup()
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="Добавить в анкеты собеседования",
                                   callback_data="interview_add_to_interview"), )
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️Назад", callback_data="get_specifically_interview_questionnaire"))

    # Отправка обновленного текста сообщения с кнопками и подтверждением удаления из избранного
    await call.message.edit_text(call.message.text, reply_markup=back_to_get_questionnaire_list_inline_keyboard)


@dp.callback_query_handler(text="interview_add_to_interview")
async def interview_add_to_interview(call: types.CallbackQuery):
    questionnaire_id = call.message.text.split("\n\n")[1].split(": ")[1]
    session.execute(update(Questionnaire).where(Questionnaire.id == questionnaire_id).values(status='interview'))
    session.commit()

    back_to_get_questionnaire_list_inline_keyboard = types.InlineKeyboardMarkup()
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="Удалить из анкет собеседования",
                                   callback_data="interview_delete_to_interview"), )
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️Назад", callback_data="get_specifically_interview_questionnaire"))

    await call.message.edit_text(call.message.text, reply_markup=back_to_get_questionnaire_list_inline_keyboard)


@dp.callback_query_handler(text="back_to_get_interview_questionnaire_list_menu")
async def interview_back_to_get_interview_questionnaire_list_menu(call: types.CallbackQuery):
    interviews = session.query(Questionnaire).filter(Questionnaire.status == 'interview').all()

    if interviews:
        questionnaires_settings_inline_keyboard = types.InlineKeyboardMarkup(row_width=2)

        row2_button = [
            types.InlineKeyboardButton(text="📤Выгрузить все на собеседовании",
                                       callback_data="get_all_interview_questionnaires")]
        row3_button = [types.InlineKeyboardButton(text="🔎Получить данные про конкретную анкету",
                                                  callback_data="get_specifically_interview_questionnaire"), ]
        row4_button = [types.InlineKeyboardButton(text="⤴️Главное меню", callback_data="back_main_menu")]

        questionnaires_settings_inline_keyboard.row(*row2_button)
        questionnaires_settings_inline_keyboard.row(*row3_button)
        questionnaires_settings_inline_keyboard.row(*row4_button)

        text = ''
        for interview in interviews:
            text += (f"🔹<b>ID:</b> {interview.id}\n"
                     f"👤 {interview.first_name} {interview.last_name}\n"
                     f"🎯 <b>Желаемая_должность:</b> {interview.title}\n"
                     f"👨‍🏫 <b>Предыдущая_должность:</b> {interview.position}\n"
                     f"📅 <b>Опыт_работы:</b> {interview.total_experience}\n\n")

        await call.message.edit_text(f'<b>Анкеты на собеседовании:</b>\n\n'
                                     f'{text}', reply_markup=questionnaires_settings_inline_keyboard)
    else:
        text = "У вас пока нет анкет на собеседовании."
        await call.message.edit_text(text)


#
#
#
#
#

async def employment_display_interview(message: types.Message):
    employments = session.query(Questionnaire).filter(Questionnaire.status == 'employment').all()

    if employments:
        questionnaires_settings_inline_keyboard = types.InlineKeyboardMarkup(row_width=2)

        row2_button = [
            types.InlineKeyboardButton(text="📤Выгрузить все на трудоустройстве",
                                       callback_data="get_all_employment_questionnaires")]
        row3_button = [types.InlineKeyboardButton(text="🔎Получить данные про конкретную анкету",
                                                  callback_data="get_specifically_employments_questionnaire"), ]
        row4_button = [types.InlineKeyboardButton(text="⤴️Главное меню", callback_data="back_main_menu")]

        questionnaires_settings_inline_keyboard.row(*row2_button)
        questionnaires_settings_inline_keyboard.row(*row3_button)
        questionnaires_settings_inline_keyboard.row(*row4_button)

        text = ''
        for employment in employments:
            text += (f"🔹<b>ID:</b> {employment.id}\n"
                     f"👤 {employment.first_name} {employment.last_name}\n"
                     f"🎯 <b>Желаемая_должность:</b> {employment.title}\n"
                     f"👨‍🏫 <b>Предыдущая_должность:</b> {employment.position}\n"
                     f"📅 <b>Опыт_работы:</b> {employment.total_experience}\n\n")

        await message.answer(f'<b>Анкеты на трудоустройстве:</b>\n\n'
                             f'{text}', reply_markup=questionnaires_settings_inline_keyboard)
    else:
        text = "У вас пока нет анкет на трудоустройстве."
        await message.answer(text)


@dp.callback_query_handler(text="get_specifically_employments_questionnaire")
async def employment_get_specifically_questionnaire(call: types.CallbackQuery):
    employments = session.query(Questionnaire).filter(Questionnaire.status == 'employment').all()
    count = len(employments)
    get_specifically_questionnaire_text = '<b>🔖Выберите анкету на трудоустройстве</b>\n\n'

    get_specifically_questionnaire_inline_keyboard = types.InlineKeyboardMarkup()

    for i in range(1, count + 1):
        get_specifically_questionnaire_inline_keyboard.add(
            types.InlineKeyboardButton(text=f"🔹Анкета N{i}",
                                       callback_data=f"get_specifically_employment_questionnaire_number_{i}")
        )

    get_specifically_questionnaire_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️Назад", callback_data="back_to_get_employment_questionnaire_list_menu"))

    await call.message.edit_text(get_specifically_questionnaire_text,
                                 reply_markup=get_specifically_questionnaire_inline_keyboard)


@dp.callback_query_handler(text_contains="get_specifically_employment_questionnaire_number_")
async def employment_get_specifically_employment_questionnaire_number_(call: types.CallbackQuery):
    employments = session.query(Questionnaire).filter(Questionnaire.status == 'employment').all()
    i = employments[int(call.data.split("_")[-1]) - 1]

    back_to_get_questionnaire_list_inline_keyboard = types.InlineKeyboardMarkup()
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="🌕 Удалить анкету трудоустройства",
                                   callback_data="employment_delete_to_employment"), )

    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️ Назад", callback_data="get_specifically_employments_questionnaire"))

    # Если есть анкеты в избранном, формируем текст для вывода
    text = "<b>Анкеты трудоустройства:</b>\n\n"
    for employment in [i]:
        text += (f"🔹<b>ID:</b> {employment.id}\n\n"
                 f"👤 {employment.first_name} {employment.last_name}\n\n"
                 f"🎯 <b>Желаемая_должность:</b> {employment.title}\n\n"
                 f"👨‍🏫 <b>Предыдущая_должность:</b> {employment.position}\n\n"
                 f"📅 <b>Опыт_работы:</b> {employment.total_experience}\n\n"
                 f"💰 <b>Требуемая_ЗП:</b> {employment.amount} {employment.currency}\n\n"
                 f"👴 <b>Возраст:</b> {employment.age}\n\n"
                 f"🏙️ <b>Город_проживания:</b> {employment.area}\n\n"
                 f"📜 <b>Сертификаты:</b> {employment.certificate}\n\n"
                 f"🎓 <b>Образование:</b> {employment.level}\n\n"
                 )
        text += "\n"
    await call.message.edit_text(text, reply_markup=back_to_get_questionnaire_list_inline_keyboard)


@dp.callback_query_handler(text="employment_delete_to_employment")
async def employment_delete_from_employment(call: types.CallbackQuery):
    questionnaire_id = int(call.message.text.split('\n\n')[1].split('\n')[0].split(': ')[1])
    session.execute(update(Questionnaire).where(Questionnaire.id == questionnaire_id).values(status=''))
    session.commit()

    back_to_get_questionnaire_list_inline_keyboard = types.InlineKeyboardMarkup()
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="Добавить в анкеты трудоустройства",
                                   callback_data="employment_add_to_employment"), )
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️Назад", callback_data="get_specifically_employments_questionnaire"))

    # Отправка обновленного текста сообщения с кнопками и подтверждением удаления из избранного
    await call.message.edit_text(call.message.text, reply_markup=back_to_get_questionnaire_list_inline_keyboard)


@dp.callback_query_handler(text="employment_add_to_employment")
async def employment_add_to_employment(call: types.CallbackQuery):
    questionnaire_id = call.message.text.split("\n\n")[1].split(": ")[1]
    session.execute(update(Questionnaire).where(Questionnaire.id == questionnaire_id).values(status='employment'))
    session.commit()

    back_to_get_questionnaire_list_inline_keyboard = types.InlineKeyboardMarkup()
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="Удалить из анкет трудоустройства",
                                   callback_data="employment_delete_to_employment"), )
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️Назад", callback_data="get_specifically_employments_questionnaire"))

    await call.message.edit_text(call.message.text, reply_markup=back_to_get_questionnaire_list_inline_keyboard)


@dp.callback_query_handler(text="back_to_get_employment_questionnaire_list_menu")
async def employment_back_to_get_employment_questionnaire_list_menu(call: types.CallbackQuery):
    employments = session.query(Questionnaire).filter(Questionnaire.status == 'employment').all()

    if employments:
        questionnaires_settings_inline_keyboard = types.InlineKeyboardMarkup(row_width=2)

        row2_button = [
            types.InlineKeyboardButton(text="📤Выгрузить все на трудоустройстве",
                                       callback_data="get_all_employment_questionnaires")]
        row3_button = [types.InlineKeyboardButton(text="🔎Получить данные про конкретную анкету",
                                                  callback_data="get_specifically_employments_questionnaire"), ]
        row4_button = [types.InlineKeyboardButton(text="⤴️Главное меню", callback_data="back_main_menu")]

        questionnaires_settings_inline_keyboard.row(*row2_button)
        questionnaires_settings_inline_keyboard.row(*row3_button)
        questionnaires_settings_inline_keyboard.row(*row4_button)

        text = ''
        for employment in employments:
            text += (f"🔹<b>ID:</b> {employment.id}\n"
                     f"👤 {employment.first_name} {employment.last_name}\n"
                     f"🎯 <b>Желаемая_должность:</b> {employment.title}\n"
                     f"👨‍🏫 <b>Предыдущая_должность:</b> {employment.position}\n"
                     f"📅 <b>Опыт_работы:</b> {employment.total_experience}\n\n")

        await call.message.edit_text(f'<b>Анкеты на трудоустройстве:</b>\n\n'
                                     f'{text}', reply_markup=questionnaires_settings_inline_keyboard)
    else:
        text = "У вас пока нет анкет на трудоустройстве."
        await call.message.edit_text(text)


#
#
#
#
#

async def employee_display_employee(message: types.Message):
    employees = session.query(Questionnaire).filter(Questionnaire.status == 'employee').all()

    if employees:
        questionnaires_settings_inline_keyboard = types.InlineKeyboardMarkup(row_width=2)

        row2_button = [
            types.InlineKeyboardButton(text="📤Выгрузить все из анкет сотрудников",
                                       callback_data="get_all_employee_questionnaires")]
        row3_button = [types.InlineKeyboardButton(text="🔎Получить данные про конкретную анкету",
                                                  callback_data="get_specifically_employee_questionnaire"), ]
        row4_button = [types.InlineKeyboardButton(text="⤴️Главное меню", callback_data="back_main_menu")]

        questionnaires_settings_inline_keyboard.row(*row2_button)
        questionnaires_settings_inline_keyboard.row(*row3_button)
        questionnaires_settings_inline_keyboard.row(*row4_button)

        text = ''
        for employee in employees:
            text += (f"🔹<b>ID:</b> {employee.id}\n"
                     f"👤 {employee.first_name} {employee.last_name}\n"
                     f"🎯 <b>Желаемая_должность:</b> {employee.title}\n"
                     f"👨‍🏫 <b>Предыдущая_должность:</b> {employee.position}\n"
                     f"📅 <b>Опыт_работы:</b> {employee.total_experience}\n\n")

        await message.answer(f'<b>Анкеты сотрудников:</b>\n\n'
                             f'{text}', reply_markup=questionnaires_settings_inline_keyboard)
    else:
        text = "У вас пока нет анкет на трудоустройстве."
        await message.answer(text)


@dp.callback_query_handler(text="get_specifically_employee_questionnaire")
async def employee_get_specifically_questionnaire(call: types.CallbackQuery):
    employees = session.query(Questionnaire).filter(Questionnaire.status == 'employee').all()
    count = len(employees)
    get_specifically_questionnaire_text = '<b>🔖Выберите анкету сотрудника</b>\n\n'

    get_specifically_questionnaire_inline_keyboard = types.InlineKeyboardMarkup()

    for i in range(1, count + 1):
        get_specifically_questionnaire_inline_keyboard.add(
            types.InlineKeyboardButton(text=f"🔹Анкета N{i}",
                                       callback_data=f"get_specifically_employee_questionnaire_number_{i}")
        )

    get_specifically_questionnaire_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️Назад", callback_data="back_to_get_employee_questionnaire_list_menu"))

    await call.message.edit_text(get_specifically_questionnaire_text,
                                 reply_markup=get_specifically_questionnaire_inline_keyboard)


@dp.callback_query_handler(text_contains="get_specifically_employee_questionnaire_number_")
async def employee_get_specifically_employee_questionnaire_number_(call: types.CallbackQuery):
    employees = session.query(Questionnaire).filter(Questionnaire.status == 'employee').all()
    i = employees[int(call.data.split("_")[-1]) - 1]

    back_to_get_questionnaire_list_inline_keyboard = types.InlineKeyboardMarkup()
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="🌕 Удалить анкету сотрудника",
                                   callback_data="employee_delete_to_employee"), )

    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️ Назад", callback_data="get_specifically_employee_questionnaire"))

    # Если есть анкеты в избранном, формируем текст для вывода
    text = "<b>Анкеты сотрудников:</b>\n\n"
    for employee in [i]:
        text += (f"🔹<b>ID:</b> {employee.id}\n\n"
                 f"👤 {employee.first_name} {employee.last_name}\n\n"
                 f"🎯 <b>Желаемая_должность:</b> {employee.title}\n\n"
                 f"👨‍🏫 <b>Предыдущая_должность:</b> {employee.position}\n\n"
                 f"📅 <b>Опыт_работы:</b> {employee.total_experience}\n\n"
                 f"💰 <b>Требуемая_ЗП:</b> {employee.amount} {employee.currency}\n\n"
                 f"👴 <b>Возраст:</b> {employee.age}\n\n"
                 f"🏙️ <b>Город_проживания:</b> {employee.area}\n\n"
                 f"📜 <b>Сертификаты:</b> {employee.certificate}\n\n"
                 f"🎓 <b>Образование:</b> {employee.level}\n\n"
                 )
        text += "\n"
    await call.message.edit_text(text, reply_markup=back_to_get_questionnaire_list_inline_keyboard)


@dp.callback_query_handler(text="employee_delete_to_employee")
async def employee_delete_from_employee(call: types.CallbackQuery):
    questionnaire_id = int(call.message.text.split('\n\n')[1].split('\n')[0].split(': ')[1])
    session.execute(update(Questionnaire).where(Questionnaire.id == questionnaire_id).values(status=''))
    session.commit()

    back_to_get_questionnaire_list_inline_keyboard = types.InlineKeyboardMarkup()
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="Добавить в анкеты сотрудников",
                                   callback_data="employee_add_to_employee"), )
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️Назад", callback_data="get_specifically_employee_questionnaire"))

    # Отправка обновленного текста сообщения с кнопками и подтверждением удаления из избранного
    await call.message.edit_text(call.message.text, reply_markup=back_to_get_questionnaire_list_inline_keyboard)


@dp.callback_query_handler(text="employee_add_to_employee")
async def employment_add_to_employment(call: types.CallbackQuery):
    questionnaire_id = call.message.text.split("\n\n")[1].split(": ")[1]
    session.execute(update(Questionnaire).where(Questionnaire.id == questionnaire_id).values(status='employee'))
    session.commit()

    back_to_get_questionnaire_list_inline_keyboard = types.InlineKeyboardMarkup()
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="Удалить из анкет сотрудников",
                                   callback_data="employee_delete_to_employee"), )
    back_to_get_questionnaire_list_inline_keyboard.add(
        types.InlineKeyboardButton(text="⬅️Назад", callback_data="get_specifically_employee_questionnaire"))

    await call.message.edit_text(call.message.text, reply_markup=back_to_get_questionnaire_list_inline_keyboard)


@dp.callback_query_handler(text="back_to_get_employee_questionnaire_list_menu")
async def employment_back_to_get_employment_questionnaire_list_menu(call: types.CallbackQuery):
    employees = session.query(Questionnaire).filter(Questionnaire.status == 'employee').all()

    if employees:
        questionnaires_settings_inline_keyboard = types.InlineKeyboardMarkup(row_width=2)

        row2_button = [
            types.InlineKeyboardButton(text="📤Выгрузить все из анкет сотрудников",
                                       callback_data="get_all_employee_questionnaires")]
        row3_button = [types.InlineKeyboardButton(text="🔎Получить данные про конкретную анкету",
                                                  callback_data="get_specifically_employee_questionnaire"), ]
        row4_button = [types.InlineKeyboardButton(text="⤴️Главное меню", callback_data="back_main_menu")]

        questionnaires_settings_inline_keyboard.row(*row2_button)
        questionnaires_settings_inline_keyboard.row(*row3_button)
        questionnaires_settings_inline_keyboard.row(*row4_button)

        text = ''
        for employee in employees:
            text += (f"🔹<b>ID:</b> {employee.id}\n"
                     f"👤 {employee.first_name} {employee.last_name}\n"
                     f"🎯 <b>Желаемая_должность:</b> {employee.title}\n"
                     f"👨‍🏫 <b>Предыдущая_должность:</b> {employee.position}\n"
                     f"📅 <b>Опыт_работы:</b> {employee.total_experience}\n\n")

        await call.message.edit_text(f'<b>Анкеты сотрудников:</b>\n\n'
                                     f'{text}', reply_markup=questionnaires_settings_inline_keyboard)
    else:
        text = "У вас пока нет анкет на трудоустройстве."
        await call.message.edit_text(text)
