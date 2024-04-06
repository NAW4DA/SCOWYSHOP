from flask import *
from flask_session import *
import sqlite3
from datetime import *  
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import webbrowser
import random
import re
from configparser import *

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def init_db():
    with sqlite3.connect('database/data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                date_register TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verification_codes (
                id INTEGER PRIMARY KEY,
                email TEXT NOT NULL,
                code TEXT NOT NULL,
                expiry TIMESTAMP NOT NULL
            )
        ''')

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

@app.route('/')
def index():
    return send_from_directory('html', 'index.html')

@app.route('/html/<path:filename>')
def send_html(filename):
    return send_from_directory('html', filename)

@app.route('/css/<path:filename>')
def send_css(filename):
    return send_from_directory('css', filename)

@app.route('/javascript/<path:filename>')
def send_js(filename):
    return send_from_directory('javascript', filename)

@app.route('/fonts/<path:filename>')
def send_fonts(filename):
    return send_from_directory('fonts', filename)

@app.route('/img/<path:filename>')
def send_img(filename):
    return send_from_directory('img', filename)

@app.route('/favicon/<filename>')
def send_favicon(filename):
    return send_from_directory('favicon', filename)

def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    username, email, password = data.get('username'), data.get('email'), data.get('password')
    if not all([username, email, password]):
        return jsonify({'status': 'error', 'message': 'All fields are required'}), 400

    if not is_valid_email(email):
        return jsonify({'status': 'error', 'message': 'Invalid email format'}), 400

    date_register = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with sqlite3.connect('database/data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, email, password, date_register) 
                VALUES (?, ?, ?, ?)
            ''', (username, email, password, date_register))
    except sqlite3.IntegrityError:
        return jsonify({'status': 'error', 'message': 'User with this username or email already exists'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    return jsonify({'status': 'success', 'message': 'User successfully registered'})

def read_config():
    config = ConfigParser()
    config.read('config.ini')
    return config

def send_email_with_code(email_address, verification_code):
    config = read_config()
    sender_email, email_password = config['email']['sender_email'], config['email']['email_password']
    smtp_server, smtp_port = config['email']['smtp_server'], config['email'].getint('smtp_port')

    message = MIMEMultipart("alternative")
    message["Subject"] = "Код подтверждения"
    message["From"] = sender_email
    message["To"] = email_address

    text = f"Привет!\nВаш код подтверждения: {verification_code}"
    html = f"<html><body><p>Привет!<br>Ваш код подтверждения: <b>{verification_code}</b></p></body></html>"

    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, email_password)
            server.sendmail(sender_email, email_address, message.as_string())
        expiry = datetime.now() + timedelta(minutes=10)
        with sqlite3.connect('database/data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO verification_codes (email, code, expiry) 
                VALUES (?, ?, ?)
            ''', (email_address, verification_code, expiry))
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    return True

@app.route('/api/send-verification-code', methods=['POST'])
def api_send_verification_code():
    email = request.json.get('email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Email is required'}), 400
    verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    if send_email_with_code(email, verification_code):
        return jsonify({'status': 'success', 'message': 'Code sent'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send code'})

@app.route('/api/verify-code', methods=['POST'])
def verify_code():
    data = request.json
    email, code = data.get('email'), data.get('code')

    with sqlite3.connect('database/data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM verification_codes 
            WHERE email = ? AND code = ? AND expiry > ?
        ''', (email, code, datetime.now()))
        verification = cursor.fetchone()

    if verification:
        return jsonify({'status': 'success', 'message': 'Code verified successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid or expired code'}), 400
    
@app.route('/api/user')
def get_user_info():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Не аутентифицирован'}), 401
    
    user_id = session['user_id']
    try:
        with sqlite3.connect('database/data.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT username, email, date_register FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            if user:
                return jsonify({
                    'status': 'success',
                    'data': {
                        'username': user['username'],
                        'email': user['email'],
                        'dateRegister': user['date_register']
                    }
                })
            else:
                return jsonify({'status': 'error', 'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'status': 'success', 'message': 'Вы успешно вышли из системы'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({'status': 'error', 'message': 'Username and password are required'}), 400

    try:
        with sqlite3.connect('database/data.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT id, username FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()
            if user:
                session['user_id'] = user['id']
                return jsonify({'status': 'success', 'message': 'Logged in successfully', 'user': {'username': user['username']}})
            else:
                return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    init_db()
    open_browser()
    app.run(debug=True)
