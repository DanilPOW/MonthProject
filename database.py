from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost/learning_platform"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
SQLALCHEMY_DATABASE_URL = settings.database_url

# Добавляем pool_pre_ping для автоматической проверки соединения
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Проверяет соединение перед использованием
    echo=False  # Установите True для отладки SQL запросов
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

