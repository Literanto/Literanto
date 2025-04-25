from dbCommands.dbConnect import get_db_connection
import logging
import secrets
import psycopg2
from datetime import datetime, timedelta

def generate_token():
    return secrets.token_hex(16)

def insert_user(username, email, hashed_password):
    if not username or not email or not hashed_password:
        logging.error("Parâmetros inválidos para insert_user")
        return False, "Parâmetros inválidos"

    conn = get_db_connection()
    if not conn:
        return False, "Erro ao conectar ao banco de dados"

    token = generate_token()
    token_expiration = datetime.now() + timedelta(days=1)

    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO users (user_name, user_email, user_password, user_token, token_expiration)
            VALUES (%s, %s, %s, NULL, NULL)""",
            (username, email, hashed_password)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True, "Usuário registrado com sucesso!"

    except psycopg2.IntegrityError:
        logging.error(f"Usuário '{username}' já existe.")
        return False, "Usuário já existe"

    except Exception as e:
        logging.error(f"Erro inesperado ao inserir usuário '{username}': {e}")
        return False, "Erro inesperado"

def get_user_by_email(email):
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT user_code, user_name, user_email, user_password, user_token, token_expiration FROM users WHERE user_email = %s",
            (email,)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            return {
                "user_code": user[0],
                "user_name": user[1],
                "user_email": user[2],
                "user_password": user[3],
                "user_token": user[4],
                "token_expiration": user[5]
            }
        return None

    except Exception as e:
        logging.error(f"Erro ao buscar usuário: {e}")
        return None