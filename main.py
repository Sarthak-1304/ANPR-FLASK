from flask import Flask, request, render_template, redirect, url_for, flash, session
import os
import mysql.connector
from anpr import process_image
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'CHANGE_ME'

# ---------------- USERS ----------------
USERS = {
    "siddharth": "sid@12",
    "vaibhav": "vaibhav@12",
    "sarthak": "sarthak@12"
}

# ---------------- FOLDERS ----------------
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ---------------- DATABASE ----------------
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_DB_PASSWORD",
        database="anpr"
    )
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_info (
            id INT AUTO_INCREMENT PRIMARY KEY,
            plate VARCHAR(20) UNIQUE,
            name VARCHAR(100),
            phone VARCHAR(15)
        )
    """)
    conn.commit()
except mysql.connector.Error as err:
    print("Database Error:", err)

# ---------------- AUTH DECORATOR ----------------
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            flash("Please login first")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ---------------- ROUTES ----------------
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip().lower()
        password = request.form['password']

        if username in USERS and USERS[username] == password:
            session['username'] = username
            flash("Login successful")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out")
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    cursor.execute("SELECT COUNT(*) FROM vehicle_info")
    total_vehicles = cursor.fetchone()[0]
    return render_template('dashboard.html', total_vehicles=total_vehicles)

# ---------------- UPLOAD + ANPR ----------------
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':

        if 'file' not in request.files:
            flash("No file uploaded")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("No file selected")
            return redirect(request.url)

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # ---- LIMIT IMAGE SIZE (PREVENT CRASH) ----
        try:
            img = Image.open(file_path)
            img.thumbnail((1024, 1024))
            img.save(file_path)
        except Exception as e:
            print("Image resize error:", e)

        # ---- SAFE ANPR CALL ----
        try:
            plate_number = process_image(file_path)
        except Exception as e:
            print("ANPR Error:", e)
            flash("Error processing image. Try another image.")
            return redirect(request.url)

        if plate_number:
            cursor.execute(
                "SELECT * FROM vehicle_info WHERE plate = %s",
                (plate_number,)
            )
            record = cursor.fetchone()

            if record:
                flash(f"Vehicle Found | Plate: {record[1]}, Owner: {record[2]}, Phone: {record[3]}")
                return redirect(url_for('vehicles'))
            else:
                cursor.execute(
                    "INSERT INTO vehicle_info (plate) VALUES (%s)",
                    (plate_number,)
                )
                conn.commit()
                return redirect(url_for('register', plate=plate_number))
        else:
            flash("Number plate not detected")

    return render_template('upload.html')   

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    plate = request.args.get('plate')

    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']

        cursor.execute(
            "UPDATE vehicle_info SET name=%s, phone=%s WHERE plate=%s",
            (name, phone, plate)
        )
        conn.commit()

        flash("Vehicle registered successfully")
        return redirect(url_for('vehicles'))

    return render_template('register.html', plate=plate)

# ---------------- VIEW VEHICLES ----------------
@app.route('/vehicles')
@login_required
def vehicles():
    cursor.execute("SELECT * FROM vehicle_info")
    records = cursor.fetchall()
    return render_template('vehicles.html', records=records)

# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=False)
