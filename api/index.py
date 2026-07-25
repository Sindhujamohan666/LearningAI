from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("architecture.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api")
def api_info():
    return jsonify({
        "name": "QABuddyAI",
        "version": "2.0",
        "description": "Multi-Agent AI QA Automation Assistant",
        "endpoints": {
            "/": "Architecture diagram",
            "/health": "Health check",
            "/api": "API info"
        }
    })

if __name__ == "__main__":
    app.run()
