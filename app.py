from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from datetime import datetime,timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


app = Flask(__name__)

app.secret_key = 'a4ad3bb3f36eff1b4d0e0fc83f1f4a0e3f0d76d712eb3bacad3646ab06373894'

app.debug = True


    
#function to get all the available dates
def available_dates():
    connection = sqlite3.connect('appointments.db')
    db = connection.cursor()
    today = datetime.now()
    avail_days_list = list(db.execute("SELECT * FROM available ORDER BY id DESC"))
    def sort_by_date(item):
        return datetime.strptime(item[1][:8], "%d-%m-%y")
    
    avail_days_sorted = sorted(avail_days_list, key=sort_by_date)
    avail_days = []
    for daydata in avail_days_sorted:
        d = datetime.strptime(daydata[1][:8], "%d-%m-%y")
        if d > today:
            day = d.strftime("%A")
            booked_day = datetime.strftime(d, "%d-%m-%y")
            booked_day = (booked_day + '(' + day + ')',daydata[2])
            avail_days.append(booked_day)
    connection.close()
    return avail_days
       
#index page route
@app.route("/",methods = ["POST", "GET"])
@app.route("/index.html", methods = ["POST","GET"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    
#login route
@app.route("/login", methods =["POST", "GET"])
def login():
    
    if request.method == "GET":
        return render_template("login.html")
    else:
        connection = sqlite3.connect('appointments.db')
        db = connection.cursor()
        username = str(request.form.get("username"))
        check_user = list(db.execute("SELECT id,username, password FROM users WHERE username = ?;", (username,)))
        #cheking user name if it exists
        if len(check_user) == 0:
            return render_template("login.html", x = "user name doesn't exists")
        #checking password is correct or not
        elif not (check_password_hash(check_user[0][2],request.form.get("password")) and username == check_user[0][1]):
            return render_template("login.html", x = "Wrong password")
        print(check_user)
        session["userid"] = check_user[0][0]
        session["username"] = username
        session["logged_in"] = True
        return redirect("index.html")
    
        
#logout
@app.route("/logout", methods = ["POST", "GET"])
def logout():
    #logging out clearing session
    session["logged_in"] = False
    session.pop("username", None)
    session.pop("useid", None)
    return render_template("index.html")

#register user
@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        connection = sqlite3.connect('appointments.db')
        db = connection.cursor()
        username = str(request.form.get("username"))
        print(username)
        hashed_password = generate_password_hash(request.form.get("password"))
        mail = str(request.form.get("email"))
        user_data = (username, hashed_password, mail)
        print(user_data)
        check_username = list(db.execute("SELECT COUNT(*) FROM users WHERE username = ?",(username,)))
        check_mail = list(db.execute("SELECT COUNT(*) FROM users WHERE email = ?",(mail,)))
        print(check_username)
        #checking if password and confirm are same
        if not check_password_hash(hashed_password, request.form.get("confirm")):
            return render_template("register.html", x = "PASSWORDS DONOT MATCH")
        #checking user name already doesnt exist
        elif check_username[0][0] != 0:
            return render_template("register.html", x = "username already taken")
        #checking if mail is already present or not
        elif check_mail[0][0] != 0:
            return render_template("login.html", x = "Account already exits for this mail login")
        
        db.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password HASH NOT NULL, email TEXT NOT NULL);")
        db.execute("INSERT INTO users(username, password, email) VALUES(?, ?, ?)", user_data)
        connection.commit()
        connection.close()
        return redirect("/")

#book appointment
@app.route("/book",methods = ["POST","GET"])
def book():
    if request.method == "POST":
        connection = sqlite3.connect('appointments.db')
        db = connection.cursor()
        db.execute("CREATE TABLE IF NOT EXISTS booked(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL, phno TEXT NOT NULL, date TEXT NOT NULL, booked_data TEXT NOT NULL, userid INTEGER, FOREIGN KEY (userid) REFERENCES users(id))")
        booked_day = request.form.get("book")
        booking_day = datetime.now()
        booking_day = datetime.strftime(booking_day, "%d-%m-%y")
        data = session["temp_data"]
        data.append(booked_day)
        data.append(booking_day)
        #checking if logged in or not and taking user_id
        try:
            if (session["logged_in"] == True):
                user_id = session['userid']
            else:
                user_id = None
        except:
            user_id = None
        data.append(user_id)
        #inserting booked data into database
        db.execute("INSERT INTO booked(name, email, phno, date, booked_data, userid) VALUES( ?, ?, ?, ?, ?, ? )", tuple(data))
        db.execute("UPDATE available SET appointments = appointments - 1 WHERE date = ?", (booked_day,))
        
        appointments = list(db.execute("SELECT appointments FROM available WHERE date = ?", (booked_day,)))
        print(booked_day)
        print(appointments)
       
        admin_mail = list(db.execute("SELECT email FROM users WHERE id == 1;"))
        
        print(admin_mail[0][0])
        connection.commit()
        connection.close()
        #mailing the admin
        from_mail = "captainappointease@gmail.com"
        subject = 'Apointment alert'
        message = f'Appointment made by \nname: {data[0]}\nemail: {data[1]}\nphno: {data[2]}\ndate: {data[3]}\nbooked_date: {data[4]}'
        msg = MIMEMultipart()
        msg['From'] = from_mail
        msg['To'] = admin_mail[0][0]
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_mail, "vhqe trvn wpnr gxbv")

            # Send the email
            server.sendmail(from_mail, admin_mail[0][0], msg.as_string())

            print('Email sent successfully!')

        except Exception as e:
            print('Email could not be sent. Error:', str(e))

        finally:
            server.quit()
        return render_template("index.html", success = "true")
    else:
        return redirect(url_for('index'))


