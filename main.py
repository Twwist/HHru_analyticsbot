from interface.database.create_db import create_db
from aiogram import executor
from main_bot import dp


async def main(dp) -> None:
    await create_db()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=main, skip_updates=True)
