"""
Скрипт для проверки подключения к базе данных
"""
import sys
from database import engine, SQLALCHEMY_DATABASE_URL

def check_connection():
    """Проверяет подключение к базе данных"""
    print(f"Проверка подключения к: {SQLALCHEMY_DATABASE_URL.split('@')[1] if '@' in SQLALCHEMY_DATABASE_URL else 'базе данных'}")
    print("-" * 50)
    
    try:
        with engine.connect() as connection:
            print("✓ Подключение к базе данных успешно!")
            return True
    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")
        print("\nВозможные причины:")
        print("1. PostgreSQL не запущен")
        print("2. Неправильные данные в .env файле")
        print("3. База данных не создана")
        print("4. Неправильный пароль или пользователь")
        print("\nПроверьте файл .env и убедитесь, что:")
        print("- PostgreSQL запущен")
        print("- База данных создана: CREATE DATABASE learning_platform;")
        print("- Данные подключения правильные")
        return False

if __name__ == "__main__":
    success = check_connection()
    sys.exit(0 if success else 1)




