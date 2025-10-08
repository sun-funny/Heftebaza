from sqlalchemy import Column, Integer, String, Numeric, Text, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base

# Создание основного класса
Base = declarative_base()

class Plan(Base):
    __tablename__ = 'tab_plan_oss_nb'
    __table_args__ = {'schema': 'public'}

    # Поля описываются точно как в QUERY:
    id = Column(Integer, primary_key=True)
    date = Column(Integer)  # Дата
    tab_bazis_bk_ids = Column(Integer)  # Ключ к Заводам
    tab_product_nb_ids = Column(Integer)  # Ключ к Продуктам
    tab_station_nb_ids = Column(Integer)  # Ключ к Станциям
    value = Column(Numeric)  # Объем

class Product(Base):
    __tablename__ = 'tab_product_nb_ids'
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)

class Station(Base):
    __tablename__ = 'tab_station_nb_ids'
    __table_args__ = {'schema': 'public'}
    id = Column(Text, primary_key=True)
    name = Column(Text, unique=True)
    tab_fo_d314_ids = Column(Integer)  # Ключ к ФО
    tab_region_d314_ids = Column(Integer)  # Ключ к Регионам
    geo = Column(Text, unique=True)

class Bazis(Base):
    __tablename__ = 'tab_bazis_bk'
    __table_args__ = {'schema': 'public'}
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    tab_proizv_bk_ids = Column(Integer)  # Ключ к Агент/Производитель

# Определить эталонные модели и их атрибуты. Поля можно задать без _ids
reference_models = {
    'tab_product_nb': Product,
    'tab_station_nb': Station,
    'tab_bazis_bk': Bazis
}

