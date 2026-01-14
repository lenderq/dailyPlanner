# Daily Planner

## Описание проекта
    
Daily Planner — полнофункциональное веб-приложение для ежедневного планирования. Пользователи регистрируются, добавляют события с датой, временем, цветовой маркировкой и напоминаниями (поддержка таймзон Moscow/UTC). Интеграция FullCalendar для интерактивного календаря, REST API для JSON-данных, PostgreSQL для хранения.

## Ключевые возможности

- Полная аутентификация и регистрация с хэшированием паролей (Flask-Login)
- CRUD-операции для событий: создание, редактирование, удаление, просмотр списков
- Система напоминаний с проверкой каждые 30 секунд и статусом "просмотрено"
- Адаптивный календарь с цветовой кодировкой событий и поддержкой allDay-событий
- REST API эндпоинты для событий и напоминаний (JSON-формат)


## Технологический стек

| Компонент | Технологии |
| :-- | :-- |
| Backend | Flask 3.1, SQLAlchemy, WTForms, Flask-Login |
| База данных | PostgreSQL (psycopg2-binary), модели User/Event |
| Frontend | Jinja2, FullCalendar 6.1.8, Vanilla JS |
| Зависимости | Полный список в `requirements.txt` |

## Установка и запуск

1. **Клонирование репозитория**:

```
git clone https://github.com/lenderq/dailyPlanner.git
cd dailyPlanner
```

2. **Установка зависимостей**:

```
pip install -r requirements.txt
```

3. **Настройка базы данных PostgreSQL**:
    - Создайте базу данных `dailyplannerdb`
    - Обновите `config.py`: `SECRET_KEY`, `SQLALCHEMY_DATABASE_URI`
4. **Инициализация и запуск**:

```
python run.py
```

5. **Доступ к приложению**:
Откройте `http://127.0.0.1:5000` в браузере

## Структура проекта

```
dailyPlanner/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── forms.py
│   ├── routes.py
│   ├── config.py
│   └── templates/
├── static/
├── requirements.txt
└── run.py
```


## API эндпоинты

- `GET /api/events?start=...&end=...` — события для календаря
- `GET /api/reminders` — активные напоминания
- `POST /api/reminders/<event_id>/seen` — отметить напоминание просмотренным

