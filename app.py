from flask import Flask, render_template, request, redirect, url_for, current_app, flash, session
from flask_login import LoginManager, UserMixin, logout_user, login_required
import sqlite3
import secrets

app = Flask(__name__)
secret_key = secrets.token_hex()
app.secret_key = secret_key
login_manager = LoginManager()
login_manager.init_app(app)
app.app_context().push()

# Follow the sequence 
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

class Website:
    def __init__(self, id, user_id, name, url):
        self.id = id
        self.user_id = user_id
        self.url = url
        self.name = name

def get_user_by_id(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = {}'.format(int(user_id)))
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        return User(user_data[0], user_data[1], user_data[2])
    else:
        return None

# Callback to reload the user object headon
@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    # TODO 1: Implement the user registration.

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not username:
            flash('username is required!')
        elif not password:
            flash('Password is required!')
        elif not password == confirm_password:
            flash("Password and confirm password is doesn't match ")
        else:
            # connect to database
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            print(c.lastrowid)

            conn.commit()
            c.close()
            conn.close()
            return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # TODO 2: Implement the user login.

    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username:
            flash('username is required!')
        elif not password:
            flash('Password is required!')
        else:
            # connect to database head-on
            conn = sqlite3.connect('database.db', timeout=60)
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username = :user AND password = :pass",
                      {'user': username, 'pass': password})
            data = c.fetchone()
            session["user_id"] = data[0]
            print(session["user_id"])
            conn.commit()
            return redirect(url_for('dashboard'))

    return render_template('login.html', error=error)


@app.route('/logout')
#@login_required
def logout():
    session.pop("user_id",None)
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard', methods=['GET', 'POST'])
#@login_required
def dashboard():
    # TODO 3: Implement the function for adding websites to user profiles.
    if request.method == 'POST':
        website_name = request.form['website_name']
        website_url = request.form['website_url']

        if not website_name:
            flash('website_name is required!')
        elif not website_url:
            flash('website_url is required!')
        else:
            # connect to database
            user=session
            print(user["user_id"])
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute('INSERT INTO websites (user_id,name, url) VALUES (?,?, ?)',
                      (user["user_id"], website_name, website_url))
            conn.commit()
            return redirect(url_for('dashboard'))

    return render_template('dashboard.html')


@app.route('/dashboard/<int:website_id>/delete', methods=['POST'])
#@login_required
def delete(website_id):
    # TODO 4: Implement the function for deleting websites from user profiles.
    conn = sqlite3.connect('database.db', timeout=60)
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE id = ?', (website_id,))
    conn.commit()
    flash(' was successfully deleted!')
    return redirect(url_for("dashboard"))


def create_tables():
    # Creates new tables in the database.db database if they do not already exist.
    conn = sqlite3.connect('database.db', timeout=60)
    c = conn.cursor()
    with current_app.open_resource("schema.sql") as f:
        c.executescript(f.read().decode("utf8"))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
