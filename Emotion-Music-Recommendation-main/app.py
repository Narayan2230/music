from flask import Flask, render_template, Response, jsonify
import gunicorn
from camera import *
import pandas as pd
import os
from flask import Flask, render_template, request, redirect, session, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import re


app = Flask(__name__)
app.secret_key = '3232'


# Database Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Change to your MySQL password
app.config['MYSQL_DB'] = 'db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

headings = ("Name", "Album", "Artist", "URL")

# Assuming music_rec() fetches your music data; no changes to this logic.
df1 = music_rec()  # Fetch music data
df1 = df1.head(15)  # Limit to the first 15 rows for display

# ✅ Home Route - Redirect to Register/Login
@app.route('/')
def home():
    return render_template('home.html')

# ✅ Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        address = request.form['address']
        gender = request.form['gender']
        dob = request.form['dob']

        # Strong Password Validation
        if not re.match(r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            flash("Password must have at least 8 characters, one uppercase letter, one number, and one special character.", "danger")
            return redirect('/register')

        # Hash Password
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insert into Database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, email, phone, password_hash, address, gender, dob) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                       (username, email, phone, password_hash, address, gender, dob))
        mysql.connection.commit()
        cursor.close()

        flash("Registration successful! Please login.", "success")
        return redirect('/login')

    return render_template('register.html')

# ✅ Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash("Login successful!", "success")
            return redirect('/index')
        else:
            flash("Invalid email or password!", "danger")

    return render_template('login.html')



# ✅ Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out!", "info")
    return redirect('/login')



@app.route('/index')
def index():
    # Convert the DataFrame to JSON and pass it to the frontend
    print(df1.to_json(orient='records'))  # Print to console for debugging
    return render_template('index.html', headings=headings, data=df1)

def gen(camera):
    while True:
        global df1
        frame, df1 = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/t')
def gen_table():
    # Return the music data as JSON
    return jsonify(df1.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
