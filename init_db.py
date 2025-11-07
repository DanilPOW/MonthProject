"""
Скрипт для инициализации базы данных с тестовыми данными
"""
from database import SessionLocal, engine, Base
from models import User, Track, Assignment, TrackEnrollment
from auth import get_password_hash
from datetime import datetime

# Создаем таблицы
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Создаем тестового пользователя
    test_user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpass123")
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    print(f"Создан пользователь: {test_user.username}")

    # Создаем тестовый трек
    test_track = Track(
        title="Python Basics",
        description="Изучение основ Python",
        required_participants=3,
        status="waiting"
    )
    db.add(test_track)
    db.commit()
    db.refresh(test_track)
    print(f"Создан трек: {test_track.title}")

    # Создаем задания для трека
    assignments_data = [
        {
            "title": "Задание 1: Hello World",
            "description": "Создайте программу, которая выводит 'Hello, World!'",
            "order": 1,
            "deadline_hours": 24
        },
        {
            "title": "Задание 2: Калькулятор",
            "description": "Создайте простой калькулятор с операциями +, -, *, /",
            "order": 2,
            "deadline_hours": 48
        },
        {
            "title": "Задание 3: Список задач",
            "description": "Создайте приложение для управления списком задач",
            "order": 3,
            "deadline_hours": 72
        }
    ]

    for assignment_data in assignments_data:
        assignment = Assignment(
            track_id=test_track.id,
            **assignment_data
        )
        db.add(assignment)
        print(f"Создано задание: {assignment.title}")

    db.commit()
    print("\nБаза данных инициализирована успешно!")

except Exception as e:
    print(f"Ошибка при инициализации: {e}")
    db.rollback()
finally:
    db.close()




