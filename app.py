from flask import Flask, render_template, request, jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from recommendation import target
import random
import time
import sqlite3
import datetime
import smtplib
import os 

app = Flask(__name__)

pending_users = {}
registered_users = {}
conn = sqlite3.connect("fintraclai.db")
cur = conn.cursor()
cur.execute("select * from user")
x = cur.fetchall()
reg = []
for i in x:
    reg.append(i[3].lower())

OTP_EXPIRY_SECONDS = 300  # 5 minutes


def generate_otp():
    return str(random.randint(1000, 9999))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/signup")
def signup_page():
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        user_email = request.form.get("email", "").strip()
        user_password = request.form.get("password", "").strip()

        # Check email first
        conn = sqlite3.connect('fintraclai.db')
        cur = conn.cursor()
        cur.execute("SELECT EMAIL,PASSWORD_HASH FROM USER")
        x = dict(cur.fetchall())

        if user_email in x:
            # Check hashed password
            if check_password_hash(x[user_email], user_password):
                return render_template("dashboard.html", user_email=user_email)
            else:
                error = "Invalid password."
        else:
            error = "Invalid email."

    return render_template("login.html", error=error)

@app.route("/income", methods=["GET", "POST"])
def income():
    if request.method == "GET":
        return render_template("income.html")

    email = request.form.get("email", "").strip()
    income_type = request.form.get("income_type", "").strip()
    monthly_income = request.form.get("monthly_income", "").strip()
    additional_income_type = request.form.get("additional_income_type", "").strip()
    additional_monthly_income = request.form.get("additional_monthly_income", "").strip()
    dependants = request.form.get("dependants", "").strip()

    conn = sqlite3.connect('fintraclai.db')
    cur = conn.cursor()
    cur.execute("SELECT EMAIL,PASSWORD_HASH FROM USER")
    x = dict(cur.fetchall())

    if email not in x:
        return render_template("income.html", error="Email is required.")

    try:

        # Assumption: USER table contains EMAIL column
        cur.execute("SELECT USER_ID FROM USER WHERE EMAIL = ?", (email,))
        user_row = cur.fetchone()

        if not user_row:
            conn.close()
            return render_template("income.html", error="No user found with this email.")

        user_id = user_row[0]
        now = datetime.datetime.now()
        profile_id = cur.execute("SELECT max(PROFILE_ID) FROM INCOMEPROFILE")
        x = cur.fetchall()
        if x[0][0]==None:
            x = 1
        else:
            x = x[0][0]+1

        cur.execute("""
            INSERT INTO INCOMEPROFILE (
                PROFILE_ID,
                USER_ID,
                INCOME_TYPE,
                MONTHLY_INCOME,
                ADDITIONAL_INCOME_TYPE,
                ADDITIONAL_MONTHLY_INCOME,
                DEPENDANTS,
                CREATED_AT,
                UPDATED_AT
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            int(x),
            int(user_id),
            income_type,
            float(monthly_income),
            additional_income_type,
            float(additional_monthly_income),
            int(dependants),
            now,
            now
        ))

        conn.commit()
        conn.close()

        return render_template("income.html", success="Income profile saved successfully.")

    except sqlite3.IntegrityError as e:
        return render_template("income.html", error=f"Database integrity error: {str(e)}")

    except Exception as e:
        return render_template("income.html", error=f"Error: {str(e)}")
    
@app.route("/expense", methods=["GET", "POST"])
def expense():
    if request.method == "GET":
        return render_template("expense.html")

    email = request.form.get("email", "").strip()
    groceries = request.form.get("groceries", "").strip()
    travel = request.form.get("travel", "").strip()
    medfit = request.form.get("medfit", "").strip()
    lep = request.form.get("lep", "").strip()
    monthly_rent = request.form.get("monthly_rent", "").strip()
    m_bills = request.form.get("m_bills", "").strip()
    fashion = request.form.get("fashion", "").strip()
    entertainment = request.form.get("entertainment", "").strip()
    education = request.form.get("education", "").strip()
    emsaving = request.form.get("emsaving", "").strip()
    miscellaneous = request.form.get("miscellaneous", "").strip()

    if not email:
        return render_template("expense.html", error="Email is required.")

    try:
        conn = sqlite3.connect("fintraclai.db")
        cur = conn.cursor()

        cur.execute("SELECT USER_ID FROM USER WHERE EMAIL = ?", (email,))
        user_row = cur.fetchone()

        if not user_row:
            conn.close()
            return render_template("expense.html", error="No user found with this email.")

        user_id = user_row[0]
        expense_id = cur.execute("SELECT max(expense_ID) FROM expensePROFILE")
        x = cur.fetchall()
        if x[0][0]==None:
            x = 1
        else:
            x = x[0][0]+1

        print(x,user_id,email,groceries,travel,medfit,lep,monthly_rent,m_bills,fashion,entertainment,education,emsaving,miscellaneous)
        cur.execute("""
            INSERT INTO EXPENSEPROFILE (
                Expense_ID,
                USER_ID,
                GROCERIES,
                TRAVEL,
                MEDFIT,
                LEP,
                MONTHLY_RENT,
                M_BILLS,
                FASHION,
                ENTERTAINMENT,
                EDUCATION,
                EMSAVING,
                MISCELLANEOUS,
                CREATED_AT
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
        """, (
            x,
            int(user_id),
            float(groceries),
            float(travel),
            float(medfit),
            float(lep),
            float(monthly_rent),
            float(m_bills),
            float(fashion),
            float(entertainment),
            float(education),
            float(emsaving),
            float(miscellaneous),
            datetime.datetime.now()
        ))

        conn.commit()
        conn.close()

        return render_template("expense.html", success="Expense profile saved successfully.")

    except sqlite3.IntegrityError as e:
        return render_template("expense.html", error=f"Database integrity error: {str(e)}")
    except ValueError:
        return render_template("expense.html", error="Please enter valid numeric values in all amount fields.")
    except Exception as e:
        return render_template("expense.html", error=f"Error: {str(e)}")
    
@app.route("/goals", methods=["GET", "POST"])
def goals():
    if request.method == "GET":
        return render_template("goals.html")

    try:
        email = request.form.get("email", "").strip()
        goal_name = request.form.get("goal_name", "").strip()
        goal_amount = request.form.get("goal_amount", "").strip()
        start_date = request.form.get("start_date", "").strip()
        end_date = request.form.get("end_date", "").strip()
        goal_status = request.form.get("goal_status", "").strip()

        if not email or not goal_name or not goal_amount or not start_date or not end_date or not goal_status:
            return jsonify({"success": False, "error": "All fields are required."})

        goal_amount = float(goal_amount)



        # Calculate duration in months
       

        ob = target(email)
        res = ob.monthly_target(goal_amount)


        monthly_target = res[0]
        duration_in_month = res[1]

        conn = sqlite3.connect("fintraclai.db")
        cur = conn.cursor()

        cur.execute("SELECT USER_ID FROM USER WHERE EMAIL = ?", (email,))
        user = cur.fetchone()

        if not user:
            conn.close()
            return jsonify({"success": False, "error": "User not found."})

        user_id = user[0]

        # Generate GOALID
        goal_id = random.randint(10000, 99999)

        # Optional: avoid duplicate GOALID
        while True:
            cur.execute("SELECT 1 FROM GOALS WHERE GOALID = ?", (goal_id,))
            existing = cur.fetchone()
            if not existing:
                break
            goal_id = random.randint(10000, 99999)

        now = datetime.datetime.now()

        cur.execute("""
            INSERT INTO GOALS (
                GOALID,
                USER_ID,
                GOAL_NAME,
                START_DATE,
                END_DATE,
                GOAL_AMOUNT,
                MONTHLY_SAVING_T,
                GOAL_STATUS,
                CREATED_AT,
                UPDATED_AT
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            goal_id,
            user_id,
            goal_name,
            start_date,
            end_date,
            goal_amount,
            monthly_target,
            goal_status,
            now,
            now
        ))

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "monthlytarget": monthly_target,
            "durationinmonth": duration_in_month
        })

    except ValueError:
        return jsonify({"success": False, "error": "Please enter valid numeric values and valid dates."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/send-otp", methods=["POST"])
def send_otp():
    try:
        import requests as http_requests
        import random, time

        data = request.get_json()
        name     = data.get("name", "").strip()
        email    = data.get("email", "").strip()
        gender   = data.get("gender")
        password = data.get("password")

        if not name or not email:
            return jsonify({"message": "Name and email required"}), 400

        otp = str(random.randint(1000, 9999))

        pending_users[email] = {
            "name": name,
            "gender": gender,
            "email": email,
            "password": password,
            "otp": otp,
            "expires_at": time.time() + OTP_EXPIRY_SECONDS
        }

        api_key = os.environ.get("BREVO_API_KEY")
        if not api_key:
            return jsonify({"message": "Email service not configured"}), 500

        response = http_requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": api_key,
                "Content-Type": "application/json"
            },
            json={
                "sender": {"name": "FinTrack AI", "email": "suryatejau55794@gmail.com"},
                "to": [{"email": email, "name": name}],
                "subject": "Your FinTrack AI OTP Code",
                "htmlContent": f"""
                    <div style="font-family:sans-serif;max-width:400px;margin:auto;padding:32px;
                                background:#0a0820;color:#ede8ff;border-radius:16px;">
                        <h2 style="color:#a78bfa">FinTrack AI</h2>
                        <p>Hi <strong>{name}</strong>, your OTP verification code is:</p>
                        <h1 style="font-size:3rem;letter-spacing:12px;color:#7c3aed;
                                   text-align:center;padding:16px 0">{otp}</h1>
                        <p style="color:#9d8ec4">This code expires in 5 minutes.<br/>
                        If you did not request this, ignore this email.</p>
                    </div>
                """
            },
            timeout=10
        )

        if response.status_code not in [200, 201]:
            print("BREVO API ERROR:", response.text)
            return jsonify({"message": "Failed to send OTP. Try again."}), 500

        print("OTP EMAIL SENT SUCCESSFULLY via Brevo API")
        return jsonify({"message": "OTP sent successfully"}), 200

    except Exception as e:
        print("SEND-OTP ERROR:", str(e))
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    try:
        data = request.get_json()

        email = data.get("email", "").strip().lower()
        otp = data.get("otp", "").strip()

        if not email or not otp:
            return jsonify({"success": False, "message": "Email and OTP are required."}), 400

        if email not in pending_users:
            return jsonify({"success": False, "message": "No pending signup found for this email."}), 400

        user_data = pending_users[email]

        if time.time() > user_data["expires_at"]:
            del pending_users[email]
            return jsonify({"success": False, "message": "OTP expired. Please sign up again."}), 400

        if otp != user_data["otp"]:
            return jsonify({"success": False, "message": "Incorrect OTP. User not registered."}), 400

        hashed_password = generate_password_hash(user_data["password"])

        registered_users[email] = {
            "name": user_data["name"],
            "email": user_data["email"],
            "gender": user_data["gender"],
            "password": hashed_password,
            "registered_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        print(registered_users)
        conn = sqlite3.connect("fintraclai.db")
        cur = conn.cursor()
        cur.execute("select max(user_id) from user")
        x1 = cur.fetchall()
        cur.execute(f'''
            INSERT INTO USER VALUES({x1[0][0]+1},"{registered_users[email]['name']}",
            "{registered_users[email]['gender']}","{registered_users[email]['email']}",
            "{registered_users[email]['password']}","{datetime.datetime.now()}")
            ''')
        conn.commit()
        
        print(pending_users)
        cur.execute("select max(otp_id) from VERIFICATION")
        x2 = cur.fetchall()
        cur.execute(f'''
            INSERT INTO VERIFICATION VALUES({x2[0][0]+1},{x1[0][0]+1},
            {pending_users[email]['otp']},"{pending_users[email]['expires_at']}",
            "{datetime.datetime.now()}","verified")
            ''')
        conn.commit()

        del pending_users[email]

        return jsonify({
            "success": True,
            "message": "User registered successfully."
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


@app.route("/users", methods=["GET"])
def users():
    return jsonify({
        "success": True,
        "registered_users": registered_users
    }), 200


if __name__ == "__main__":
    app.run(debug=True,host = "0.0.0.0",port = 5050)