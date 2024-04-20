from flask import Flask, render_template, request
from model import Row
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import asyncio
import aiomysql

app = Flask(__name__)

async def get_vacancies():
    async with aiomysql.create_pool(
            host='mysql.5f3ead315b5.hosting.myjino.ru',
            port=3306,
            user='j73867464_new',
            password='bog789064',
            db='j73867464_new',
            autocommit=True) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("SELECT * FROM employees")
                rows = await cur.fetchall()
                filtered_vacancies = [dict(row) for row in rows]
    return filtered_vacancies

@app.route('/add_to_favorites/<int:vacancy_id>', methods=['POST'])
async def add_to_favorites(vacancy_id):
    async with aiomysql.create_pool(
            host='mysql.5f3ead315b5.hosting.myjino.ru',
            port=3306,
            user='j73867464_new',
            password='bog789064',
            db='j73867464_new',
            autocommit=True) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("UPDATE employees SET favourites = 1 WHERE id = %s", (vacancy_id,))
    return {'message': 'Vacancy added to favorites'}

@app.route('/remove_from_favorites/<int:vacancy_id>', methods=['POST'])
async def remove_from_favorites(vacancy_id):
    async with aiomysql.create_pool(
            host='mysql.5f3ead315b5.hosting.myjino.ru',
            port=3306,
            user='j73867464_new',
            password='bog789064',
            db='j73867464_new',
            autocommit=True) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("UPDATE employees SET favourites = 0 WHERE id = %s", (vacancy_id,))
    return {'message': 'Vacancy removed from favorites'}

async def get_unique_values(key):
    vacancies = await get_vacancies()
    unique_values = set()
    for vacancy in vacancies:
        if key in vacancy:
            unique_values.add(vacancy[key])
    return list(unique_values)

# Функция для фильтрации данных
async def filter_results(filters):
    conn = await aiomysql.connect(host='mysql.5f3ead315b5.hosting.myjino.ru',
        port=3306,
        user='j73867464_new',
        password='bog789064',
        db='j73867464_new',
        autocommit=True)

    async with conn.cursor(aiomysql.DictCursor) as cursor:
        # Формируем базовый SQL-запрос
        sql_query = "SELECT * FROM employees WHERE "
        conditions = []

        # Формируем условия для фильтрации
        for key, value in filters.items():
            if value != '' and value:
                conditions.append(f"{key} = '{value}'")

        # Если нет ни одного условия, добавляем условие, которое всегда истинно
        if not conditions:
            conditions.append(" 1 = 1")

        # Добавляем условия к SQL-запросу
        sql_query += " AND ".join(conditions)
        print(sql_query)
        # Выполняем SQL-запрос
        await cursor.execute(sql_query)

        # Получаем результаты запроса
        result = await cursor.fetchall()

    # Закрываем соединение
    conn.close()

    return result



# Маршрут для главной страницы
@app.route('/')
async def index():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    all_position = await get_unique_values('position')  # Await the result
    all_area = await get_unique_values('area')  # Await the result
    amount_ranges = ["0-50000", "50001-100000", "100001-150000", "150001-200000", "200001-250000", "250001-300000"]
    filters = {
        "position": request.args.get('position', ''),
        "area": request.args.get('area', ''),
        "amount": request.args.get('amount', '')
    }
    print(filters)
    filtered_vacancies = await filter_results(filters)
    total_pages = (len(filtered_vacancies) - 1) // per_page + 1
    vacancies_page = filtered_vacancies[(page - 1) * per_page:page * per_page]
    return render_template('index.html', vacancies=vacancies_page, filters=filters, total_pages=total_pages, page=page, all_position=all_position, all_area=all_area, amount_ranges=amount_ranges)

# Маршрут для отображения подробной информации о вакансии
@app.route('/vacancy/<int:vacancy_id>')
async def vacancy_detail(vacancy_id):
    vacancies = await get_vacancies()
    vacancy = next((v for v in vacancies if v['id'] == vacancy_id), None)
    if not vacancy:
        return "Vacancy not found", 404
    return render_template('vacancy_detail.html', vacancy=vacancy)

if __name__ == '__main__':
    app.run(debug=True)
