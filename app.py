from flask import Flask, render_template
import os
import random

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("main.html")

@app.route("/login")
def index():
    return render_template("login.html")

@app.route("/register")
def index():
    return render_template("register.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))