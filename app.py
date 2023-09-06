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

if __name__ == '__main__':
    app.run(debug=True)

#function to get all the available dates
def available_dates():
    connection = sqlite3.connect('appointments.db')
    db = connection.cursor()
    today = datetime.now()
    avail_days_list = list(db.execute("SELECT * FROM available ORDER BY id DESC"))
    def sort_by_date(item):
        return datetime.strptime(item[1], "%d-%m-%y")
    
    avail_days_sorted = sorted(avail_days_list, key=sort_by_date)
    avail_days = []
    for day in avail_days_sorted:
        d = datetime.strptime(day[1], "%d-%m-%y")
        if d > today:
            day = d.strftime("%A")
            booked_day = datetime.strftime(d, "%d-%m-%y")
            booked_day = booked_day + '(' + day + ')'
            avail_days.append(booked_day)
    print(avail_days)
    connection.close()
    return avail_days
       
#index page route
@app.route("/",methods = ["POST", "GET"])
@app.route("/index.html", methods = ["POST","GET"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    

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
    

@app.route("/logout", methods = ["POST", "GET"])
def logout():
    #logging out clearing session
    session["logged_in"] = False
    session.pop("username", None)
    session.pop("useid", None)
    return render_template("index.html")


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
        if (session["logged_in"] == True):
            user_id = session['userid']
        else:
            user_id = None
        data.append(user_id)
        #inserting booked data into database
        db.execute("INSERT INTO booked(name, email, phno, date, booked_data, userid) VALUES( ?, ?, ?, ?, ?, ? )", tuple(data))
        admin_mail = list(db.execute("SELECT email FROM users WHERE id == 1;"))
        print(admin_mail[0][0])
        connection.commit()
        connection.close()
        #mailing the admin
        from_mail = "captainappointease@gmail.com"
        subject = 'Apointment alert'
        message = f'Appointment made by \nname: {data[0]}\nemail: {data[1]}\nphno: {data[3]}\ndate: {data[4]}\nbooked_date: {data[5]}'
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
        return 'APPOINTMENT SUCCESSFUL'
    else:
        return redirect(url_for('index'))
    
@app.route("/available", methods = ["GET", "POST"])
def available():
    if request.method == "POST":
        avail_days = available_dates()
        email = request.form.get('email')
        name = request.form.get('name')
        phno = request.form.get('phno')
        session["temp_data"] = [name, email, phno]
        return render_template("index.html", avail_days=avail_days, visibility = True)
    else:
        return render_template("index.html", visibility = False)

 
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
     
@app.route("/admin", methods = ["GET", "POST"])
def admin():
    days =[]
    if session['userid'] == 1:
        if request.method == "GET":
            today = datetime.now()
            dayslist = [(today + timedelta(i)).strftime("%d-%m-%y") for i in range(7)]
            days ={}
            for i in range(1,8):
                days[str(i)] = dayslist[i-1]
            avail_days = available_dates()
            return render_template("admin.html",days = days, avail_days = avail_days)
        else:
            daylist = []
            connection = sqlite3.connect('appointments.db')
            db = connection.cursor()
            available = list(db.execute("SELECT date FROM available;"))
            print(available)
            if len(available) >= 7:
                db.execute("DELETE FROM available;")
                db.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'available';")
                connection.commit()
            db.execute("CREATE TABLE IF NOT EXISTS available(id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT)")
            for i in range(1,8):
                d = request.form.get(str(i))
                if (d,) not in available:
                    daylist.append(d)

                else:
                    daylist.append(None)
                if daylist[i-1] != None:
                    a = (daylist[i-1],)
                    db.execute("INSERT INTO available(date) VALUES(?)", a)
                    connection.commit()
                    connection.close()
            return redirect(url_for('admin'))
    else:
        return render_template("index.html", admin_alert = 'true')
    

