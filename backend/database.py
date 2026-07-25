import sqlite3, os
from datetime import datetime

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mznsocial.db")

def conn():
    c = sqlite3.connect(DB, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init():
    db = conn(); c = db.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        username     TEXT UNIQUE NOT NULL,
        display_name TEXT NOT NULL,
        email        TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        bio          TEXT DEFAULT '',
        avatar       TEXT DEFAULT '',
        cover        TEXT DEFAULT '',
        followers    INTEGER DEFAULT 0,
        following    INTEGER DEFAULT 0,
        earnings     REAL DEFAULT 0.0,
        total_withdrawn REAL DEFAULT 0.0,
        verified     INTEGER DEFAULT 0,
        created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS posts (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id      INTEGER NOT NULL,
        content      TEXT,
        media_url    TEXT,
        media_type   TEXT DEFAULT 'none',
        likes        INTEGER DEFAULT 0,
        comments     INTEGER DEFAULT 0,
        reposts      INTEGER DEFAULT 0,
        views        INTEGER DEFAULT 0,
        earnings     REAL DEFAULT 0.0,
        is_viral     INTEGER DEFAULT 0,
        created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS likes (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        post_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, post_id)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS follows (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        follower_id INTEGER NOT NULL,
        following_id INTEGER NOT NULL,
        created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(follower_id, following_id)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS comments (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id    INTEGER NOT NULL,
        user_id    INTEGER NOT NULL,
        content    TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(post_id) REFERENCES posts(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS messages (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id     TEXT NOT NULL,
        sender_id   INTEGER NOT NULL,
        content     TEXT NOT NULL,
        msg_type    TEXT DEFAULT 'text',
        created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(sender_id) REFERENCES users(id)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS memories (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER NOT NULL,
        content    TEXT,
        media_url  TEXT,
        boosts     INTEGER DEFAULT 0,
        expires_at DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS earnings_log (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER NOT NULL,
        amount     REAL NOT NULL,
        reason     TEXT NOT NULL,
        post_id    INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS withdrawals (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER NOT NULL,
        amount      REAL NOT NULL,
        moizzen_email TEXT NOT NULL,
        status      TEXT DEFAULT 'pending',
        created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    db.commit(); db.close()

init()
