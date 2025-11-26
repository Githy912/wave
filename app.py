from flask import Flask, request, jsonify, render_template_string
import psycopg2
import os
from dotenv import load_dotenv

# Load .env file (for DATABASE_URL)
load_dotenv()

app = Flask(__name__)

# Get Neon PostgreSQL connection URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in .env")

def get_db_conn():
    return psycopg2.connect(DATABASE_URL)

# Create table if not exists
def init_db():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wave_messages (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def index():
    """Serve the main Wave HTML file."""
    # IMPORTANT: make sure this filename matches your file
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
    return render_template_string(html)

@app.route("/contact", methods=["POST"])
def contact():
    """Receive contact form and save into Neon database."""
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    if not name or not email or not message:
        return jsonify({"ok": False, "error": "Missing fields"}), 400

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO wave_messages (name, email, message) VALUES (%s, %s, %s)",
        (name, email, message)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"ok": True, "msg": "Saved to database"})

@app.route("/admin/messages")
def admin_messages():
    """Very simple admin view for reading stored messages."""
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, email, message, created_at
        FROM wave_messages
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    html = "<h1>Wave Messages</h1>"
    for r in rows:
        html += (
            "<div style='margin-bottom:15px;"
            "padding:10px;border-radius:8px;border:1px solid #ccc;'>"
        )
        html += f"<strong>#{r[0]} — {r[1]} ({r[2]})</strong><br>"
        html += f"{r[3]}<br>"
        html += f"<small>{r[4]}</small>"
        html += "</div>"
        
    return html

if __name__ == "__main__":
    init_db()
    # You can change port if needed, e.g. app.run(port=8000)
    app.run(debug=True)
