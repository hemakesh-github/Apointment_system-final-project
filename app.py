from flask import Flask, render_template, request, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3



app = Flask(__name__)


app.debug = True


@app.route("/",methods = ["POST", "GET"])
@app.route("/index.html", methods = ["POST","GET"])
def fun():
    if request.method == "GET":
        return render_template("index.html")
    



@app.route("/login", methods =["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        return redirect("index.html")



@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        connection = sqlite3.connect('appointments.db')
        db = connection.cursor()
        username = (request.form.get("username"), )
        print(username)
        hashed_password = generate_password_hash(request.form.get("password"))
        mail = (request.form.get("email"),)
        user_data = (username, hashed_password, mail)
        check_username = list(db.execute("SELECT COUNT(*) FROM users WHERE username = ?",username))
        check_mail = list(db.execute("SELECT COUNT(*) FROM users WHERE email = ?",mail))
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
    
    
