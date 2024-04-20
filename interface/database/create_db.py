import sqlite3

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import asyncio
import aiohttp
import sqlalchemy as db

Base = declarative_base()


class Questionnaire(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    age = Column(Integer)
    area = Column(String(255))
    certificate = Column(String(255))
    level = Column(String(255))
    primary_name = Column(String(255))
    primary_organization = Column(String(255))
    primary_result = Column(String(255))
    primary_year = Column(Integer)
    company = Column(String(255))
    start = Column(DateTime)
    end = Column(DateTime)
    industry = Column(String(255))
    position = Column(String(255))
    first_name = Column(String(255))
    gender = Column(String(255))
    last_name = Column(String(255))
    middle_name = Column(String(255))
    resume = Column(String(1000))
    amount = Column(Integer)
    currency = Column(String(255))
    title = Column(String(255))
    total_experience = Column(Integer)
    phone = Column(String(255))
    email = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    favourites = Column(Boolean)
    status = Column(String(255))


# Определение класса модели для таблицы users
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    first_name = Column(String(255))
    last_name = Column(String(255))


# Определение класса модели для таблицы filters
class Filter(Base):
    __tablename__ = 'filters'

    filter_id = Column(Integer, primary_key=True)
    filter_name = Column(String(255))
    filter_description = Column(String(255))
    filter_author_id = Column(Integer)


async def create_db():
    # URL для запроса
    engine = create_engine('mysql://j73867464_new:bog789064@mysql.5f3ead315b5.hosting.myjino.ru/j73867464_new')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Создание всех таблиц, определенных в SQLAlchemy, в удаленной базе данных MySQL
    Base.metadata.create_all(engine)

    # # Пример добавления данных в таблицу users
    # new_user = User(user_id=1, first_name='John', last_name='Doe')
    # session.add(new_user)
    # session.commit()

    # Добавления данных в таблицу filters
    new_filter = Filter(filter_name='default_filter', filter_description="Желаемая_должность Программист\n"
                                                                         "Предыдущая_должность Программист\n"
                                                                         "Опыт_работы 10\n"
                                                                         "Требуемая_ЗП 100000",
                        filter_author_id=1)
    session.add(new_filter)
    session.commit()
