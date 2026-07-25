import sys, os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from flask import Flask, request, jsonify, send_from_directory
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
from database import conn
import bcrypt
from datetime import datetime, timedelta

FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET", "mznsocial-secret-2024")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

CORS(app)
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def add_earning(user_id, amount, reason, post_id=None):
    db = conn()
    c = db.cursor()
    c.execute("UPDATE users SET earnings = earnings + ? WHERE id = ?", (amount, user_id))
    c.execute(
        "INSERT INTO earnings_log (user_id, amount, reason, post_id) VALUES (?,?,?,?)",
        (user_id, amount, reason, post_id)
    )
    db.commit()
    db.close()

def row_to_dict(row):
    return dict(row) if row else None

def rows_to_list(rows):
    return [dict(r) for r in rows]

# ─────────────────────────────────────────
# STATIC / INDEX
# ─────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

# ─────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    display_name = (data.get("display_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not all([username, display_name, email, password]):
        return jsonify(error="All fields are required"), 400

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    db = conn()
    c = db.cursor()
    try:
        c.execute(
            "INSERT INTO users (username, display_name, email, password_hash) VALUES (?,?,?,?)",
            (username, display_name, email, pw_hash)
        )
        db.commit()
        user_id = c.lastrowid
    except Exception as e:
        db.close()
        return jsonify(error="Username or email already taken"), 409
    db.close()

    # creation bonus
    add_earning(user_id, 0.10, "account_created")

    token = create_access_token(identity=str(user_id))
    return jsonify(token=token, user_id=user_id, username=username), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    db = conn()
    c = db.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    db.close()

    if not user or not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return jsonify(error="Invalid credentials"), 401

    token = create_access_token(identity=str(user["id"]))
    return jsonify(token=token, user_id=user["id"], username=user["username"]), 200

# ─────────────────────────────────────────
# FEED
# ─────────────────────────────────────────

@app.route("/api/feed", methods=["GET"])
@jwt_required()
def get_feed():
    uid = int(get_jwt_identity())
    page = int(request.args.get("page", 1))
    limit = 20
    offset = (page - 1) * limit

    db = conn()
    c = db.cursor()
    c.execute("""
        SELECT p.*, u.username, u.display_name, u.avatar, u.verified
        FROM posts p
        JOIN users u ON u.id = p.user_id
        WHERE p.user_id IN (
            SELECT following_id FROM follows WHERE follower_id = ?
        ) OR p.user_id = ?
        ORDER BY p.created_at DESC
        LIMIT ? OFFSET ?
    """, (uid, uid, limit, offset))
    posts = rows_to_list(c.fetchall())

    # fill with trending if feed is sparse
    if len(posts) < 5:
        c.execute("""
            SELECT p.*, u.username, u.display_name, u.avatar, u.verified
            FROM posts p JOIN users u ON u.id = p.user_id
            ORDER BY p.likes DESC, p.views DESC
            LIMIT ?
        """, (limit,))
        trending = rows_to_list(c.fetchall())
        seen = {p["id"] for p in posts}
        posts += [t for t in trending if t["id"] not in seen]

    # mark liked posts
    liked_ids = set()
    if posts:
        ids_placeholder = ",".join(["?"] * len(posts))
        c.execute(
            f"SELECT post_id FROM likes WHERE user_id=? AND post_id IN ({ids_placeholder})",
            [uid] + [p["id"] for p in posts]
        )
        liked_ids = {r["post_id"] for r in c.fetchall()}

    for p in posts:
        p["liked_by_me"] = p["id"] in liked_ids

    db.close()
    return jsonify(posts=posts, page=page)


