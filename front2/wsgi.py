from app import app, init_database

# Initialize SQLite database
init_database()

# Health check for Kubernetes
@app.route("/healthz")
def healthz():
    return {"status": "ok"}, 200