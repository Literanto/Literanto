import psycopg2
import logging

DB_CONFIG = {
    "dbname": "railway",
    "user": "postgres",
    "password": "iJvZTKKFCCvqaKTGjTUJGCOQIUkWjpmQ",
    "host": "metro.proxy.rlwy.net",
    "port": "58627"
}

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        return None