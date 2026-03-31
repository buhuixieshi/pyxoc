import os

from flask import Flask, jsonify, render_template, request

from main import Agent

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

app = Flask(__name__, template_folder="web")
agent = Agent()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/chat")
def chat():
    body = request.get_json(silent=True) or {}
    message = str(body.get("message", "")).strip()
    if not message:
        return jsonify({"error": "message 不能为空"}), 400

    try:
        reply = agent.chat(message)
    except Exception as exc:
        return jsonify({"error": f"服务内部错误: {exc}"}), 500

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
