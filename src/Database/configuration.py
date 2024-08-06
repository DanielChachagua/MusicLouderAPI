from peewee import *
import MySQLdb
from decouple import config

db = MySQLDatabase(
    config('DB_NAME'),
    host=config('DB_HOST'),
    user=config('DB_USER'),
    passwd=config('DB_PASSWORD'),
    port=int(config('DB_PORT'))
)