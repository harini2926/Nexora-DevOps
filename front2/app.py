from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

import smtplib
import random
import subprocess
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

load_dotenv()


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

# Secret key for sessions
app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "development-only-change-this"
)


# ============================================================
# DATABASE
# ============================================================

DATABASE = os.path.join(
    os.path.dirname(__file__),
    "database",
    "smart_game_studio.db"
)


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

# ============================================================
# OTP HELPERS
# ============================================================

def generate_otp():
    """Return a 6-digit numeric code."""
    return f"{random.randint(0, 999999):06d}"


def send_otp_email(to_email, code, purpose):
    host     = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port     = int(os.getenv("SMTP_PORT", "587"))
    user     = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")

    if not user or not password:
        print("[Nexora] SMTP credentials missing in .env")
        return False

    subject = ("Your Nexora signup code"
               if purpose == "register"
               else "Your Nexora login code")

    text_body = f"""Your Nexora verification code is:

{code}

It expires in 10 minutes. If you did not request this, ignore this email.
"""

    html_body = f"""
    <html>
      <body style="font-family: Inter, Arial, sans-serif;
                   background:#0d0d16; color:#ffffff; padding:40px;">
        <div style="max-width:480px; margin:0 auto; background:#15162a;
                    border-radius:16px; padding:40px;
                    border:1px solid rgba(255,255,255,0.08);">
          <h2 style="margin:0 0 8px; color:#ffffff;">Nexora</h2>
          <p style="color:rgba(255,255,255,0.7); font-size:15px;
                    margin:0 0 32px;">Your verification code</p>
          <div style="font-size:40px; font-weight:800; letter-spacing:12px;
                      color:#a78bfa; text-align:center; padding:24px 0;
                      background:rgba(139,92,246,0.08);
                      border-radius:12px; margin-bottom:24px;">
            {code}
          </div>
          <p style="color:rgba(255,255,255,0.5); font-size:13px;
                    margin:0; line-height:1.6;">
            This code expires in 10 minutes.<br>
            If you did not request this, ignore this email.
          </p>
        </div>
      </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Nexora <{user}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(host, port, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(user, password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"[Nexora] Failed to send OTP: {e}")
        return False

def store_otp(email, purpose, provider):
    """Create a fresh OTP row for this email and return the code."""
    code = generate_otp()
    expires = (datetime.utcnow() + timedelta(minutes=10)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    connection = get_db()

    # Invalidate any older unused codes for this email+purpose
    connection.execute("""
        UPDATE otp_codes
        SET used = 1
        WHERE email = ? AND purpose = ? AND used = 0
    """, (email, purpose))

    connection.execute("""
        INSERT INTO otp_codes (email, code, purpose, provider, expires_at)
        VALUES (?, ?, ?, ?, ?)
    """, (email, code, purpose, provider, expires))

    connection.commit()
    connection.close()

    # ---- Send the email --------------------------------------------
    sent = send_otp_email(email, code, purpose)
    if not sent:
        print(f"[Nexora OTP FALLBACK] {purpose} for {email}: {code}")
    # ----------------------------------------------------------------

    return code


def verify_otp(email, code, purpose):
    """Return True if `code` is valid for this email+purpose."""
    connection = get_db()
    row = connection.execute("""
        SELECT id, expires_at
        FROM otp_codes
        WHERE email = ? AND code = ? AND purpose = ? AND used = 0
        ORDER BY id DESC
        LIMIT 1
    """, (email, code, purpose)).fetchone()

    if not row:
        connection.close()
        return False

    try:
        exp = datetime.strptime(row["expires_at"], "%Y-%m-%d %H:%M:%S")
        if exp < datetime.utcnow():
            connection.close()
            return False
    except Exception:
        connection.close()
        return False

    connection.execute("UPDATE otp_codes SET used = 1 WHERE id = ?",
                       (row["id"],))
    connection.commit()
    connection.close()
    return True


def user_exists(email):
    connection = get_db()
    row = connection.execute(
        "SELECT id, username FROM users WHERE email = ?", (email,)
    ).fetchone()
    connection.close()
    return row


def init_database():
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT NOT NULL,
            email         TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            provider      TEXT NOT NULL DEFAULT 'local',
            full_name     TEXT,
            age           INTEGER,
            country       TEXT,
            bio           TEXT,
            verified_at   TIMESTAMP,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS otp_codes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            email      TEXT NOT NULL,
            code       TEXT NOT NULL,
            purpose    TEXT NOT NULL,
            provider   TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used       INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()

# ============================================================
# HOME / LANDING PAGE
# ============================================================
import random
from datetime import datetime, timedelta

def generate_otp():
    """Return a 6-digit numeric code."""
    return f"{random.randint(0, 999999):06d}"


def store_otp(email, purpose, provider):
    """Create a fresh OTP row for this email and send it."""
    code = generate_otp()
    expires = (datetime.utcnow() + timedelta(minutes=10)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    connection = get_db()

    # Invalidate any older unused codes for this email+purpose
    connection.execute("""
        UPDATE otp_codes
        SET used = 1
        WHERE email = ? AND purpose = ? AND used = 0
    """, (email, purpose))

    # Insert the new code
    connection.execute("""
        INSERT INTO otp_codes (email, code, purpose, provider, expires_at)
        VALUES (?, ?, ?, ?, ?)
    """, (email, code, purpose, provider, expires))

    connection.commit()
    connection.close()

    # ---- Attempt to send the OTP by email ----
    sent = send_otp_email(email, code, purpose)

    if sent:
        print(f"[Nexora] OTP sent to {email}")
    else:
        # Only fall back to terminal if the send genuinely failed
        print(f"[Nexora] Send failed — falling back to terminal")
        print(f"[Nexora OTP FALLBACK] {purpose} for {email}: {code}")

    return code


def verify_otp(email, code, purpose):
    """Return True if `code` is valid for this email+purpose."""
    connection = get_db()
    row = connection.execute("""
        SELECT id, expires_at
        FROM otp_codes
        WHERE email = ? AND code = ? AND purpose = ? AND used = 0
        ORDER BY id DESC
        LIMIT 1
    """, (email, code, purpose)).fetchone()

    if not row:
        connection.close()
        return False

    # Expired?
    try:
        exp = datetime.strptime(row["expires_at"], "%Y-%m-%d %H:%M:%S")
        if exp < datetime.utcnow():
            connection.close()
            return False
    except Exception:
        connection.close()
        return False

    # Mark as used
    connection.execute("UPDATE otp_codes SET used = 1 WHERE id = ?", (row["id"],))
    connection.commit()
    connection.close()
    return True


def user_exists(email):
    connection = get_db()
    row = connection.execute(
        "SELECT id, username FROM users WHERE email = ?", (email,)
    ).fetchone()
    connection.close()
    return row
@app.route("/")
def index():
    # Splash plays once per browser session. If the user has already
    # seen it, go straight to the landing page.
    
    return render_template("splash.html")


@app.route("/landing")
def landing():
    session["splash_done"] = True
    return render_template("home.html")
# ============================================================
# MARKETING PAGES
# ============================================================

@app.route("/features")
def features():
    return render_template("features.html")


@app.route("/community")
def community():
    return render_template("community.html")


@app.route("/docs")
def docs():
    return render_template("docs.html")


@app.route("/about")
def about():
    return render_template("about.html")


# ============================================================
# LOGIN
# ============================================================

# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip().lower()
        password   = request.form.get("password", "")

        if not identifier or not password:
            flash("Please enter both username/email and password.", "error")
            return render_template("login.html")

        connection = get_db()
        user = connection.execute("""
            SELECT * FROM users
            WHERE LOWER(email) = ? OR LOWER(username) = ?
        """, (identifier, identifier)).fetchone()
        connection.close()

        if not user:
            flash("No account found with that username or email.", "error")
            return render_template("login.html")

        if user["provider"] == "google":
            flash("This account uses Google sign-in. Click "
                  "'Continue with Google'.", "error")
            return render_template("login.html")

        if not check_password_hash(user["password_hash"], password):
            flash("Incorrect password.", "error")
            return render_template("login.html")

        # Success
        session["user_id"]  = user["id"]
        session["username"] = user["username"]
        session["email"]    = user["email"]
        return redirect(url_for("launch_editor"))

    return render_template("login.html")
# ============================================================
# GOOGLE LOGIN / REGISTER (single flow — same entry)
# ============================================================

@app.route("/auth/google", methods=["POST"])
def auth_google():
    """
    Called when the user clicks 'Continue with Google'.
    Step 1: collect email. Step 2: OTP.
    """
    email = request.form.get("email", "").strip().lower()

    if not email or "@" not in email:
        flash("Please enter a valid Google email.", "error")
        return render_template("google_email.html")

    # Already a user? → OTP + login
    # New user?      → OTP + register (with full onboarding)
    purpose = "login" if user_exists(email) else "register"

    store_otp(email, purpose, "google")

    # Keep this email in session so the verify page can find it
    session["pending_email"]    = email
    session["pending_purpose"]  = purpose
    session["pending_provider"] = "google"

    return redirect(url_for("verify_otp_page"))


@app.route("/auth/google/email")
def google_email_page():
    return render_template("google_email.html")


@app.route("/auth/verify", methods=["GET", "POST"])
def verify_otp_page():
    email = session.get("pending_email")
    if not email:
        return redirect(url_for("login"))

    if request.method == "POST":
        code    = request.form.get("code", "").strip()
        purpose = session.get("pending_purpose")     # ← reads the session

        if verify_otp(email, code, purpose):
            connection = get_db()
            connection.execute("""
                UPDATE users SET verified_at = CURRENT_TIMESTAMP
                WHERE email = ?
            """, (email,))
            connection.commit()
            connection.close()

            if purpose == "login":
                # Existing user — sign in and go to editor
                connection = get_db()
                user = connection.execute(
                    "SELECT * FROM users WHERE email = ?", (email,)
                ).fetchone()
                connection.close()

                session["user_id"]  = user["id"]
                session["username"] = user["username"]
                session["email"]    = user["email"]
                return redirect(url_for("launch_editor"))

            else:
                # New user → collect personal details on the Welcome page
                return redirect(url_for("welcome"))

        flash("Invalid or expired code. Try again.", "error")

    return render_template("verify_otp.html", email=email)

# ============================================================
# REGISTER
# ============================================================

# ============================================================
# REGISTER (email + password + confirm)
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        # Validate
        if not username or not email or not password or not confirm:
            flash("Please fill in all fields.", "error")
            return render_template("register.html")

        if len(username) < 3:
            flash("Username must be at least 3 characters.", "error")
            return render_template("register.html")

        if "@" not in email or "." not in email:
            flash("Please enter a valid email.", "error")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        # Already taken?
        connection = get_db()
        existing = connection.execute(
            "SELECT id FROM users WHERE LOWER(email) = ? OR LOWER(username) = ?",
            (email, username)
        ).fetchone()
        connection.close()

        if existing:
            flash("Email or username already taken.", "error")
            return render_template("register.html")

        # Don't create the user yet — first verify email with OTP.
        # But stash the signup details in the session.
        session["pending_username"] = username
        session["pending_email"]    = email
        session["pending_password"] = password
        session["pending_purpose"]  = "register"
        session["pending_provider"] = "local"

        # OTP
        store_otp(email, "register", "local")

        return redirect(url_for("verify_otp_page"))

    return render_template("register.html")
# ============================================================
# WELCOME — after OTP verification
# ============================================================


@app.route("/welcome", methods=["GET", "POST"])
def welcome():
    email = session.get("pending_email")
    if not email:
        return redirect(url_for("register"))

    provider = session.get("pending_provider", "local")

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        age_str   = request.form.get("age", "").strip()
        country   = request.form.get("country", "").strip()
        bio       = request.form.get("bio", "").strip()

        # Google flow collects username + password here too
        username  = request.form.get("username", "").strip()
        password  = request.form.get("password", "")

        if not full_name:
            flash("Please enter your full name.", "error")
            return render_template("welcome.html",
                                   email=email, provider=provider)

        if provider == "google":
            if not username or len(username) < 3:
                flash("Username must be at least 3 characters.", "error")
                return render_template("welcome.html",
                                       email=email, provider=provider)

            if not password or len(password) < 8:
                flash("Password must be at least 8 characters.", "error")
                return render_template("welcome.html",
                                       email=email, provider=provider)

            # Check username availability
            connection = get_db()
            taken = connection.execute(
                "SELECT id FROM users WHERE LOWER(username) = ?",
                (username.lower(),)
            ).fetchone()
            connection.close()

            if taken:
                flash("That username is taken.", "error")
                return render_template("welcome.html",
                                       email=email, provider=provider)

            password_hash = generate_password_hash(password)
        else:
            # Local flow — username and password were set in register()
            username      = session.get("pending_username")
            password_hash = generate_password_hash(
                session.get("pending_password")
            )

        try:
            age = int(age_str) if age_str else None
        except ValueError:
            age = None

        # Insert the new user
        connection = get_db()
        connection.execute("""
            INSERT INTO users
                (username, email, password_hash, provider,
                 full_name, age, country, bio, verified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (username, email, password_hash, provider,
              full_name, age, country, bio))
        connection.commit()

        user = connection.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        connection.close()

        # Sign the user in
        session["user_id"]  = user["id"]
        session["username"] = user["username"]
        session["email"]    = user["email"]

        # Clear pending signup state
        for key in ("pending_email", "pending_username", "pending_password",
                    "pending_purpose", "pending_provider"):
            session.pop(key, None)

        # Now launch the editor
        return redirect(url_for("launch_editor"))

    return render_template("welcome.html", email=email, provider=provider)

# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    # --------------------------------------------------------
    # User must be logged in
    # --------------------------------------------------------

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    # --------------------------------------------------------
    # Show dashboard
    # --------------------------------------------------------

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        email=session.get("email")
    )


# ============================================================
# LOGOUT
# ============================================================
# ============================================================
# LAUNCH THE C++ EDITOR
# ============================================================

import subprocess
import sys
import os

NEXORA_EXE = r"C:\gameEngine\build\Debug\Nexora.exe"


@app.route("/launch")
def launch_editor():
    """
    Launch the compiled Nexora desktop editor
    after successful authentication.
    """

    if "user_id" not in session:
        return redirect(url_for("login"))

    username = str(session.get("username", "guest"))

    if os.getenv("NEXORA_DESKTOP_ENABLED", "false").lower() != "true":
        return render_template(
            "launch.html",
            username=username,
            launch_error=(
                "Nexora web deployment is running. "
                "Desktop engine integration is coming in Phase 2."
            )
        )

    exe_path = find_nexora_exe()

    if exe_path is None:
        expected = [
            str(PROJECT_ROOT / "build" / "Release" / "Nexora.exe"),
            str(PROJECT_ROOT / "build" / "Debug" / "Nexora.exe"),
        ]

        message = (
            "Login succeeded, but Nexora.exe was not found. "
            "Build the C++ project first. Checked: " + " | ".join(expected)
        )

        print("[launch] " + message)

        return render_template(
            "launch.html",
            username=username,
            launch_error=message
        )

    # Keep the remaining original executable-launching code here.

@app.route("/logout")
def logout():

    # Clear session
    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    init_database()

    app.run(
        debug=False,
        use_reloader=False,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000"))
    )