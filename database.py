import sqlite3

db = sqlite3.connect("users.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
user_id INTEGER PRIMARY KEY,
username TEXT,
completed INTEGER DEFAULT 0
)
""")

db.commit()

def add(uid, username):
    cur.execute(
        "INSERT OR IGNORE INTO users VALUES(?,?,0)",
        (uid, username)
    )
    db.commit()

def done(uid):
    cur.execute(
        "UPDATE users SET completed=1 WHERE user_id=?",
        (uid,)
    )
    db.commit()

def completed(uid):
    r = cur.execute(
        "SELECT completed FROM users WHERE user_id=?",
        (uid,)
    ).fetchone()
    return r and r[0] == 1
