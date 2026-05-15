from flask import Flask, request, jsonify, send_from_directory
from c_syntax_checker import CSyntaxChecker
import os

BASE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE, "templates"))

@app.route("/")
def index():
    return send_from_directory(os.path.join(BASE, "templates"), "index.html")

@app.route("/check", methods=["POST"])
def check():
    data = request.get_json()
    code = data.get("code", "")
    checker = CSyntaxChecker()
    checker.check_content(code)
    return jsonify({"errors": checker.errors, "count": len(checker.errors)})

if __name__ == "__main__":
    print("✅  C Syntax Checker running → http://localhost:5050")
    app.run(debug=True, port=5050)
