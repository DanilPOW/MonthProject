# Learning Platform - Веб-сервис для совместного обучения программированию

Минимальное API на FastAPI и React фронтенд для веб-сервиса совместного обучения.

## Структура проекта

```
api/
├── backend/          # FastAPI приложение
│   ├── main.py      # Основной файл API
│   ├── models.py    # SQLAlchemy модели
│   ├── schemas.py   # Pydantic схемы
│   ├── database.py  # Настройка БД
│   ├── auth.py      # Аутентификация JWT
│   └── requirements.txt
└── frontend/        # React приложение
    ├── src/
    │   ├── App.jsx
    │   ├── api.js
    │   └── components/
    └── package.json
```

## Установка и запуск

### Backend

1. Перейдите в папку backend:
```bash
cd backend
```

2. Создайте виртуальное окружение (рекомендуется):
```bash
python -m venv venv
```

3. Активируйте виртуальное окружение:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Установите зависимости:
```bash
pip install -r requirements.txt
```

5. Запустите сервер:
```bash
uvicorn main:app --reload
```

Backend будет доступен по адресу: http://localhost:8000

API документация: http://localhost:8000/docs

### Frontend

1. Откройте новый терминал и перейдите в папку frontend:
```bash
cd frontend
```

2. Установите зависимости:
```bash
npm install
```

3. Запустите dev сервер:
```bash
npm run dev
```

Frontend будет доступен по адресу: http://localhost:5173

## Проверка работы

### 1. Регистрация и вход

1. Откройте http://localhost:5173
2. Зарегистрируйтесь (email и пароль)
3. Войдите в систему

### 2. Создание трека (через API)

Для создания трека используйте Swagger UI (http://localhost:8000/docs) или curl:

```bash
# Сначала получите токен
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your@email.com&password=yourpassword"

# Создайте трек (замените YOUR_TOKEN)
curl -X POST "http://localhost:8000/tracks" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Basics",
    "description": "Learn Python programming",
    "quota": 3,
    "criteria": "Code quality, tests, documentation",
    "assignments": [
      {
        "title": "Task 1",
        "description": "Create a calculator",
        "deadline_days": 7,
        "order": 1
      },
      {
        "title": "Task 2",
        "description": "Build a REST API",
        "deadline_days": 10,
        "order": 2
      }
    ]
  }'
```

### 3. Тестирование функционала

1. **Просмотр треков**: После входа вы увидите список треков
2. **Запись на трек**: Нажмите "Join" на треке
3. **Начало трека**: Когда наберется нужное количество участников, трек автоматически начнется
4. **Выполнение заданий**: 
   - Откройте трек
   - Выберите задание
   - Отправьте ссылку на репозиторий
5. **Код-ривью**: После дедлайна нажмите "Start Code Review" и оцените работу
6. **Дневник**: Добавляйте комментарии под заданиями

### 4. Проверка уведомлений

Уведомления обновляются каждую минуту. Они появляются:
- За 2 дня до дедлайна
- Когда начинается этап код-ривью

## Основные эндпоинты API

- `POST /register` - Регистрация
- `POST /token` - Получение JWT токена
- `GET /tracks` - Список треков
- `POST /tracks` - Создание трека
- `POST /tracks/{id}/join` - Запись на трек
- `POST /tracks/{id}/leave` - Выход с трека
- `GET /tracks/{id}/assignments` - Задания трека
- `POST /assignments/{id}/submit` - Отправка решения
- `GET /assignments/{id}/review` - Получить работу для ревью
- `POST /submissions/{id}/review` - Отправить ревью
- `GET /assignments/{id}/comments` - Комментарии к заданию
- `POST /assignments/{id}/comments` - Добавить комментарий
- `GET /notifications` - Уведомления

## База данных

Используется SQLite (файл `backend/app.db`). База создается автоматически при первом запуске.

## Примечания

- Для продакшена измените `SECRET_KEY` в `backend/auth.py`
- Уведомления работают через polling (каждую минуту)
- Критерии оценки задаются при создании трека в поле `criteria`
- Дедлайны настраиваются в днях при создании заданий

