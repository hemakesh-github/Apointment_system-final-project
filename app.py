from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from datetime import datetime,timedelta


app = Flask(__name__)

app.secret_key = 'a4ad3bb3f36eff1b4d0e0fc83f1f4a0e3f0d76d712eb3bacad3646ab06373894'

app.debug = True

if __name__ == '__main__':
    app.run(debug=True)


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
        if len(check_user) == 0:
            return render_template("login.html", x = "user name doesn't exists")
        elif not (check_password_hash(check_user[0][2],request.form.get("password")) and username == check_user[0][1]):
            return render_template("login.html", x = "Wrong password")
        print(check_user)
        session["userid"] = check_user[0][0]
        session["username"] = username
        session["logged_in"] = True
        return redirect("index.html")
    

@app.route("/logout", methods = ["POST", "GET"])
def logout():
    session.pop("logged_in", None)
    session.pop("username", None)
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
        if not check_password_hash(hashed_password, request.form.get("confirm")):
            return render_template("register.html", x = "PASSWORDS DONOT MATCH")
        elif check_username[0][0] != 0:
            return render_template("register.html", x = "username already taken")
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

        return "TO DO"
    else:
        return redirect(url_for('index'))
 
@app.route("/history")
def history():
    if request.method == "GET":
        return "TO DO"
     
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
            return render_template("admin.html",days = days)
        else:
            daylist = []
            connection = sqlite3.connect('appointments.db')
            db = connection.cursor()
            db.execute("CREATE TABLE IF NOT EXISTS available(id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT)")
            for i in range(1,8):
                daylist.append(request.form.get(str(i)))
                if daylist[i-1] != None:
                    a = (daylist[i-1],)
                    db.execute("INSERT INTO available(date) VALUES(?)", a)
                    connection.commit()
                    print(a)
            print(daylist)
            return redirect(url_for('admin'))
    else:
        return render_template("index.html", admin_alert = 'true')
    

