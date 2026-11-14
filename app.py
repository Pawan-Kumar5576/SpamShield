
from flask import Flask, render_template, request, redirect
from detector import SpamDetector
import sqlite3
import re
from difflib import SequenceMatcher

app = Flask(__name__)

detector = SpamDetector()

DATABASE = "spamshield.db"

# Known domains for basic lookalike checking
TRUSTED_DOMAINS = [
    "paypal.com",
    "google.com",
    "gmail.com",
    "microsoft.com",
    "amazon.com",
    "apple.com",
    "facebook.com",
    "outlook.com",
    "yahoo.com"
]


def check_sender_email(email):

    email = email.lower().strip()

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.match(pattern, email):
        return {
            "valid": False,
            "status": "INVALID",
            "warning": "Invalid email format"
        }

    domain = email.split("@")[-1]

    for trusted in TRUSTED_DOMAINS:

        if domain == trusted:
            return {
                "valid": True,
                "status": "NORMAL",
                "warning": "No lookalike domain detected"
            }

        similarity = SequenceMatcher(
            None, domain, trusted
        ).ratio()

        if similarity >= 0.80:
            return {
                "valid": True,
                "status": "SUSPICIOUS",
                "warning": "Domain looks similar to " + trusted
            }

    return {
        "valid": True,
        "status": "UNKNOWN",
        "warning": "Sender domain is not in the local trusted-domain list"
    }


def init_db():

    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL,
            spam_probability REAL,
            risk_level TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    columns = [
        row[1] for row in conn.execute(
            "PRAGMA table_info(history)"
        ).fetchall()
    ]

    migrations = {
        "risk_level": "TEXT",
        "sender_email": "TEXT",
        "sender_status": "TEXT"
    }

    for column, data_type in migrations.items():

        if column not in columns:
            conn.execute(
                f"ALTER TABLE history ADD COLUMN {column} {data_type}"
            )

    conn.commit()
    conn.close()


init_db()


# Delete one history record
@app.route("/delete/<int:record_id>", methods=["POST"])
def delete_history(record_id):

    conn = sqlite3.connect(DATABASE)

    conn.execute(
        "DELETE FROM history WHERE id = ?",
        (record_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


# Delete all history records
@app.route("/clear-history", methods=["POST"])
def clear_history():

    conn = sqlite3.connect(DATABASE)

    conn.execute("DELETE FROM history")

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/", methods=["GET", "POST"])
def home():

    result = None
    message = ""
    sender_email = ""

    if request.method == "POST":

        message = request.form.get("message", "").strip()

        sender_email = request.form.get(
            "sender_email", ""
        ).strip().lower()

        if message and sender_email:

            sender_result = check_sender_email(sender_email)

            if not sender_result["valid"]:

                result = {
                    "label": "INVALID EMAIL",
                    "confidence": 0,
                    "spam_probability": 0,
                    "risk_level": "UNKNOWN",
                    "sender_email": sender_email,
                    "sender_status": sender_result["status"],
                    "sender_warning": sender_result["warning"]
                }

            else:

                result = detector.predict(message)

                result["sender_email"] = sender_email
                result["sender_status"] = sender_result["status"]
                result["sender_warning"] = sender_result["warning"]

                # Raise risk for suspicious lookalike domains
                if sender_result["status"] == "SUSPICIOUS":
                    result["risk_level"] = "HIGH"

                conn = sqlite3.connect(DATABASE)

                conn.execute("""
                    INSERT INTO history
                    (message, prediction, confidence,
                     spam_probability, risk_level,
                     sender_email, sender_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    message,
                    result["label"],
                    float(result["confidence"]),
                    float(result["spam_probability"]),
                    result["risk_level"],
                    sender_email,
                    sender_result["status"]
                ))

                conn.commit()
                conn.close()

    # Search and filter
    search = request.args.get("search", "").strip()
    filter_type = request.args.get("filter", "ALL")

    conn = sqlite3.connect(DATABASE)

    total_messages = conn.execute(
        "SELECT COUNT(*) FROM history"
    ).fetchone()[0]

    spam_count = conn.execute(
        "SELECT COUNT(*) FROM history WHERE prediction = 'SPAM'"
    ).fetchone()[0]

    safe_count = conn.execute(
        "SELECT COUNT(*) FROM history WHERE prediction = 'NOT SPAM'"
    ).fetchone()[0]

    query = """
        SELECT id, message, prediction, confidence,
               spam_probability, created_at, risk_level,
               sender_email, sender_status
        FROM history
        WHERE 1=1
    """

    params = []

    if search:
        query += " AND (message LIKE ? OR sender_email LIKE ?)"
        params.extend(["%" + search + "%", "%" + search + "%"])

    if filter_type in ["SPAM", "NOT SPAM"]:
        query += " AND prediction = ?"
        params.append(filter_type)

    query += " ORDER BY id DESC LIMIT 100"

    history = conn.execute(query, params).fetchall()

    conn.close()

    return render_template(
        "index.html",
        result=result,
        message=message,
        sender_email=sender_email,
        accuracy=detector.accuracy,
        total_messages=total_messages,
        spam_count=spam_count,
        safe_count=safe_count,
        history=history,
        search=search,
        filter_type=filter_type
    )


if __name__ == "__main__":
    app.run(debug=True)
