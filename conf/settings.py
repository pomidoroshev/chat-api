"""
App settings
"""
from defaultenv import ENV

DEBUG = bool(int(ENV.DEBUG or 0))
PORT = int(ENV.PORT or 8080)

DATABASE = {
    'host': ENV.DB_HOST,
    'port': ENV.DB_PORT,
    'dbname': ENV.DB_NAME,
    'user': ENV.DB_USER,
    'password': ENV.DB_PASSWORD,
}
