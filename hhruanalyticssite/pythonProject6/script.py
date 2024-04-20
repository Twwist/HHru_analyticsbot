from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import asyncio
import aiohttp
import sqlalchemy as db
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from model import Row

Base = declarative_base()

# Database connection
def send_email(subject, message):
    from_email = "ambity-bot@yandex.ru"
    to_email = "danilvasilev465@mail.ru"
    smtp_server = "smtp.yandex.ru"
    smtp_port = 587  # Порт SMTP сервера
    smtp_username = "ambity-bot"
    smtp_password = "fhpbdhvmtbkdxcpr"
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Добавляем текст письма
    msg.attach(MIMEText(message, 'html'))

    # Устанавливаем SMTP соединение
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Начинаем шифрованное соединение
    server.login(smtp_username, smtp_password)  # Логинимся на SMTP сервере

    # Отправляем письмо
    server.sendmail(from_email, to_email, msg.as_string())

    # Закрываем соединение
    server.quit()

# URL для запроса
engine = create_engine('mysql://j73867464_new:bog789064@mysql.5f3ead315b5.hosting.myjino.ru/j73867464_new')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


# Запись данных в базу данных
async def save_to_database(Data):
    clear = db.delete(Row)
    session.execute(clear)
    for data in Data:
        new = Row(
                age=data.get('age'),
                area=data.get('area'),
                certificate=data.get("certificate"),
                level=data["education"].get("level"),
                primary_name=data["education"].get("primary_name"),
                primary_organization=data["education"].get("primary_organization"),
                primary_result=data["education"].get("primary_result"),
                primary_year=data["education"].get("primary_year"),
                company=data["experience"].get("company"),
                start=data["experience"].get("start"),
                end=data["experience"].get("end"),
                industry=data["experience"].get("industry"),
                position=data["experience"].get("position"),
                first_name=data.get("first_name"),
                gender=data.get("gender"),
                last_name=data.get("last_name"),
                middle_name=data.get("middle_name"),
                resume=data.get("resume"),
                amount=data["salary"].get("amount"),
                currency=data["salary"].get("currency"),
                title=data.get("title"),
                total_experience=data.get("total_experience"),
                phone=data.get("phone"),
                email=data.get("email"),
                created_at=data.get("created_at"),
                updated_at=data.get("updated_at"),
                favourites=0
        )
        last = session.query(Row).filter(
            Row.age == new.age,
            Row.first_name == new.first_name,
            Row.last_name == new.last_name
        ).first()
        if last == None:
            session.add(new)
        else:
            favourite_or_no = last.favourite
            last.favourite = 0
            if last != new and favourite_or_no:
                subject = 'Изменение в избранном резюме.'
                text = f'<html><body style="font-family: Arial, sans-serif;">' \
                       f'<p style="font-size: 16px;">{last.first_name} {last.last_name} обновил(а) своё резюме.</p>' \
                       f'<div style="margin-left: 20px;">' \
                       f'<p style="font-size: 14px; margin-bottom: 8px;"><strong>Контактные данные:</strong></p>' \
                       f'<p style="font-size: 14px; margin-bottom: 4px;">Email: {new.email}</p>' \
                       f'<p style="font-size: 14px; margin-bottom: 4px;">Телефон: {new.phone}</p>' \
                       f'</div></body></html>'
                send_email(subject, text)
            new.favourites = favourite_or_no
        session.add(new)
        session.commit()
        session.close()

async def fetch_data_from_api():
    headers = {
        'Api-key': 'Bxq7HZmXVDHVUW1d2X0J'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get('http://a0814722.xsph.ru/api/resume', headers=headers) as response:
            data = await response.json()
            return data


async def process_data():
    data = await fetch_data_from_api()
    await save_to_database(data)


async def main():
    while True:
        await process_data()
        await asyncio.sleep(60)

asyncio.run(main())
