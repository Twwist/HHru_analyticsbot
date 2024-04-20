import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, message):
    # Пример использования функции send_email

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

subject = 'Изменение в избранном резюме.'
text = f'<html><body style="font-family: Arial, sans-serif;">' \
                f'<p style="font-size: 16px;">Васильев Данил обновил(а) своё резюме.</p>' \
                       f'<div style="margin-left: 20px;">' \
                       f'<p style="font-size: 14px; margin-bottom: 8px;"><strong>Контактные данные:</strong></p>' \
                       f'<p style="font-size: 14px; margin-bottom: 4px;">Email: почта</p>' \
                       f'<p style="font-size: 14px; margin-bottom: 4px;">Телефон: 89677394429</p>' \
                       f'</div></body></html>'
send_email(subject, text)