import sys
import os
sys.path.insert(0,'opt/foresight')
# Импорт стандартной библиотеки
import logging  # Ведение журнала для отладки и мониторинга
# Импорт Flask
from flask import Flask, jsonify, request  # Основные классы и функции Flask
# Импорт SQLAlchemy
from sqlalchemy import select, distinct, not_, literal, func, and_  # Основные функции SQLAlchemy
from werkzeug.exceptions import HTTPException, InternalServerError
# Импорты для конкретного проекта
from NB_back.models.db_models import Base, Plan, reference_models  # Модели баз данных
from NB_back.config import Config, changelog, secret_key  # Конфигурация и список изменений
from NB_back.namespace.ns_plan_loader import ns_plan_loader
# Импорт сеанса работы с базой данных
from NB_back.database import db, engine, cache
# Импорт Flask-Restx
from flask_restx import Api, Resource, Namespace  # Классы Flask-Restx для создания API

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = secret_key

# Настройка API Flask-Restx
api = Api(app,
          version='1.1',
          title='Нефтебазы API',
          description=f'API configuration for the Neftebaza project\n\n{changelog}'
          )

cache.init_app(app)

# Создание таблиц базы данных
with app.app_context():
    Base.metadata.create_all(bind=engine)

# Настройка ведения журнала
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Добавить namespace в API
api.add_namespace(ns_plan_loader, path='/api/nb')

if __name__ == '__main__':
    app.run(debug=True)