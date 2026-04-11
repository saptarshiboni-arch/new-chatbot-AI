from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from medibot import get_response
import traceback
import os

print("App file started")

app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": "*"}})

# Store chat history
chat_history = []


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    import traceback
    try:
        data = request.get_json(force=True)
        print("Incoming:", data)

        user_msg = data.get("message", "")

        reply = get_response(user_msg)
        print("Reply:", reply)

        return jsonify({
            "response": str(reply) if reply else "No response"
        })

    except Exception as e:
        error = traceback.format_exc()
        print("ERROR:", error)

        return jsonify({
            "response": "Backend error",
            "error": error
        })

# History page
@app.route("/history")
def history():
    return render_template("history.html", chats=chat_history)


# Clear history
@app.route("/clear_history")
def clear_history():
    global chat_history
    chat_history = []
    return "History cleared! <a href='/history'>Go back</a>"


# Run app (IMPORTANT FOR RENDER)
if __name__ == "__main__":
    print ("starting flask app...")
    app.run(host="0.0.0.0", port=10000)