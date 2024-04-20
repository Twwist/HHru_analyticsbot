from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from catboost import CatBoostRegressor
from sqlalchemy import update

from configs.bot_token import token
from configs.db_configs import session
from interface.database.create_db import Questionnaire

bot = Bot(token=token, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

loaded_model = CatBoostRegressor()
loaded_model.load_model('configs/catboost_model.bin')
feature_importances = loaded_model.get_feature_importance()


async def main_menu_message(message, message_text: str):
    '''
    Отправляет главное меню
    :param message: сообщение от пользователя
    :param message_text: текст сообщения
    '''
    main_teachers_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = ["📚Получить анкеты", "💼Сохранённые анкеты", "⚙️Настройки", "🛠Помощь"]
    main_teachers_menu.add(*buttons)
    await bot.send_message(message.from_user.id, message_text, reply_markup=main_teachers_menu)
