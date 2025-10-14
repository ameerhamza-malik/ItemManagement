from flask import Flask, render_template, request, redirect, url_for, g, flash
import sqlite3
from pathlib import Path
import math

# ---------- config ----------
DB_PATH = Path(__file__).parent / 'data.db'
PAGE_SIZE = 6  # items per page, change as you like

app = Flask(__name__)
app.config['DATABASE'] = str(DB_PATH)
app.secret_key = "replace_this_with_a_random_secret"  # change this for production

# ---------- DB helpers ----------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

def column_exists(table: str, column: str) -> bool:
    db = get_db()
    cur = db.execute("PRAGMA table_info(%s)" % table)
    cols = [r["name"] for r in cur.fetchall()]
    return column in cols

def init_db():
    """
    Create table if missing, ensure created_at column exists (migrate if necessary).
    """
    db = get_db()

    # create table with minimal schema (without created_at) if it doesn't exist
    db.execute(
        '''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT
        )
        '''
    )
    db.commit()

    # If created_at column is missing, add it and populate existing rows
    if not column_exists('items', 'created_at'):
        # Add column with default CURRENT_TIMESTAMP for new rows
        # Note: SQLite accepts DEFAULT (CURRENT_TIMESTAMP)
        db.execute("ALTER TABLE items ADD COLUMN created_at DATETIME DEFAULT (CURRENT_TIMESTAMP)")
        db.commit()
        # Populate existing rows that have NULL in created_at with current timestamp
        db.execute("UPDATE items SET created_at = (datetime('now')) WHERE created_at IS NULL")
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# ---------- utility ----------
def query_items(search=None, page=1, page_size=PAGE_SIZE):
    db = get_db()
    params = []
    where = ""
    if search:
        where = "WHERE title LIKE ? OR description LIKE ?"
        q = f"%{search}%"
        params.extend([q, q])

    # total count
    count_sql = f"SELECT COUNT(*) as cnt FROM items {where}"
    cur = db.execute(count_sql, params)
    total = cur.fetchone()["cnt"]

    # pagination
    offset = (page - 1) * page_size
    sql = f"SELECT * FROM items {where} ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([page_size, offset])
    cur = db.execute(sql, params)
    items = cur.fetchall()
    return items, total

# ---------- routes ----------
@app.route('/')
def index():
    q = request.args.get('q', '').strip()
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    items, total = query_items(search=q, page=page)
    total_pages = max(1, math.ceil(total / PAGE_SIZE))
    return render_template('index.html', items=items, q=q, page=page, total_pages=total_pages, total=total)

@app.route('/create', methods=['POST'])
def create():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()

    if not title:
        q = request.args.get('q', '').strip()
        items, total = query_items(search=q, page=1)
        flash('Title is required.', 'danger')
        return render_template('index.html', items=items, q=q, page=1,
                               total_pages=max(1, math.ceil(total / PAGE_SIZE)),
                               total=total, show_create_modal=True,
                               title_prefill=title, description_prefill=description)

    db = get_db()
    db.execute('INSERT INTO items (title, description) VALUES (?, ?)', (title, description))
    db.commit()
    flash('Item created successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/item/<int:item_id>')
def view_item(item_id):
    db = get_db()
    cur = db.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    item = cur.fetchone()
    if item is None:
        flash('Item not found.', 'warning')
        return redirect(url_for('index'))
    return render_template('view.html', item=item)

@app.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
def edit(item_id):
    db = get_db()
    cur = db.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    item = cur.fetchone()
    if item is None:
        flash('Item not found.', 'warning')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        if not title:
            flash('Title is required.', 'danger')
            return render_template('edit.html', item=item)
        db.execute('UPDATE items SET title = ?, description = ? WHERE id = ?', (title, description, item_id))
        db.commit()
        flash('Item updated.', 'success')
        return redirect(url_for('view_item', item_id=item_id))

    return render_template('edit.html', item=item)

@app.route('/item/<int:item_id>/delete', methods=['POST'])
def delete(item_id):
    db = get_db()
    db.execute('DELETE FROM items WHERE id = ?', (item_id,))
    db.commit()
    flash('Item deleted.', 'info')
    return redirect(url_for('index'))

# ---------- run ----------
if __name__ == '__main__':
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with app.app_context():
        init_db()
    app.run(debug=True)
