import os
import pandas as pd
from datetime import date, datetime
from sqlalchemy import create_engine, text
import logging
import psycopg2
from flask_restx import Namespace, Resource, reqparse
from flask import jsonify, session, request, send_from_directory, send_file
from werkzeug.datastructures import FileStorage
from NB_back.database import db, cache, errorhandler, engine as global_engine
from NB_back.functions.query_functions import mapping_query, year_query
from NB_back.models.db_models import reference_models, Plan, Station, Product, Bazis

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ns_plan_loader = Namespace('Neftebaza', description='Нефтебаза')

# Парсер для загрузки файла
upload_parser = reqparse.RequestParser()
upload_parser.add_argument('file',
                           location='files',
                           type=FileStorage,
                           required=True,
                           help='Excel файл')
upload_parser.add_argument('year',
                           type=int,
                           required=True,
                           help='Год')
upload_parser.add_argument('month',
                           type=int,
                           required=True,
                           help='Месяц')
upload_parser.add_argument('bazis',
                           type=int,
                           required=True,
                           help='id базиса')
upload_parser.add_argument('product',
                           type=int,
                           required=True,
                           help='id продукта')

"""Количество дней в месяце"""
def get_days_in_month(year, month):
    """Количество дней в месяце"""
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    last_day = next_month - pd.Timedelta(days=1)
    return last_day.day

"""Мэппинги справочников"""
def mapping(model_class):
    try:
        base_query = db.session.query(model_class)
        query = mapping_query(base_query, model_class)

        result = {}
        for row in query:
            result[row.name] = row.id
        return result
    except Exception as e:
        logger.error(f"Ошибка при мэппинге {model_class}: {e}")
        return {}

"""Получение id Станции"""
def get_station_ids(station_names, engine):
    try:
        if not station_names:
            return {}

        query = text("SELECT id, name FROM public.tab_station_nb WHERE name IN :names")

        with engine.connect() as conn:
            result = conn.execute(query, {"names": tuple(station_names)}).mappings().all()
            station_mapping = {row['name']: row['id'] for row in result}

        return station_mapping
    except Exception as e:
        logger.error(f"Ошибка при получении ID станций: {e}")
        raise

