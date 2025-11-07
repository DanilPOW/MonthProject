# Примеры использования API

## 1. Регистрация пользователя

```bash
POST /register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "user123",
  "password": "securepassword123"
}
```

## 2. Вход и получение токена

```bash
POST /token
Content-Type: application/x-www-form-urlencoded

username=user123&password=securepassword123
```

Ответ:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 3. Получение списка треков

```bash
GET /tracks
Authorization: Bearer YOUR_TOKEN
```

## 4. Запись на трек

```bash
POST /tracks/1/enroll
Authorization: Bearer YOUR_TOKEN
```

## 5. Получение текущего задания

```bash
GET /tracks/1/assignments/current
Authorization: Bearer YOUR_TOKEN
```

## 6. Отправка решения на задание

```bash
POST /assignments/1/submit
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "repository_url": "https://github.com/user/repo"
}
```

## 7. Получение submission для код-ривью

```bash
GET /assignments/1/review/submission
Authorization: Bearer YOUR_TOKEN
```

## 8. Создание код-ривью

```bash
POST /submissions/1/review
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "criteria_scores": {
    "code_quality": 4.5,
    "documentation": 4.0,
    "tests": 3.5,
    "architecture": 4.0
  },
  "comment": "Хорошая работа! Есть несколько моментов для улучшения."
}
```

## 9. Создание записи в дневнике

```bash
POST /assignments/1/diary
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "content": "Возник вопрос по поводу использования декораторов. Можете помочь?"
}
```

## 10. Получение записей дневника

```bash
GET /assignments/1/diary
Authorization: Bearer YOUR_TOKEN
```




