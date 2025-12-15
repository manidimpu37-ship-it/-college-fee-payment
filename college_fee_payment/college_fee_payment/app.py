from flask import Flask, render_template, request, redirect, url_for, session
import json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "college_fee_payment_secret"

BASE_DIR = os.path.join(os.path.dirname(__file__), "database")
USERS_FILE = os.path.join(BASE_DIR, "users.json")
PAYMENTS_FILE = os.path.join(BASE_DIR, "payments.json")


# ---------- UTIL ----------
def load_json(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    # Ensure directory exists
    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
def login():
    users = load_json(USERS_FILE)
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        if u in users and users[u]["password"] == p:
            session["user"] = u
            return redirect(url_for("select_payee"))
        return "Invalid Login"
    return render_template("login.html")


# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    users = load_json(USERS_FILE)
    if request.method == "POST":
        u = request.form["username"]
        users[u] = {
            "email": request.form["email"],
            "password": request.form["password"]
        }
        save_json(USERS_FILE, users)
        return redirect(url_for("login"))
    return render_template("register.html")


# ---------- SELECT PAYEE ----------
@app.route("/select_payee", methods=["GET", "POST"])
def select_payee():
    if request.method == "POST":
        session["college"] = request.form["college"]
        return redirect(url_for("enter_details"))
    return render_template("select_payee.html")


# ---------- ENTER DETAILS ----------
@app.route("/enter_details", methods=["GET", "POST"])
def enter_details():
    if request.method == "POST":
        session["student"] = dict(request.form)
        return redirect(url_for("verify"))
    return render_template("enter_details.html")


# ---------- VERIFY ----------
@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        return redirect(url_for("payment"))
    return render_template("verify.html",
                           college=session["college"],
                           student=session["student"])


# ---------- PAYMENT ----------
@app.route("/payment", methods=["GET", "POST"])
def payment():
    if request.method == "POST":
        session["payment_mode"] = request.form["mode"]
        session["ref"] = "SB" + datetime.now().strftime("%Y%m%d%H%M%S")
        return redirect(url_for("receipt"))
    return render_template("payment.html",
                           amount=session["student"]["amount"])


# ---------- RECEIPT ----------
@app.route("/receipt")
def receipt():
    payments = load_json(PAYMENTS_FILE)

    data = {
        "ref": session["ref"],
        "date": datetime.now().strftime("%d-%m-%Y"),
        "college": session["college"],
        "student": session["student"],
        "mode": session["payment_mode"]
    }

    payments[data["ref"]] = data
    save_json(PAYMENTS_FILE, payments)

    return render_template("receipt.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)