@ns_plan_loader.route('/upload_plan')
class PlanUpload(Resource):
    @ns_plan_loader.expect(upload_parser)
    def post(self):
        """Загрузка плана из Excel файла"""
        try:
            # Получение параметров и файла
            args = upload_parser.parse_args()
            file = args['file']
            year = args['year']
            month = args['month']
            bazis_id = args['bazis']
            product_id = args['product']

            logger.info(
                f"Обработка файла: {file.filename} для {month}.{year}, базис: {bazis_id}, продукт: {product_id}")

            # Сохраняем файл временно
            temp_dir = "temp_uploads"
            os.makedirs(temp_dir, exist_ok=True)
            file_path = os.path.join(temp_dir, file.filename)
            file.save(file_path)

            try:
                # Чтение Excel файла
                logger.info(f"Чтение файла: {file_path}")
                df = pd.read_excel(file_path, header=4)  # Данные с 5 строки

                # Проверка наличия необходимых столбцов
                if df.shape[1] < 2:
                    raise ValueError("Файл должен содержать минимум 2 столбца")

                # Получение количества дней в месяце
                days_in_month = get_days_in_month(year, month)
                logger.info(f"Месяц {month}.{year} содержит {days_in_month} дней")

                # Проверка соответствия количества столбцов
                if df.shape[1] < days_in_month + 2:  # +2 для станции и "Заявлено Итого"
                    raise ValueError(
                        f"Недостаточно столбцов в файле. Ожидается: {days_in_month + 2}, найдено: {df.shape[1]}")

                # Получение списка станций (первый столбец)
                station_names = df.iloc[:, 0].dropna().astype(str).unique().tolist()
                logger.info(f"Найдено станций: {len(station_names)}")

                # Получение соответствия имен станций и их ID
                engine = global_engine
                station_mapping = get_station_ids(station_names, engine)
                logger.info(f"Получено id для {len(station_mapping)} станций")

                # Проверка наличия всех станций в справочнике
                missing_stations = set(station_names) - set(station_mapping.keys())
                if missing_stations:
                    logger.warning(f"Не найдены id для станций: {missing_stations}")

                # Подготовка данных для вставки
                data_to_insert = []

                for index, row in df.iterrows():
                    station_name = str(row.iloc[0]) if pd.notna(row.iloc[0]) else None

                    # Пропускаем пустые строки
                    if not station_name:
                        continue

                    # Получаем ID станции
                    station_id = station_mapping.get(station_name)
                    if not station_id:
                        logger.warning(f"Пропущена станция '{station_name}' - не найден id")
                        continue

                    # Обрабатываем данные по дням месяца
                    for day in range(1, days_in_month + 1):
                        # Столбец для дня = 1 + day (0-станция, 1-заявлено итого, 2-1й день и т.д.)
                        col_index = 1 + day

                        if col_index < len(row):
                            value = row.iloc[col_index]

                            # Пропускаем пустые значения
                            if pd.isna(value):
                                continue

                            # Формируем дату
                            try:
                                record_date = date(year, month, day)
                            except ValueError as e:
                                logger.warning(f"Некорректная дата {day}.{month}.{year}: {e}")
                                continue

                            # Добавляем запись
                            data_to_insert.append({
                                'tab_bazis_bk_ids': bazis_id,
                                'tab_product_nb_ids': product_id,
                                'tab_station_nb_ids': station_id,
                                'date': record_date,
                                'value': float(value) if pd.notna(value) else None
                            })

                logger.info(f"Всего {len(data_to_insert)} записей для вставки")

                # Вставка данных в БД
                if data_to_insert:
                    try:
                        # Создаем DataFrame для вставки
                        df_to_insert = pd.DataFrame(data_to_insert)

                        # Вставляем данные
                        df_to_insert.to_sql(
                            'tab_plan_oss_nb',
                            engine,
                            schema='public',
                            if_exists='append',
                            index=False,
                            method='multi'
                        )
                        logger.info(f"Успешно загружено {len(data_to_insert)} записей в БД")

                        return {
                            'message': f'Успешно загружено {len(data_to_insert)} записей',
                            'stations_processed': len(station_mapping),
                            'missing_stations': list(missing_stations),
                            'file': file.filename
                        }, 200

                    except Exception as e:
                        logger.error(f"Ошибка при вставке данных в БД: {e}")
                        return {'error': f'Ошибка при загрузке данных: {str(e)}'}, 500
                else:
                    logger.warning("Нет данных для загрузки")
                    return {'error': 'Нет данных для загрузки'}, 400

            finally:
                # Удаляем временный файл
                if os.path.exists(file_path):
                    os.remove(file_path)

        except Exception as e:
            logger.error(f"Общая ошибка: {e}")
            return {'error': f'Внутренняя ошибка сервера: {str(e)}'}, 500


@ns_plan_loader.route('/get_references')
class References(Resource):
    def get(self):
        try:
            engine = global_engine

            bazis_mapping = mapping(Bazis)
            product_mapping = mapping(Product)

            station_query = text("SELECT id, name FROM public.tab_station_nb ORDER BY name")
            with engine.connect() as conn:
                result = conn.execute(station_query).mappings().all()
                stations = [{'id': row['id'], 'name': row['name']} for row in result]

            return {
                'bazis': [{'id': k, 'name': v} for k, v in bazis_mapping.items()],
                'products': [{'id': k, 'name': v} for k, v in product_mapping.items()],
                'stations': stations
            }, 200

        except Exception as e:
            logger.error(f"Ошибка при получении справочников: {e}")
            return {'error': f'Ошибка при получении справочников: {str(e)}'}, 500