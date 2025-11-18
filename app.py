"""
Secure Flask ItemManagement Application
Author: Malik Ameer Hamza
Roll No: 22i-1570
Date: October 29, 2025

Security Features:
1. Secure Input Handling with WTForms validation and sanitization
2. Parameterized Queries to prevent SQL injection
3. CSRF Protection with Flask-WTF
4. Secure Session Management with HttpOnly, SameSite, and Secure flags
5. Password Hashing with Flask-Bcrypt
6. User Authentication with Flask-Login
7. Custom Error Handlers to prevent information disclosure
"""

from flask import Flask, render_template, request, redirect, url_for, g, flash
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
from pathlib import Path
import math
from datetime import timedelta
import secrets

# Import secure forms
from forms import ItemForm, RegistrationForm, LoginForm

# ---------- config ----------
DB_PATH = Path(__file__).parent / 'data.db'
PAGE_SIZE = 6  # items per page, change as you like

app = Flask(__name__)
app.config['DATABASE'] = str(DB_PATH)

# Generate a secure secret key (in production, use environment variable)
app.secret_key = secrets.token_hex(32)

# CSRF Protection
csrf = CSRFProtect(app)

# Password Hashing
bcrypt = Bcrypt(app)

# Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

# Secure Session Configuration
# Prevent JavaScript access to cookies
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
# Set to True in production with HTTPS
app.config['SESSION_COOKIE_SECURE'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
    hours=2)  # Session expires after 2 hours
# CSRF tokens don't expire (use session lifetime instead)
app.config['WTF_CSRF_TIME_LIMIT'] = None

# ---------- DB helpers ----------


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db


def column_exists(table: str, column: str) -> bool:
    """Check if a column exists in a table"""
    db = get_db()
    cur = db.execute("PRAGMA table_info(%s)" % table)
    cols = [r["name"] for r in cur.fetchall()]
    return column in cols


def table_exists(table: str) -> bool:
    """Check if a table exists in the database"""
    db = get_db()
    cur = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None


def init_db():
    """
    Create tables if missing, ensure proper schema with migrations.
    Implements secure password storage for users.
    """
    db = get_db()

    # Create items table with minimal schema (without created_at) if it
    # doesn't exist
    db.execute(
        '''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        '''
    )
    db.commit()

    # Create users table for authentication
    db.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    db.commit()

    # If created_at column is missing in items, add it and populate existing
    # rows
    if not column_exists('items', 'created_at'):
        db.execute(
            "ALTER TABLE items ADD COLUMN created_at DATETIME DEFAULT (CURRENT_TIMESTAMP)")
        db.commit()
        db.execute(
            "UPDATE items SET created_at = (datetime('now')) WHERE created_at IS NULL")
        db.commit()

    # Add user_id column to items if it doesn't exist
    if not column_exists('items', 'user_id'):
        db.execute("ALTER TABLE items ADD COLUMN user_id INTEGER")
        db.commit()


# User class for Flask-Login
class User(UserMixin):
    """User model for authentication"""

    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    db = get_db()
    cur = db.execute(
        'SELECT id, username, email FROM users WHERE id = ?', (user_id,))
    user_data = cur.fetchone()
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['email'])
    return None


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# ---------- utility ----------


def query_items(search=None, page=1, page_size=PAGE_SIZE, user_id=None):
    """
    Query items with parameterized queries to prevent SQL injection.
    Optionally filter by user_id for user-specific items.
    """
    db = get_db()
    params = []
    where_clauses = []

    if search:
        where_clauses.append("(title LIKE ? OR description LIKE ?)")
        q = f"%{search}%"
        params.extend([q, q])

    if user_id is not None:
        where_clauses.append("user_id = ?")
        params.append(user_id)

    where = ""
    if where_clauses:
        where = "WHERE " + " AND ".join(where_clauses)

    # Total count - parameterized query
    count_sql = f"SELECT COUNT(*) as cnt FROM items {where}"
    cur = db.execute(count_sql, params)
    total = cur.fetchone()["cnt"]

    # Pagination - parameterized query
    offset = (page - 1) * page_size
    sql = f"SELECT * FROM items {where} ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([page_size, offset])
    cur = db.execute(sql, params)
    items = cur.fetchall()
    return items, total

