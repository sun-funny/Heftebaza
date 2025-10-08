class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5433/NB'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    CACHE_TYPE = 'simple'  # You can choose other types like 'redis', 'memcached', etc.
    CACHE_DEFAULT_TIMEOUT = 300  # Cache timeout in seconds
    UPLOAD_FOLDER = '/opt/foresight/cabinet_back/uploads'
    ALLOWED_EXTENSIONS = {'xlsx'}

secret_key = 'supersecretkey'

format_strings = ["0.0f", "0.1f", "0.2f", "0.3f", "0.4f"]


# Changelog
changelog = """
# Changelog

## Version 1.1
- updated /02/srr_volume_pie to srr_pie with argument to chose spending or volume
- data on spending and volumes updated from 2018 to 2024. Resources stll only for 2020
- for ns all added sorting of results and global_filter arg for /get_specific_filter to get relevenat data for specific conditions. for example for calyear=2024

"""