from flask import Flask, render_template, url_for, request, redirect, flash
import sqlite3 as sql
import ibm_db

connection_online=ibm_db.connect("",'','')


app = Flask(__name__, static_folder='static')


@app.route("/")
def homePage():
    return render_template('home.html')


@app.route("/about")
def aboutPage():
    return render_template("about.html")


@app.route("/signin", methods=["GET", "POST"])
def signinpage():
    if request.method == "GET":
        return render_template('signin.html')
    else:
        email = request.form["email"]
        password = request.form["password"]
        sql_stmt="SELECT email,password FROM PERSONS WHERE email=?"
        prep_stmt=ibm_db.prepare(connection_online,sql_stmt)
        ibm_db.bind_param(prep_stmt,1,email)
        ibm_db.execute(prep_stmt)
        item=ibm_db.fetch_both(prep_stmt)
        print(item)


        return render_template("home.html")

        # with sql.connect("users.db") as connection:
        #     cursor = connection.cursor()
        #     cursor.execute(
        #         "SELECT email,password FROM STUDENTS WHERE email=?", (email,))
        #     student = cursor.fetchone()
        #     print(student)
            # if student:
            #     if password == student[1]:
            #         error = "Logged in"
            #         return render_template("home.html", error=error)
            #     else:
            #         error = "User Invalid Password"
            #     return render_template("signin.html", error=error)
            # else:
            #     error = "invalid credentials"
            #     return render_template("signin.html", error=error)


@app.route("/signup", methods=["GET", "POST"])
def signuppage():
    if request.method == "POST":
        password = request.form["password"]
        confirmPassword = request.form["confirm-password"]
        if password == confirmPassword:
            name = request.form["name"]
            email = request.form["email"]
            phone = request.form["phone"]
            password = request.form["password"]
            print(name, email, phone, password)
            sql_stmt="INSERT INTO PERSONS VALUES (?,?,?,?)"
            prep_statement=ibm_db.prepare(connection_online,sql_stmt)
            ibm_db.bind_param(prep_statement, 1, name)
            ibm_db.bind_param(prep_statement, 2, phone) 
            ibm_db.bind_param(prep_statement, 3, email)
            ibm_db.bind_param(prep_statement, 4, password)
            ibm_db.execute(prep_statement)
            
            # with sql.connect("users.db") as connection:
            #     cursor = connection.cursor()
            #     cursor.execute(
            #         "INSERT INTO students (name,phone,email,password) VALUES (?,?,?,?)", (name, phone, email, password))
            #     connection.commit()
            return redirect("/")
        else:
            return ("Password does not match each other   ")

    else:
        return render_template('signup.html')


@app.route("/add", methods=["GET", "POST"])
def addElement():
    if request.method == "GET":
        return render_template('addpage.html')
    else:
        uname = request.form["username"]
        contact = request.form["contact"]
        with sql.connect("students.db") as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO students (name,contact) VALUES (?,?)", (uname, contact))
            connection.commit()

        print(uname, contact)
        return redirect("/item")


@app.route("/item")
def addItem():
    with sql.connect("students.db") as connection:
        connection.row_factory = sql.Row
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        users = cursor.fetchall()
        # print(users)

    return render_template("item.html", user=users)


@app.route("/edit/<key>", methods=["GET", "POST"])
def editItem(key):
    if request.method == "GET":
        with sql.connect("students.db") as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM students WHERE name==? ", (key,))
            user = cursor.fetchone()
            print(user)
            return render_template("addpage.html", item=user)
    else:
        uname = request.form['username']
        contact = request.form['contact']
        with sql.connect("students.db") as connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE students SET name=?,contact=? WHERE name=?", (uname, contact, key,))
            connection.commit()
            return redirect("/item")


@app.route("/delete/<name>")
def deletePage(name):
    with sql.connect("students.db") as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE name=?", (name,))
        return redirect("/item")
