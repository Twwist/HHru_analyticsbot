from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = create_engine('mysql://j73867464_new:bog789064@mysql.5f3ead315b5.hosting.myjino.ru/j73867464_new')
Session = sessionmaker(bind=engine)
session = Session()