from flask import Flask,url_for,render_template,request,redirect
import sqlite3 as sql

app=Flask(__name__,static_folder="static")

@app.route("/",methods=["POST","GET"])
def home():
    if request.method=="GET":
        return render_template("home.html")

    else:
        email=request.form["email"]
        password=request.form["password"]
        print(email,password)

        with sql.connect("persons.db") as con:
            cursor=con.cursor()
            cursor.execute("SELECT email,password FROM persons WHERE email=? ",(email,))
            person=cursor.fetchone()
            print(person)
            print(person[0])

            if person:
                if password==person[1]:

                    return render_template("portal.html")
                else:
                    return "Incorrect password"

            else:
                return "Invalid Response"

@app.route("/signup" ,methods=["POST","GET"])
def signup():
    if request.method == "GET":
        
        return render_template('signup.html')
    else:
        
        name=request.form["name"]
        email=request.form["email"]
        phone=request.form["phone"]
        password=request.form["password"]
        re_password=request.form["Re-password"]
        print(name,email,phone,password,re_password)

        if (password==re_password):

            print("password matched")

            with sql.connect("persons.db") as con:
            
                cur=con.cursor();
                cur.execute("INSERT INTO persons (name,email,phone,password) VALUES (?,?,?,?)",(name,email,phone,password))
                con.commit()

                print("successfully added")
                return redirect("/")

        else:
            return "Password mismatching"

        



@app.route("/apply",methods=["POST","GET"])
def apply():
    if request.method=="GET":
        return render_template("portal.html")
    else:
        return "Successfully Applied"

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)
    