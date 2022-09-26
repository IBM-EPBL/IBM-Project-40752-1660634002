from flask import Flask, render_template, url_for, request, redirect
import sqlite3 as sql

app = Flask(__name__, static_folder='static')


@app.route("/")
def homePage():
    return render_template('home.html')


@app.route("/about")
def aboutPage():
    return render_template("about.html")


@app.route("/signin")
def signinpage():
    return render_template('signin.html')


@app.route("/signup", methods=["GET", "POST"])
def signuppage():
    if request.method == "POST":
        val = request.form
        print(val["name"])
        return redirect("/")
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
        uname=request.form['username']
        contact=request.form['contact']
        with sql.connect("students.db") as connection:
            cursor=connection.cursor()
            cursor.execute("UPDATE students SET name=?,contact=? WHERE name=?",(uname,contact,key,))
            connection.commit()
            return redirect("/item")
        




@app.route("/delete/<name>")
def deletePage(name):
    with sql.connect("students.db") as connection:
        cursor=connection.cursor()
        cursor.execute("DELETE FROM students WHERE name=?",(name,))
        return redirect("/item")