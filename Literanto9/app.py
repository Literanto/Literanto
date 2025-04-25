from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import logging
from datetime import datetime

from dbCommands.dbQueries import insert_user, get_user_by_email

app = Flask(__name__)
bcrypt = Bcrypt(app)
CORS(app)

app.secret_key = 'teste'

logging.basicConfig(level=logging.INFO)

def check_token():
    user_token = session.get('user_token')
    token_expiration = session.get('token_expiration')

    if user_token and token_expiration:
        if isinstance(token_expiration, str):
            try:
                token_expiration = datetime.strptime(token_expiration, '%Y-%m-%d %H:%M:%S')
            except ValueError as e:
                logging.error(f"Erro ao converter token_expiration: {e}")
                return False

        if datetime.now() > token_expiration:
            session.clear()
            return False

        return True

    return False

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"status": "error"}), 400

    user = get_user_by_email(email)
    if not user:
        return jsonify({"status": "error"}), 401

    stored_password = user["user_password"]
    password_match = bcrypt.check_password_hash(stored_password, password)

    if not password_match:
        return jsonify({"status": "error"}), 401

    session['user_id'] = user["user_code"]
    session['user_email'] = email

    return jsonify({
        "status": "success",
        "redirect": url_for('dashboard')
    }), 200

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"status": "error"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    success = insert_user(username, email, hashed_password)
    if success:
        return jsonify({
            "status": "success",
            "redirect": url_for('login')
        }), 200
    else:
        return jsonify({"status": "error"}), 400

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