# ---------- routes ----------

# Authentication Routes


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with secure password hashing"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Check if username or email already exists - parameterized query
        db = get_db()
        existing_user = db.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?',
            (username, email)
        ).fetchone()

        if existing_user:
            flash(
                'Username or email already exists. Please choose a different one.',
                'danger')
            return render_template('register.html', form=form)

        # Hash password securely with bcrypt
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insert new user - parameterized query
        db.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        db.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login with secure password verification"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Retrieve user - parameterized query
        db = get_db()
        user_data = db.execute(
            'SELECT id, username, email, password_hash FROM users WHERE username = ?',
            (username,)
        ).fetchone()

        # Verify password using bcrypt
        if user_data and bcrypt.check_password_hash(
                user_data['password_hash'], password):
            user = User(
                user_data['id'],
                user_data['username'],
                user_data['email'])
            login_user(user)
            flash(f'Welcome back, {username}!', 'success')

            # Redirect to next page if specified, otherwise to index
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(
                url_for('index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


# Item Management Routes
@app.route('/')
def index():
    """Display all items with search and pagination"""
    q = request.args.get('q', '').strip()
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    items, total = query_items(search=q, page=page)
    total_pages = max(1, math.ceil(total / PAGE_SIZE))

    # Create form for modal (requires CSRF token)
    form = ItemForm()

    return render_template('index.html', items=items, q=q, page=page,
                           total_pages=total_pages, total=total, form=form)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new item with secure form validation and parameterized queries"""
    form = ItemForm()

    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data

        # Insert with parameterized query
        db = get_db()
        db.execute(
            'INSERT INTO items (title, description, user_id) VALUES (?, ?, ?)',
            (title, description, current_user.id)
        )
        db.commit()
        flash('Item created successfully.', 'success')
        return redirect(url_for('index'))

    # If validation fails, redisplay form with errors
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')

    q = request.args.get('q', '').strip()
    items, total = query_items(search=q, page=1)
    return render_template('index.html', items=items, q=q, page=1,
                           total_pages=max(1, math.ceil(total / PAGE_SIZE)),
                           total=total, form=form, show_create_modal=True)


@app.route('/item/<int:item_id>')
def view_item(item_id):
    """View single item - parameterized query"""
    db = get_db()
    cur = db.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    item = cur.fetchone()
    if item is None:
        flash('Item not found.', 'warning')
        return redirect(url_for('index'))
    return render_template('view.html', item=item)


@app.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(item_id):
    """Edit item with secure form validation and parameterized queries"""
    db = get_db()
    cur = db.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    item = cur.fetchone()

    if item is None:
        flash('Item not found.', 'warning')
        return redirect(url_for('index'))

    form = ItemForm()

    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data

        # Update with parameterized query
        db.execute(
            'UPDATE items SET title = ?, description = ? WHERE id = ?',
            (title, description, item_id)
        )
        db.commit()
        flash('Item updated successfully.', 'success')
        return redirect(url_for('view_item', item_id=item_id))

    # Prepopulate form with existing data on GET request
    if request.method == 'GET':
        form.title.data = item['title']
        form.description.data = item['description']

    return render_template('edit.html', item=item, form=form)


@app.route('/item/<int:item_id>/delete', methods=['POST'])
@login_required
def delete(item_id):
    """Delete item with CSRF protection and parameterized query"""
    db = get_db()
    # Parameterized query to prevent SQL injection
    db.execute('DELETE FROM items WHERE id = ?', (item_id,))
    db.commit()
    flash('Item deleted successfully.', 'info')
    return redirect(url_for('index'))


# ---------- Error Handlers ----------
@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 error handler to prevent information disclosure"""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Custom 500 error handler to prevent stack trace exposure"""
    return render_template('errors/500.html'), 500


# ---------- run ----------
if __name__ == '__main__':
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with app.app_context():
        init_db()
    app.run(debug=True)
