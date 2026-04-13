from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from medibot import get_response

import json
import os


app = Flask(__name__)
CORS(app)

# File to store history
HISTORY_FILE = "history.json"


# ✅ Save chat to file
def save_chat(user, bot):
    history = []

    # Load existing history
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                history = json.load(f)
            except:
                history = []

    # Add new chat
    history.append({
        "user": user,
        "bot": bot
    })

    # Save back
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    import traceback
    try:
        data = request.get_json(force=True)

        user_msg = data.get("message", "")

        print("Request Received")

        reply = get_response(user_msg)

        print("Reply ready")

        if not reply:
            reply = "Empty response from backend"

        # ✅ SAVE CHAT HERE
        save_chat(user_msg, reply)

        return jsonify({
            "response": str(reply)
        })

    except Exception as e:
        error = traceback.format_exc()
        print(error)

        return jsonify({
            "response": "Backend error",
            "error": error
        })


@app.route("/history")
def history():
    # ✅ Load history from file
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                data = json.load(f)
            except:
                data = []
    else:
        data = []

    return render_template("history.html", chats=data)




@app.route("/clear_history")
def clear_history():
    try:
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
    except Exception as e:
        return str(e)

    # ✅ redirect back to home (important)
    return redirect(url_for("home"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)