from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from config import Config

# Создание движка SQLAlchemy
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, pool_size=30)
db = scoped_session(sessionmaker(bind=engine))

from flask_caching import Cache

cache = Cache()

def errorhandler(e):
    # Check for specific error messages
    if str(e) == "max() arg - это пустая последовательность":
        return 502, "Нет данных для указанных условий"
    elif isinstance(e, ValueError):
        return 501, f"Неверный ввод: {str(e)}"
    elif isinstance(e, KeyError):
        return 504, f"Ключ не найден: {str(e)}"
    elif isinstance(e, PermissionError):
        return 503, f"Доступ запрещен: {str(e)}"
    # You can add more specific exception types as needed
    else:
        # Default error message for unhandled exceptions
        return 500, f"Произошла непредвиденная ошибка: {str(e)}"