@app.route("/api/posts", methods=["POST"])
@jwt_required()
def create_post():
    uid = int(get_jwt_identity())
    data = request.get_json() or {}
    content = data.get("content", "")
    media_url = data.get("media_url", "")
    media_type = data.get("media_type", "none")

    if not content and not media_url:
        return jsonify(error="Post must have content or media"), 400

    db = conn()
    c = db.cursor()
    c.execute(
        "INSERT INTO posts (user_id, content, media_url, media_type) VALUES (?,?,?,?)",
        (uid, content, media_url, media_type)
    )
    db.commit()
    post_id = c.lastrowid
    db.close()

    add_earning(uid, 0.10, "post_created", post_id)
    return jsonify(post_id=post_id, message="Post created"), 201


@app.route("/api/posts/<int:post_id>/like", methods=["POST"])
@jwt_required()
def like_post(post_id):
    uid = int(get_jwt_identity())
    db = conn()
    c = db.cursor()

    try:
        c.execute("INSERT INTO likes (user_id, post_id) VALUES (?,?)", (uid, post_id))
        c.execute("UPDATE posts SET likes = likes + 1 WHERE id = ?", (post_id,))
        db.commit()

        # award post owner
        c.execute("SELECT user_id, likes, is_viral FROM posts WHERE id = ?", (post_id,))
        post = c.fetchone()
        if post:
            add_earning(post["user_id"], 0.05, "like_received", post_id)
            # viral bonus
            if post["likes"] >= 500 and not post["is_viral"]:
                c.execute("UPDATE posts SET is_viral = 1 WHERE id = ?", (post_id,))
                db.commit()
                add_earning(post["user_id"], 50.00, "viral_bonus", post_id)

        db.close()
        return jsonify(liked=True)
    except Exception:
        # already liked – unlike
        c.execute("DELETE FROM likes WHERE user_id=? AND post_id=?", (uid, post_id))
        c.execute("UPDATE posts SET likes = MAX(0, likes - 1) WHERE id = ?", (post_id,))
        db.commit()
        db.close()
        return jsonify(liked=False)


@app.route("/api/posts/<int:post_id>/comment", methods=["POST"])
@jwt_required()
def add_comment(post_id):
    uid = int(get_jwt_identity())
    data = request.get_json() or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify(error="Comment cannot be empty"), 400

    db = conn()
    c = db.cursor()
    c.execute("INSERT INTO comments (post_id, user_id, content) VALUES (?,?,?)", (post_id, uid, content))
    c.execute("UPDATE posts SET comments = comments + 1 WHERE id = ?", (post_id,))
    db.commit()
    comment_id = c.lastrowid

    # award post owner
    c.execute("SELECT user_id FROM posts WHERE id = ?", (post_id,))
    post = c.fetchone()
    db.close()

    if post and post["user_id"] != uid:
        add_earning(post["user_id"], 0.02, "comment_received", post_id)

    return jsonify(comment_id=comment_id), 201


@app.route("/api/posts/<int:post_id>/comments", methods=["GET"])
def get_comments(post_id):
    db = conn()
    c = db.cursor()
    c.execute("""
        SELECT cm.*, u.username, u.display_name, u.avatar
        FROM comments cm JOIN users u ON u.id = cm.user_id
        WHERE cm.post_id = ?
        ORDER BY cm.created_at ASC
    """, (post_id,))
    comments = rows_to_list(c.fetchall())
    db.close()
    return jsonify(comments=comments)


@app.route("/api/posts/<int:post_id>/view", methods=["POST"])
@jwt_required()
def record_view(post_id):
    uid = int(get_jwt_identity())
    db = conn()
    c = db.cursor()
    c.execute("UPDATE posts SET views = views + 1 WHERE id = ?", (post_id,))
    db.commit()

    c.execute("SELECT user_id, views FROM posts WHERE id = ?", (post_id,))
    post = c.fetchone()
    db.close()

    if post:
        # every 100 views = R0.50 to owner
        if post["views"] % 100 == 0:
            add_earning(post["user_id"], 0.50, "100_views_milestone", post_id)
        # watcher earns R0.01
        if post["user_id"] != uid:
            add_earning(uid, 0.01, "watch_to_earn", post_id)

    return jsonify(ok=True)


