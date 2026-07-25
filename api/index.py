from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({
        "name": "QABuddyAI",
        "version": "2.0",
        "status": "running",
        "description": "Multi-Agent AI QA Automation Assistant",
    })

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run()
