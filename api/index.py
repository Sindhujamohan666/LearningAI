from flask import Flask, jsonify, render_template

app = Flask(__name__, template_folder=".")

@app.route("/")
def index():
    return render_template("architecture.html")

@app.route("/api")
def api_index():
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