@app.route("/api/trending", methods=["GET"])
def get_trending():
    db = conn()
    c = db.cursor()
    c.execute("""
        SELECT p.*, u.username, u.display_name, u.avatar, u.verified
        FROM posts p JOIN users u ON u.id = p.user_id
        ORDER BY (p.likes * 2 + p.views) DESC
        LIMIT 30
    """)
    posts = rows_to_list(c.fetchall())
    db.close()
    return jsonify(posts=posts)

# ─────────────────────────────────────────
# USERS
# ─────────────────────────────────────────

@app.route("/api/user/me", methods=["GET"])
@jwt_required()
def me():
    uid = int(get_jwt_identity())
    db = conn()
    c = db.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (uid,))
    user = row_to_dict(c.fetchone())
    db.close()
    if not user:
        return jsonify(error="User not found"), 404
    user.pop("password_hash", None)
    return jsonify(user=user)


@app.route("/api/user/<username>", methods=["GET"])
def get_user(username):
    db = conn()
    c = db.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = row_to_dict(c.fetchone())
    if not user:
        db.close()
        return jsonify(error="User not found"), 404
    user.pop("password_hash", None)

    c.execute("""
        SELECT p.*, u.username, u.display_name, u.avatar, u.verified
        FROM posts p JOIN users u ON u.id = p.user_id
        WHERE p.user_id = ?
        ORDER BY p.created_at DESC LIMIT 20
    """, (user["id"],))
    posts = rows_to_list(c.fetchall())
    db.close()

    return jsonify(user=user, posts=posts)


@app.route("/api/user/follow/<username>", methods=["POST"])
@jwt_required()
def follow_user(username):
    uid = int(get_jwt_identity())
    db = conn()
    c = db.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    target = c.fetchone()
    if not target:
        db.close()
        return jsonify(error="User not found"), 404
    target_id = target["id"]
    if target_id == uid:
        db.close()
        return jsonify(error="Cannot follow yourself"), 400

    try:
        c.execute("INSERT INTO follows (follower_id, following_id) VALUES (?,?)", (uid, target_id))
        c.execute("UPDATE users SET followers = followers + 1 WHERE id = ?", (target_id,))
        c.execute("UPDATE users SET following = following + 1 WHERE id = ?", (uid,))
        db.commit()
        db.close()
        return jsonify(following=True)
    except Exception:
        c.execute("DELETE FROM follows WHERE follower_id=? AND following_id=?", (uid, target_id))
        c.execute("UPDATE users SET followers = MAX(0, followers - 1) WHERE id = ?", (target_id,))
        c.execute("UPDATE users SET following = MAX(0, following - 1) WHERE id = ?", (uid,))
        db.commit()
        db.close()
        return jsonify(following=False)


@app.route("/api/user/update", methods=["PUT"])
@jwt_required()
def update_user():
    uid = int(get_jwt_identity())
    data = request.get_json() or {}
    bio = data.get("bio")
    display_name = data.get("display_name")
    avatar = data.get("avatar")
    cover = data.get("cover")

    fields, vals = [], []
    if bio is not None:        fields.append("bio=?"); vals.append(bio)
    if display_name is not None: fields.append("display_name=?"); vals.append(display_name)
    if avatar is not None:     fields.append("avatar=?"); vals.append(avatar)
    if cover is not None:      fields.append("cover=?"); vals.append(cover)

    if not fields:
        return jsonify(error="Nothing to update"), 400

    vals.append(uid)
    db = conn()
    c = db.cursor()
    c.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", vals)
    db.commit()
    db.close()
    return jsonify(ok=True)

# ─────────────────────────────────────────
# VIDEOS
# ─────────────────────────────────────────

