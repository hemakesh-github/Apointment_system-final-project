# CAPTAIN APPOINTEASE
#### Video Demo:  https://youtu.be/30pezXbaPsI
#### Description:
This is Captain Appointease an appointment booking website

This website is based on flask.

Storing data:
All the data is stored in the appointments.db whose schema is
*CREATE TABLE users(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password HASH NOT NULL, email TEXT NOT NULL);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE booked(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL, phno TEXT NOT NULL, date TEXT NOT NULL, booked_data TEXT NOT NULL, userid INTEGER, FOREIGN KEY (userid) REFERENCES users(id));
CREATE TABLE available(id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, appointments INTEGER);*

In the users table we store the user data such as username, password, email. In the booked table we store name, email, phone number, date, and booked_date. In the available table we store the available dates and number of appointments


The app.py contains 10 routes each route having its own role. and a funtion available_dates()

In available_dates() funtion we connnect with appointments.db then get data from avaialable table and sort it and attach day part to day and returns the available dates.

The "/index" route renders the index page.

The "/login" route is used for logging in the user.if request method is get then render login.html. if not establish a connection between appointments.db and take a cursor db. Get the username from form and check if it exists and then get the password from user and and convert to hash and check if  it is right with the available data in the users table if correct we implement session saving userid, username, and logged_in boolean in the session the redirect to index.html

"/logout" to logout the user by poping the session and render index.html.

The "/register" route is used to register a new user. if request method is get renders register.html if not we establish a connection between the database appointments.db and the get the username from form then  we check is username already exists or not if not we check if passwords match and get email from and form and check if it already exists in the users table if not then create an account by adding details to user table of registrants.db.

The "/book" route is for booking the appointments we collect the data and confirm booking and send a mail to the admin regarding the appointment. if the request method id post then we establish a connection with appointments.db and create a table booked if not exists the get the booked day from form find todays date convert to string. we retrieve data from session["temp_data] and then append booked day and booking day then check if user is logged in if yes get user id from session else userid is None and append thi userid to data. Now we add all this data to booked table and then update the appointments by decreasing 1 in the table available. Now we try to mail the admin by geting the admin mail from users table then we render index.html with an alert Appointment successfull.

The "/available" route to display all the available dates. We get the dates from the database and pass to html file. if the request method id post we get the available dates calling  available_dates() funtion. then update these available dates where appointments > 0. then get email, name, phone number from the form and store in session["temp_data] to be used in the "/book" route. and renders index.html passing values to the place holder

The "/history" route to display the previous appointments.

The "/admin" route is for managing admin functions like updating available dates.

The "/dashboard" route is to retrieve the current user data and sends to html file to display information.

The "/changepass" route to update the password in users table.

