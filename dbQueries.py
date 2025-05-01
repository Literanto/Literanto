from flask import request, jsonify, session
from dbConnect import get_db_connection
import bcrypt
import psycopg2
import logging
import re
from datetime import datetime

SECRET_KEY = 'gatinhos'

def register_user():
    data = request.get_json()

    username = data.get("username")
    arroba = data.get("arroba")
    email = data.get("email")
    password = data.get("password")
    date_of_birth_str = data.get("date_of_birth")

    if not username or not arroba or not email or not password or not date_of_birth_str:
        return jsonify({"status": "error", "message": "Todos os campos são obrigatórios"}), 400

    if not re.match(r'^[a-zA-Z0-9_]+$', arroba):
        return jsonify({"status": "error", "message": "Arroba inválido: só pode conter letras, números e underline (_)."}), 400

    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return jsonify({"status": "error", "message": "Formato de e-mail inválido"}), 400

    password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'
    if not re.match(password_pattern, password):
        return jsonify({"status": "error", "message": "Senha fraca: deve conter maiúscula, minúscula, número e caractere especial"}), 400

    try:
        date_of_birth = datetime.strptime(date_of_birth_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"status": "error", "message": "Data de nascimento inválida"}), 400

    today = datetime.today().date()
    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    if age < 13:
        return jsonify({"status": "error", "message": "Você precisa ter pelo menos 13 anos para se registrar"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Erro ao conectar com o banco de dados"}), 500

    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (username, arroba, email, password, date_of_birth)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING user_id
        """, (username, arroba, email, hashed_password.decode('utf-8'), date_of_birth))

        user_id = cur.fetchone()[0]
        conn.commit()

    except psycopg2.IntegrityError as e:
        conn.rollback()
        logging.error(f"Erro de integridade: {e}")
        error_message = str(e).lower()
        if "arroba" in error_message:
            return jsonify({"status": "error", "message": "Esse arroba já está em uso"}), 409
        elif "email" in error_message:
            return jsonify({"status": "error", "message": "Esse e-mail já está em uso"}), 409
        return jsonify({"status": "error", "message": "Usuário já registrado"}), 409

    except Exception as e:
        conn.rollback()
        logging.error(f"Erro inesperado: {e}")
        return jsonify({"status": "error", "message": "Erro inesperado no servidor"}), 500

    finally:
        cur.close()
        conn.close()

    return jsonify({"status": "success"}), 200

def login_user():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"status": "error", "message": "Email e senha são obrigatórios"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Erro ao conectar com o banco de dados"}), 500

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id, username, arroba, password FROM users WHERE email = %s
        """, (email,))
        result = cur.fetchone()

        if not result:
            return jsonify({"status": "error", "message": "Usuário não encontrado"}), 404

        user_id, username, arroba, hashed_password = result

        if not bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            return jsonify({"status": "error", "message": "Senha incorreta"}), 401

        session['user_id'] = user_id
        session['username'] = username
        session['arroba'] = arroba 
        session.permanent = True

        return jsonify({
            "status": "success",
            "user": {
                "id": user_id,
                "email": email,
                "username": username,
                "arroba": arroba
            },
            "redirect": "/dashboard"
        }), 200

    except Exception as e:
        conn.rollback()
        logging.error(f"Erro ao fazer login: {e}")
        return jsonify({"status": "error", "message": "Erro interno no servidor"}), 500
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def logout_user():
    session.clear()
    return jsonify({
        'status': 'success',
        'message': 'Logout realizado com sucesso',
        'redirect': '/login'
    }), 200

def create_story():
    data = request.get_json()
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"status": "error", "message": "Usuário não autenticado"}), 401

    title = data.get("title")
    synopsis = data.get("synopsis", "")
    cover_image_id = data.get("cover_image_id", 1)

    if not title:
        return jsonify({"status": "error", "message": "Título é obrigatório"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Erro ao conectar com o banco"}), 500

    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO stories (user_id, title, synopsis, cover_image_id)
            VALUES (%s, %s, %s, %s)
            RETURNING story_id
        """, (user_id, title, synopsis, cover_image_id))
        story_id = cur.fetchone()[0]
        conn.commit()
        return jsonify({"status": "success", "story_id": story_id}), 201
    except Exception as e:
        conn.rollback()
        logging.error(f"Erro ao criar história: {e}")
        return jsonify({"status": "error", "message": "Erro ao criar história"}), 500
    finally:
        cur.close()
        conn.close()

def get_stories():
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Erro ao conectar com o banco"}), 500

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM stories ORDER BY created_at DESC")
        stories = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        results = [dict(zip(columns, row)) for row in stories]
        return jsonify({"status": "success", "stories": results}), 200
    except Exception as e:
        logging.error(f"Erro ao buscar histórias: {e}")
        return jsonify({"status": "error", "message": "Erro ao buscar histórias"}), 500
    finally:
        cur.close()
        conn.close()

def get_story_by_id(story_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Erro ao conectar com o banco"}), 500
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM stories WHERE story_id = %s", (story_id,))
        story = cur.fetchone()
        if not story:
            return jsonify({"status": "error", "message": "História não encontrada"}), 404
        columns = [desc[0] for desc in cur.description]
        result = dict(zip(columns, story))
        return jsonify({"status": "success", "story": result}), 200
    except Exception as e:
        logging.error(f"Erro ao buscar história: {e}")
        return jsonify({"status": "error", "message": "Erro ao buscar história"}), 500
    finally:
        cur.close()
        conn.close()

def update_story(story_id):
    data = request.get_json()
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "Usuário não autenticado"}), 401

    fields = ["title", "synopsis", "cover_image_id", "status", "published_at"]
    updates = []
    values = []

    for field in fields:
        if field in data:
            updates.append(f"{field} = %s")
            values.append(data[field])

    if not updates:
        return jsonify({"status": "error", "message": "Nenhum dado para atualizar"}), 400

    values.append(datetime.utcnow())
    values.append(story_id)
    values.append(user_id)

    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Erro ao conectar com o banco"}), 500

    try:
        cur = conn.cursor()
        cur.execute(f"""
            UPDATE stories SET {', '.join(updates)}, updated_at = %s
            WHERE story_id = %s AND user_id = %s
            RETURNING story_id
        """, tuple(values))
        if cur.rowcount == 0:
            return jsonify({"status": "error", "message": "História não encontrada ou sem permissão"}), 404
        conn.commit()
        return jsonify({"status": "success", "message": "História atualizada com sucesso"}), 200
    except Exception as e:
        conn.rollback()
        logging.error(f"Erro ao atualizar história: {e}")
        return jsonify({"status": "error", "message": "Erro ao atualizar história"}), 500
    finally:
        cur.close()
        conn.close()

def delete_story(story_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "Usuário não autenticado"}), 401

    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Erro ao conectar com o banco"}), 500

    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM stories WHERE story_id = %s AND user_id = %s", (story_id, user_id))
        if cur.rowcount == 0:
            return jsonify({"status": "error", "message": "História não encontrada ou sem permissão"}), 404
        conn.commit()
        return jsonify({"status": "success", "message": "História deletada com sucesso"}), 200
    except Exception as e:
        conn.rollback()
        logging.error(f"Erro ao deletar história: {e}")
        return jsonify({"status": "error", "message": "Erro ao deletar história"}), 500
    finally:
        cur.close()
        conn.close()
