from flask import Flask, render_template, request, session, redirect
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

from database import get_connection, create_table

app = Flask(__name__, template_folder="templates_new")

# Flask secret key
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Gemini AI
apikey = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=apikey)

# Create database table
try:
    create_table()
except Exception as e:
    print("DATABASE ERROR:", e)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if (
            username == os.getenv("ADMIN_USERNAME")
            and password == os.getenv("ADMIN_PASSWORD")
        ):
            session["admin_logged_in"] = True

            return redirect("/dashboard")

        else:
            return render_template(
                "login.html",
                error="Invalid username or password."
            )

    return render_template("login.html")


@app.route("/donate", methods=["POST"])
def donate():

    hotel = request.form.get("hotel")
    food = request.form.get("food")
    quantity = request.form.get("quantity")
    location = request.form.get("location")
    contact = request.form.get("contact")

    # Save donation to PostgreSQL database
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO donations
            (hotel, food, quantity, location, contact)
            VALUES (%s, %s, %s, %s, %s)
        """, (hotel, food, quantity, location, contact))

        connection.commit()

        cursor.close()
        connection.close()

    except Exception as e:
        print("DATABASE ERROR:", e)

        return """
        <h2>Unable to submit donation.</h2>
        <p>Please check the database connection.</p>
        <a href="/">← Back to FoodConnect</a>
        """

    # AI prompt
    prompt = f"""
You are an AI assistant for FoodConnect, a food waste management
website that connects hotels with nearby orphanages.

A hotel has the following leftover food:

Hotel: {hotel}
Food: {food}
Quantity: {quantity}
Location: {location}

Give a short and simple recommendation about donating this food.
Mention that the food should be safe, fresh, properly stored,
and suitable for human consumption before donation.

Keep the response within 3 to 4 sentences.
"""

    # Gemini AI
    try:

        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt
        )

        ai_response = interaction.output_text

    except Exception as e:

        print("GEMINI ERROR:", e)

        ai_response = (
            "AI recommendation is currently unavailable. "
            "Please check the server logs for the Gemini error."
        )

    # Donation result page
    return f"""
<!DOCTYPE html>
<html>

<head>

    <title>Food Donation Submitted</title>

    <style>

        body {{
            font-family: Arial, sans-serif;
            background: #f0f8f0;
            text-align: center;
            padding: 40px;
        }}

        .box {{
            background: white;
            max-width: 700px;
            margin: auto;
            padding: 35px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }}

        h1 {{
            color: #2e7d32;
            margin-bottom: 25px;
        }}

        h2 {{
            color: #1b5e20;
            margin-top: 30px;
        }}

        p {{
            font-size: 18px;
            margin: 12px;
        }}

        .ai-box {{
            background: #e8f5e9;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
            text-align: left;
            line-height: 1.6;
        }}

        .ai-title {{
            font-weight: bold;
            color: #2e7d32;
            font-size: 20px;
        }}

        a {{
            display: inline-block;
            margin-top: 25px;
            padding: 12px 25px;
            background: #2e7d32;
            color: white;
            text-decoration: none;
            border-radius: 8px;
        }}

    </style>

</head>

<body>

    <div class="box">

        <h1>✅ Food Donation Submitted!</h1>

        <p><b>Hotel:</b> {hotel}</p>

        <p><b>Food:</b> {food}</p>

        <p><b>Quantity:</b> {quantity}</p>

        <p><b>Location:</b> {location}</p>

        <p><b>Contact:</b> {contact}</p>

        <h2>🤖 AI Food Donation Assistant</h2>

        <div class="ai-box">

            <div class="ai-title">
                AI Recommendation
            </div>

            <p>
                {ai_response}
            </p>

        </div>

        <p>
            Thank you for helping reduce food waste! ❤️
        </p>

        <a href="/">
            ← Back to FoodConnect
        </a>

    </div>

</body>

</html>
"""


@app.route("/dashboard")
def dashboard():

    if not session.get("admin_logged_in"):
        return redirect("/login")

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT * FROM donations
            ORDER BY id DESC
        """)

        donations = cursor.fetchall()

        cursor.close()
        connection.close()

    except Exception as e:

        print("DATABASE ERROR:", e)

        return """
        <h2>Unable to load dashboard.</h2>
        <p>Please check the database connection.</p>
        <a href="/">← Back to FoodConnect</a>
        """

    total_meals = 0

    for donation in donations:

        quantity = donation[3]

        try:
            number = int(quantity.split()[0])
            total_meals += number

        except:
            pass

    return render_template(
        "dashboard.html",
        donations=donations,
        total_meals=total_meals
    )


@app.route("/logout")
def logout():

    session.pop("admin_logged_in", None)

    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)