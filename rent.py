from flask import Flask, render_template, request, redirect, session
import pymysql
import os

app = Flask(__name__)
app.secret_key = "kashif_secret_key"

# ___________________________________
# DATABASE CONNECTION

def get_db_connection():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",        # XAMPP default password blank
        database="rentcar_db",
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

# =========================
# HOME
# =========================
@app.route("/")
def index():
    return render_template("index.html")

# ============================
# USER SIGNUP
# ============================
@app.route("/signup_user", methods=["GET","POST"])
def signup_user():
    if request.method=="POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name,email,password,phone) VALUES (%s,%s,%s,%s)",
                    (name,email,password,phone))
        conn.commit()
        conn.close()
        return redirect("/login_user")
    return render_template("usersignup.html")

# ============================
# OWNER SIGNUP
# ============================
@app.route("/signup_owner", methods=["GET","POST"])
def signup_owner():
    if request.method=="POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO owners (name,email,password,phone) VALUES (%s,%s,%s,%s)",
                    (name,email,password,phone))
        conn.commit()
        conn.close()
        return redirect("/login_owner")
    return render_template("ownersignup.html")

# ============================
# USER LOGIN
# ============================
@app.route("/login_user", methods=["GET","POST"])
def login_user():
    if request.method=="POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email=%s AND password=%s",(email,password))
        user = cur.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            return redirect("/user_home")
        else:
            return "Invalid Login"
    return render_template("userlogin.html")

# ============================
# OWNER LOGIN
# ============================
@app.route("/login_owner", methods=["GET","POST"])
def login_owner():
    if request.method=="POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM owners WHERE email=%s AND password=%s",(email,password))
        owner = cur.fetchone()
        conn.close()

        if owner:
            session["owner_id"] = owner["id"]
            return redirect("/owner_home")
        else:
            return "Invalid Login"
    return render_template("ownerlogin.html")

# ============================
# USER HOME
# ============================
@app.route("/user_home")
def user_home():
    if "user_id" not in session:
        return redirect("/login_user")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cars ORDER BY car_id DESC")   # نئی گاڑیاں اوپر
    cars = cur.fetchall()
    conn.close()

    return render_template("userhome.html", cars=cars)

# ============================
# VIEW CARS
# ============================
@app.route("/view_cars")
def view_cars():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cars")
    cars = cur.fetchall()
    conn.close()
    return render_template("carlist.html", cars=cars)

# __________________________________
# CAR DETAILS

@app.route("/car/<int:car_id>")
def car_details(car_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cars WHERE car_id=%s",(car_id,))
    car = cur.fetchone()
    conn.close()
    return render_template("cardetail.html", car=car)

# ______________________________
# RENT CAR kily 

@app.route("/rent/<int:car_id>", methods=["GET","POST"])
def rent_car(car_id):
    if "user_id" not in session:
        return redirect("/login_user")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cars WHERE car_id=%s",(car_id,))
    car = cur.fetchone()

    if request.method=="POST":
        from_date = request.form["date_from"]
        to_date = request.form["date_to"]
        driver = request.form["driver"]
        user_id = session["user_id"]

        cur.execute("INSERT INTO bookings (user_id, car_id, from_date, to_date, driver) VALUES (%s,%s,%s,%s,%s)",
                    (user_id,car_id,from_date,to_date,driver))
        conn.commit()
        conn.close()
        return render_template("confirmbooking.html")
    conn.close()
    return render_template("rentcar.html", car=car)

# OWNER HOME
@app.route("/owner_home")
def owner_home():
    if "owner_id" not in session:
        return redirect("/login_owner")
    return render_template("ownerhome.html")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login_user")

# ============================
# ADD CAR (OWNER)
# ============================
@app.route("/add_car", methods=["GET","POST"])
def add_car():
    if "owner_id" not in session:
        return redirect("/login_owner")
    if request.method=="POST":
        car_name = request.form["car_name"]
        model = request.form["model"]
        price = request.form["price"]
        description = request.form["description"]

        image = request.files["image"]
        filename = image.filename
        image.save(os.path.join("static/car_images", filename))

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO cars (owner_id,car_name,model,price,image,description) VALUES (%s,%s,%s,%s,%s,%s)",
                    (session["owner_id"],car_name,model,price,filename,description))
        conn.commit()
        conn.close()
        return redirect("/owner_home")
    return render_template("addcar.html")

# ============================
# MY CARS (OWNER)
# ============================
@app.route("/my_cars")
def my_cars():
    if "owner_id" not in session:
        return redirect("/login_owner")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cars WHERE owner_id=%s",(session["owner_id"],))
    cars = cur.fetchall()
    conn.close()
    return render_template("mycar.html", cars=cars)


# ============================
# RUN SERVER
# ============================
if __name__=="__main__":
    if not os.path.exists("static/car_images"):
        os.makedirs("static/car_images")
    app.run(debug=True, port=5001)