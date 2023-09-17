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


The app.py contains 10 routes each route having its own role.

The "/index" route renders the index page.The "/login" route is used for logging in the user. "/logout" to logout the user by poping the session. The "/register" route is used to register a new user we check is username already exists or not if not we check if passwords match then create an account by adding details to user table of registrants.db.

The "/book" route is for booking the appointments we collect the data and confirm booking and send a mail to the admin regarding the appointment.

The "/available" route to display all the available dates. We get the dates from the database and pass to html file.

The "/history" route to display the previous appointments.

The "/admin" route is for managing admin functions like updating available dates.

The "/dashboard" route is to retrieve the current user data and sends to html file to display information.

The "/changepass" route to update the password in users table.