@app.route("/api/videos", methods=["GET"])
def get_videos():
    page = int(request.args.get("page", 1))
    limit = 10
    offset = (page - 1) * limit
    db = conn()
    c = db.cursor()
    c.execute("""
        SELECT p.*, u.username, u.display_name, u.avatar, u.verified
        FROM posts p JOIN users u ON u.id = p.user_id
        WHERE p.media_type = 'video'
        ORDER BY p.created_at DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    videos = rows_to_list(c.fetchall())
    db.close()
    return jsonify(videos=videos)


@app.route("/api/videos/trending", methods=["GET"])
def trending_videos():
    db = conn()
    c = db.cursor()
    c.execute("""
        SELECT p.*, u.username, u.display_name, u.avatar, u.verified
        FROM posts p JOIN users u ON u.id = p.user_id
        WHERE p.media_type = 'video'
        ORDER BY (p.likes * 2 + p.views) DESC
        LIMIT 20
    """)
    videos = rows_to_list(c.fetchall())
    db.close()
    return jsonify(videos=videos)

# ─────────────────────────────────────────
# CHAT
# ─────────────────────────────────────────

@app.route("/api/chat/rooms", methods=["GET"])
@jwt_required()
def chat_rooms():
    uid = int(get_jwt_identity())
    db = conn()
    c = db.cursor()
    # rooms where this user appears in the room_id
    c.execute("""
        SELECT DISTINCT room_id,
            MAX(created_at) as last_message_at,
            (SELECT content FROM messages m2 WHERE m2.room_id = m.room_id ORDER BY created_at DESC LIMIT 1) as last_message
        FROM messages m
        WHERE room_id LIKE ?
        GROUP BY room_id
        ORDER BY last_message_at DESC
    """, (f"%_{uid}_%",))
    rooms_raw = rows_to_list(c.fetchall())

    rooms = []
    for r in rooms_raw:
        parts = r["room_id"].replace("_", "").split()
        other_id = None
        for part in r["room_id"].split("_"):
            if part.isdigit() and int(part) != uid:
                other_id = int(part)
                break
        if other_id:
            c.execute("SELECT id, username, display_name, avatar FROM users WHERE id = ?", (other_id,))
            other = c.fetchone()
            r["other_user"] = row_to_dict(other)
        rooms.append(r)

    db.close()
    return jsonify(rooms=rooms)


@app.route("/api/chat/messages/<room_id>", methods=["GET"])
@jwt_required()
def chat_messages(room_id):
    db = conn()
    c = db.cursor()
    c.execute("""
        SELECT m.*, u.username, u.display_name, u.avatar
        FROM messages m JOIN users u ON u.id = m.sender_id
        WHERE m.room_id = ?
        ORDER BY m.created_at ASC
        LIMIT 100
    """, (room_id,))
    messages = rows_to_list(c.fetchall())
    db.close()
    return jsonify(messages=messages)


@app.route("/api/chat/send", methods=["POST"])
@jwt_required()
def send_message():
    uid = int(get_jwt_identity())
    data = request.get_json() or {}
    room_id = data.get("room_id", "")
    content = (data.get("content") or "").strip()

    if not room_id or not content:
        return jsonify(error="room_id and content required"), 400

    db = conn()
    c = db.cursor()
    c.execute(
        "INSERT INTO messages (room_id, sender_id, content) VALUES (?,?,?)",
        (room_id, uid, content)
    )
    db.commit()
    msg_id = c.lastrowid
    db.close()

    socketio.emit("new_message", {"room_id": room_id, "sender_id": uid, "content": content}, room=room_id)
    return jsonify(message_id=msg_id), 201

# ─────────────────────────────────────────
# MEMORIES
# ─────────────────────────────────────────

@app.route("/api/memories", methods=["GET"])
@jwt_required()
def get_memories():
    uid = int(get_jwt_identity())
    db = conn()
    c = db.cursor()
    c.execute("""
        SELECT m.*, u.username, u.display_name, u.avatar
        FROM memories m JOIN users u ON u.id = m.user_id
        WHERE (m.user_id IN (SELECT following_id FROM follows WHERE follower_id=?) OR m.user_id=?)
          AND (m.expires_at IS NULL OR m.expires_at > CURRENT_TIMESTAMP)
        ORDER BY m.boosts DESC, m.created_at DESC
    """, (uid, uid))
    memories = rows_to_list(c.fetchall())
    db.close()
    return jsonify(memories=memories)


@app.route("/api/memories", methods=["POST"])
@jwt_required()
def create_memory():
    uid = int(get_jwt_identity())
    data = request.get_json() or {}
    content = data.get("content", "")
    media_url = data.get("media_url", "")
    expires_hours = int(data.get("expires_hours", 24))
    expires_at = (datetime.utcnow() + timedelta(hours=expires_hours)).strftime("%Y-%m-%d %H:%M:%S")

    db = conn()
    c = db.cursor()
    c.execute(
        "INSERT INTO memories (user_id, content, media_url, expires_at) VALUES (?,?,?,?)",
        (uid, content, media_url, expires_at)
    )
    db.commit()
    mem_id = c.lastrowid
    db.close()
    return jsonify(memory_id=mem_id), 201


@app.route("/api/memories/<int:mem_id>/boost", methods=["POST"])
@jwt_required()
def boost_memory(mem_id):
    db = conn()
    c = db.cursor()
    c.execute("UPDATE memories SET boosts = boosts + 1 WHERE id = ?", (mem_id,))
    db.commit()
    db.close()
    return jsonify(boosted=True)

# ─────────────────────────────────────────
# EARNINGS
# ─────────────────────────────────────────

@app.route("/api/earnings", methods=["GET"])
@jwt_required()
def get_earnings():
    uid = int(get_jwt_identity())
    db = conn()
    c = db.cursor()

    c.execute("SELECT earnings, total_withdrawn FROM users WHERE id = ?", (uid,))
    user = c.fetchone()

    c.execute("""
        SELECT * FROM earnings_log WHERE user_id = ?
        ORDER BY created_at DESC LIMIT 50
    """, (uid,))
    log = rows_to_list(c.fetchall())

    c.execute("""
        SELECT * FROM withdrawals WHERE user_id = ?
        ORDER BY created_at DESC LIMIT 10
    """, (uid,))
    withdrawals = rows_to_list(c.fetchall())

    db.close()
    return jsonify(
        balance=user["earnings"],
        total_withdrawn=user["total_withdrawn"],
        log=log,
        withdrawals=withdrawals
    )


@app.route("/api/earnings/withdraw", methods=["POST"])
@jwt_required()
def withdraw():
    uid = int(get_jwt_identity())
    data = request.get_json() or {}
    amount = float(data.get("amount", 0))
    moizzen_email = (data.get("moizzen_email") or "").strip()

    if amount <= 0:
        return jsonify(error="Amount must be positive"), 400
    if not moizzen_email:
        return jsonify(error="Moizzen email required"), 400

    db = conn()
    c = db.cursor()
    c.execute("SELECT earnings FROM users WHERE id = ?", (uid,))
    user = c.fetchone()

    if not user or user["earnings"] < amount:
        db.close()
        return jsonify(error="Insufficient balance"), 400

    c.execute("UPDATE users SET earnings = earnings - ?, total_withdrawn = total_withdrawn + ? WHERE id = ?",
              (amount, amount, uid))
    c.execute(
        "INSERT INTO withdrawals (user_id, amount, moizzen_email) VALUES (?,?,?)",
        (uid, amount, moizzen_email)
    )
    db.commit()
    withdrawal_id = c.lastrowid
    db.close()

    return jsonify(withdrawal_id=withdrawal_id, status="pending", amount=amount)

# ─────────────────────────────────────────
# SOCKET.IO
# ─────────────────────────────────────────

@socketio.on("join_room")
def on_join(data):
    room = data.get("room_id")
    if room:
        join_room(room)
        emit("status", {"msg": f"Joined {room}"})

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
