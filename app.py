from flask import Flask, request, session, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import logging
from dbQueries import (login_user, logout_user, register_user, create_story,
                       get_stories, get_story_by_id, update_story, delete_story)

app = Flask(__name__)

SECRET_KEY = 'gatinhos'
app.secret_key = SECRET_KEY

CORS(app, resources={
    r"/*": {
        "origins": "*",
        "allow_headers": ["Authorization", "Content-Type"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }
})

logging.basicConfig(level=logging.INFO)

@app.route('/check_session')
def check_session():
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'username': session.get('username', 'Convidado'),
            'arroba': session.get('arroba', 'desconhecido')
        })
    return jsonify({'logged_in': False})

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    return login_user()

@app.route('/logout', methods=['POST'])
def logout():
    return logout_user()

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    return register_user()

@app.route('/my-stories')
def my_stories():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('myStories.html')

@app.route('/story')
def story():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('story.html')

if __name__ == '__main__':
    app.run(debug=True)
