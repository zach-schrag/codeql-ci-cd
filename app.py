from flask import Flask, request, render_template_string, g
import sqlite3

app = Flask(__name__)
DATABASE = 'users.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            DROP TABLE IF EXISTS users
        ''')
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin"))
        db.commit()

def fetch_user(username, password, sanitize=False):
    db = get_db()
    cursor = db.cursor()

    if sanitize:
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        cursor.execute(query, (username, password))
    else:
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        cursor.execute(query)

    return cursor.fetchone()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template_string('''
        <html>
        <body>
            <h3>Vulnerable Login</h3>
            <form action="/login/vulnerable" method="post">
                <label for="vuln_user">Username:</label>
                <input type="text" name="username" id="vuln_user">
                <label for="vuln_pass">Password:</label>
                <input type="text" name="password" id="vuln_pass">
                <button type="submit">Login</button>
            </form>

            <h3>Fixed Login</h3>
            <form action="/login/fixed" method="post">
                <label for="fixed_user">Username:</label>
                <input type="text" name="username" id="fixed_user">
                <label for="fixed_pass">Password:</label>
                <input type="text" name="password" id="fixed_pass">
                <button type="submit">Login</button>
            </form>
        </body>
        </html>
    ''')

@app.route('/login/vulnerable', methods=['POST'])
def login_vulnerable():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    user = fetch_user(username, password, sanitize=False)
    return ("Login successful!" if user else "Invalid credentials!") + "<br/> <a href='/'>Go back</a>"

@app.route('/login/fixed', methods=['POST'])
def login_fixed():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    user = fetch_user(username, password, sanitize=True)
    return ("Login successful!" if user else "Invalid credentials!") + "<br/> <a href='/'>Go back</a>"

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
