from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json, os
from datetime import datetime
from twilio.rest import Client

app = Flask(__name__)
app.secret_key = "college_fee_payment_secret"

BASE_DIR = os.path.join(os.path.dirname(__file__), "database")
USERS_FILE = os.path.join(BASE_DIR, "users.json")
PAYMENTS_FILE = os.path.join(BASE_DIR, "payments.json")
PENDING_FILE = os.path.join(BASE_DIR, "pending_transactions.json")


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

# ---------- SMS WITH TWILIO ----------
def send_sms(mobile, message):
    # Get Twilio credentials from environment variables
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_number = os.environ.get('TWILIO_PHONE_NUMBER')
    
    # If credentials are not set, fall back to simulation
    if not all([account_sid, auth_token, twilio_number]):
        print(f"\n[SMS SIMULATION] Sending to {mobile}: {message}\n")
        print("[INFO] Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER to enable real SMS\n")
        return
    
    try:
        client = Client(account_sid, auth_token)
        sms = client.messages.create(
            body=message,
            from_=twilio_number,
            to=mobile
        )
        print(f"\n[SMS SENT] Message SID: {sms.sid} to {mobile}\n")
    except Exception as e:
        print(f"\n[SMS ERROR] Failed to send SMS: {str(e)}\n")
        print(f"[SMS SIMULATION] Would have sent to {mobile}: {message}\n")

# ---------- PAYMENT ----------
@app.route("/payment", methods=["GET", "POST"])
def payment():
    # Check if session data exists
    if "student" not in session or "amount" not in session.get("student", {}):
        return redirect(url_for("enter_details"))

    if request.method == "POST":
        session["payment_mode"] = request.form["mode"]
        
        # Generate Reference
        ref = "SB" + datetime.now().strftime("%Y%m%d%H%M%S")
        session["ref"] = ref
        
        # Simplified Flow: Save directly as SUCCESS
        payments = load_json(PAYMENTS_FILE)
        payments[ref] = {
            "ref": ref,
            "date": datetime.now().strftime("%d-%m-%Y"),
            "college": session.get("college", "PBR VITS"),
            "student": session["student"], # Contains student_name, amount etc
            "mode": request.form["mode"],
            "amount": session["student"]["amount"],
            "status": "SUCCESS"
        }
        save_json(PAYMENTS_FILE, payments)
        
        # Also add to pending just in case, but mark SUCCESS
        pending = load_json(PENDING_FILE)
        pending[ref] = {
            "ref": ref,
            "amount": session["student"]["amount"],
            "student": session["student"]["student_name"],
            "status": "SUCCESS",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        save_json(PENDING_FILE, pending)
        
        # Redirect directly to receipt
        return redirect(url_for("receipt"))
                               
    return render_template("payment.html",
                           amount=session["student"]["amount"],
                           ref=session.get("ref", ""))


# ---------- POLLING & BANK ADMIN ----------

@app.route("/check_status/<ref>")
def check_status(ref):
    print(f"DEBUG: Checking status for {ref}")
    
    # Check pending transactions file
    pending = load_json(PENDING_FILE)
    if ref in pending:
        status = pending[ref]["status"]
        print(f"DEBUG: Found in pending file. Status: {status}")
        return jsonify({"status": status})
    
    # Check payments.json for completed
    payments = load_json(PAYMENTS_FILE)
    if ref in payments:
         print(f"DEBUG: Found in payments.json. Status: SUCCESS")
         return jsonify({"status": "SUCCESS"})
    
    print(f"DEBUG: Not found. Status: UNKNOWN")
    return jsonify({"status": "UNKNOWN"})

@app.route("/bank_admin")
def bank_admin():
    # Show only PENDING transactions from file
    all_pending = load_json(PENDING_FILE)
    pending = {k: v for k, v in all_pending.items() if v.get("status") == "PENDING"}
    return render_template("bank_admin.html", transactions=pending)

@app.route("/approve_payment/<ref>")
def approve_payment(ref):
    pending = load_json(PENDING_FILE)
    
    if ref in pending:
        # Update status to SUCCESS
        pending[ref]["status"] = "SUCCESS"
        save_json(PENDING_FILE, pending)
        
        # Save to permanent storage
        payments = load_json(PAYMENTS_FILE)
        data = {
            "ref": ref,
            "date": datetime.now().strftime("%d-%m-%Y"),
            "college": "PBR VITS",
            "student": {"student_name": pending[ref]["student"]},
            "mode": "UPI (Approved)",
            "amount": pending[ref]["amount"]
        }
        payments[ref] = data
        save_json(PAYMENTS_FILE, payments)
        
    return redirect(url_for("bank_admin"))

# ---------- RECEIPT ----------
@app.route("/receipt")
def receipt():
    # Only show if confirmed? Or just show data from session/file
    ref = session.get("ref")
    payments = load_json(PAYMENTS_FILE)
    
    data = {}
    if ref and ref in payments:
        data = payments[ref]
    else:
        # Fallback if accessed directly or before polling finished (shouldn't happen in flow)
        student_data = session.get("student", {})
        data = {
            "ref": ref or "N/A",
            "date": datetime.now().strftime("%d-%m-%Y"),
            "college": session.get("college", "PBR VITS"),
            "student": {
                "student_name": student_data.get("student_name", "N/A"),
                "amount": student_data.get("amount", "0"),
                "remarks": student_data.get("remarks", "")
            },
            "mode": session.get("payment_mode", "N/A")
        }

    return render_template("receipt.html", data=data)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)