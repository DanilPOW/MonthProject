# Learning Platform API

Веб-сайт для совместного обучения программированию на FastAPI.

## Возможности

- Регистрация и аутентификация пользователей (JWT)
- Управление треками обучения
- Запись на треки и выход из них (до начала трека)
- Автоматический запуск трека при достижении нужного количества участников
- Последовательное выполнение заданий с дедлайнами
- Уведомления о приближающемся дедлайне (80% времени) через WebSocket
- Этап код-ривью после дедлайна (каждый должен оценить 3 человек)
- Фиксированные критерии код-ривью, задаваемые при создании трека
- Дневник для комментариев под каждым заданием
- Отправка решений через ссылку на репозиторий

## Установка

1. Убедитесь, что у вас установлен Python 3.11 или 3.12:
```bash
python --version
```

2. Создайте виртуальное окружение (рекомендуется):
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` с настройками базы данных:
```
DATABASE_URL=postgresql://user:password@localhost:5432/learning_platform
```

5. Запустите сервер:
```bash
uvicorn app:app --reload
```

API будет доступен по адресу: `http://localhost:8000`

Документация API (Swagger): `http://localhost:8000/docs`

## Структура проекта

- `app.py` - главный файл с эндпоинтами FastAPI
- `models.py` - модели базы данных (SQLAlchemy)
- `schemas.py` - схемы Pydantic для валидации
- `database.py` - настройка подключения к БД (PostgreSQL)
- `auth.py` - аутентификация и авторизация (JWT)
- `services.py` - бизнес-логика
- `websocket_manager.py` - менеджер WebSocket соединений для уведомлений

## Основные эндпоинты

### Аутентификация
- `POST /register` - регистрация нового пользователя
- `POST /token` - получение JWT токена
- `GET /me` - информация о текущем пользователе

### Треки
- `GET /tracks` - список всех треков
- `GET /tracks/my` - треки текущего пользователя
- `GET /tracks/{track_id}` - информация о треке
- `POST /tracks/{track_id}/enroll` - записаться на трек
- `DELETE /tracks/{track_id}/enroll` - выйти из трека

### Задания
- `GET /tracks/{track_id}/assignments` - список заданий трека
- `GET /tracks/{track_id}/assignments/current` - текущее доступное задание
- `POST /assignments/{assignment_id}/submit` - отправить решение

### Код-ривью
- `GET /assignments/{assignment_id}/review/submission` - получить случайное submission для ревью
- `POST /submissions/{submission_id}/review` - создать код-ривью

### WebSocket
- `WS /ws/{token}` - подключение для получения уведомлений о дедлайнах

### Дневник
- `POST /assignments/{assignment_id}/diary` - создать запись в дневнике
- `GET /assignments/{assignment_id}/diary` - получить записи дневника

## База данных

Используется PostgreSQL. Настройки подключения задаются через переменную окружения `DATABASE_URL` в файле `.env`.

Пример `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/learning_platform
```

Таблицы создаются автоматически при первом запуске.

## Безопасность

⚠️ **Важно**: В продакшене обязательно измените `SECRET_KEY` в `auth.py` на безопасный случайный ключ!

## Примеры использования

### Регистрация
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "username": "user", "password": "password123"}'
```

### Вход
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user&password=password123"
```

### Получение списка треков (требует авторизации)
```bash
curl -X GET "http://localhost:8000/tracks" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Логика работы

1. **Регистрация**: Пользователь регистрируется с email, username и password
2. **Треки**: Пользователь может просматривать треки и записываться на них
3. **Запуск трека**: Трек автоматически запускается, когда набирается нужное количество участников
4. **Задания**: После запуска трека участники последовательно выполняют задания
5. **Дедлайн**: На каждое задание дается определенное количество часов
6. **Уведомление**: При 80% времени до дедлайна отправляется WebSocket уведомление
7. **Код-ривью**: После дедлайна начинается этап код-ривью, где каждый должен оценить 3 случайных участника по фиксированным критериям
8. **Следующее задание**: Доступ к следующему заданию открывается только после завершения всех 3 код-ривью