#available slots
@app.route("/available", methods = ["GET", "POST"])
def available():
    if request.method == "POST":
        avail_days = available_dates()
        availDays = []
        print(avail_days)
        for d in avail_days:
            if d[1] > 0:
                availDays.append(d)
        email = request.form.get('email')
        name = request.form.get('name')
        phno = request.form.get('phno')
        session["temp_data"] = [name, email, phno]
        return render_template("index.html", avail_days=availDays, visibility = True)
    else:
        return render_template("index.html", visibility = False)


#appointment history
@app.route("/history",methods = ["POST","GET"])
def history():
    if session['logged_in'] == True:
        connection = sqlite3.connect("appointments.db")
        db = connection.cursor()
        user_id = (session["userid"],)
        history = list(db.execute("SELECT name,date, booked_data FROM booked WHERE userid = ? ORDER BY id DESC", user_id))
        print(history)
        connection.close()
        return render_template("history.html", history = list(history))
    else:
        return render_template("index.html", logged_in = 'false')


#admin route
@app.route("/admin", methods = ["GET", "POST"])
def admin():
    days =[]
    if session['userid'] == 1:
        if request.method == "GET":
            today = datetime.now()
            dayslist = [(today + timedelta(i)).strftime("%d-%m-%y") + '(' + (today + timedelta(i)).strftime("%A") + ')' for i in range(1,8)]
            days ={}
            for i in range(1,8):
                days[str(i)] = dayslist[i-1]
            avail_days = available_dates()
            avail = []
            for i in avail_days:
                avail.append(i[0])
            
            return render_template("admin.html",days = days, avail_days = avail_days, avail = avail)
        else:
            daylist = []
            connection = sqlite3.connect('appointments.db')
            db = connection.cursor()
            available = list(db.execute("SELECT date FROM available;"))
            if len(available) >= 7:
                db.execute("DELETE FROM available;")
                db.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'available';")
                connection.commit()
            db.execute("CREATE TABLE IF NOT EXISTS available(id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, appointments INTEGER)")
            for i in range(1,8):
                d = request.form.get(str(i))
                if (d,) not in available:
                    daylist.append(d)
                else:
                    daylist.append(None)
                if daylist[i-1] != None:
                    a = (daylist[i-1],15)
                    db.execute("INSERT INTO available(date, appointments) VALUES(?, ?)", a)
                    connection.commit()
            connection.close()
            return redirect(url_for('admin'))
    else:
        return render_template("index.html", admin_alert = 'true')
    

#dashboard
@app.route("/dashboard", methods = ["GET", "POSt"])
def dashboard():
    if session['logged_in']:
        user_id = session["userid"]
        connection = sqlite3.connect("appointments.db")
        db = connection.cursor()
        user_details = list(db.execute("SELECT * FROM users WHERE id = ?",(user_id,)))
        print(user_details)
        return render_template("dashboard.html", user_details = user_details[0])
    
#change password
@app.route("/changepass", methods = ["POST", "GET"])
def updatepass():
    if request.method == "POST":
        connection = sqlite3.connect("appointments.db")
        db = connection.cursor()
        hashed_password = generate_password_hash(request.form.get("password"))
        print(hashed_password)

        if not check_password_hash(hashed_password, request.form.get("confirm")):
            return render_template("register.html", x = "PASSWORDS DO NOT MATCH")
        elif "logged_in" in session.keys() and session["logged_in"]:
            user_id = session['userid']
            user = list(db.execute("SELECT id,email FROM users WHERE id = ?", (user_id,)))
        else:
            username = request.form.get("username")
            
            user = list(db.execute("SELECT id,email FROM users WHERE username = ?", (username,)))
            if not user:
                return render_template("changepass.html", x = "User not found")
        print(user)
        db.execute("UPDATE users SET password = ? WHERE id = ? and email = ?",(hashed_password, user[0][0], user[0][1]))
        connection.commit()
        if "logged_in" in session.keys() and session["logged_in"]:
            return render_template("index.html")
        return render_template("login.html")
    else:
        return render_template("changepass.html")
    
