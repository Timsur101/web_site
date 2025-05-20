# Веб-приложение для управления рецептами

## Описание
Flask-приложение для работы с кулинарными рецептами, включая авторизацию пользователей и систему избранного.

## Установка
1. Клонировать репозиторий:
   ```bash
   git clone https://github.com/Timsur101/web_site.git
   cd web_site
2. Создать и активировать виртуальное окружение:


python -m venv venv
# Для Windows:
venv\Scripts\activate
# Для Linux/Mac:
source venv/bin/activate

3. Установить зависимости:


pip install -r requirements.txt

4. Настроить базу данных:

- Запустить MySQL

- Выполнить скрипт create.sql для создания структуры БД

- (Опционально) Добавить тестовые данные из example.sql

5. Запустить приложение:

python app.py

Технические детали:
- Зависимости (см. requirements.txt):

Flask==3.0.3

mysql-connector-python==8.4.0

Werkzeug==3.0.3

- База данных (см. create.sql):

Таблицы: users, recipes, favorites

Связи: внешние ключи между таблицами

Тестовые данные (example.sql)


INSERT INTO users (username, email, password) VALUES ('test', 'example1@mail.ru', 'qwerty123');
INSERT INTO users (username, email, password, role) VALUES ('admin', 'admin@mail.ru', 'qwerty123', 'admin');
Доступные функции
Регистрация (/register)

- Авторизация (/login)

- Просмотр рецептов (/)

- Добавление рецептов (/add)

- Избранное (/favorites)

- Профиль (/profile)

- Выход (/logout)
