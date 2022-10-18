from flask import Flask,render_template,request,redirect,flash
import sqlite3 as sql

import ibm_db



con=ibm_db.connect("","")
print(con)
print("connection successfull")

app=Flask(__name__,static_folder="static")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route('/about')
def about():
    return render_template('about.html')

#database connection 

@app.route("/signin", methods=["GET", "POST"])
def signinpage():
    if request.method == "GET":
        
        return render_template('signin.html')
    else:
        email = request.form["email"]
        password = request.form["password"]
        print(email,password)
        sql_stmt="SELECT email,password FROM USERS WHERE email=?"
        prep_stmt=ibm_db.prepare(con,sql_stmt)
        ibm_db.bind_param(prep_stmt,1,email)
        ibm_db.execute(prep_stmt)
        item=ibm_db.fetch_both(prep_stmt)
        print(item)


        return render_template("index.html")
    

@app.route('/signup', methods=['POST','GET'])
def submit():
    if(request.method =='POST'):
        password=request.form["password"]
        confirm_password=request.form["Re-password"]
        if password==confirm_password:
            name = request.form["name"]
            email = request.form["email"]
            phone = request.form["phone"]
            password = request.form["password"]
            print(name,email,phone,password)
            insert_sql="INSERT INTO users VALUES (?,?,?,?)"
            prep=ibm_db.prepare(con,insert_sql)
            ibm_db.bind_param(prep, 1, name)
            ibm_db.bind_param(prep, 2, phone) 
            ibm_db.bind_param(prep, 3, email)
            ibm_db.bind_param(prep, 4, password)
            ibm_db.execute(prep)
            return redirect("/")

        else:
            return("password doesn't match")
         

@app.route("/users")
def users():
    with sql.connect("users.db") as con:
        
        con.row_factory=sql.Row

        
        cur=con.cursor()
        cur.execute("SELECT * FROM users")
        users=cur.fetchall();
        print(users)
    return render_template("users.html",users=users)


@app.route("/edit/<name>")
def edit(name):
    
    with sql.connect("users.db") as con:
        cur=con.cursor()
        cur.execute("SELECT * FROM users WHERE name=?",(name,))
        user=cur.fetchone();
        print(user)
    return render_template("update.html",user=user )

        
        

@app.route("/delete/<name>")
def delete(name):
    with sql.connect("users.db") as con:
        cur=con.cursor()
        cur.execute("DELETE  FROM users WHERE name=?",(name,))
        return redirect("/users")
        

@app.route("/edit/<names>",methods=['POST'])
def update(names):
    name=request.form['name'];
    email=request.form['email'];
    phone=request.form['phone'];
    with sql.connect("users.db") as con:
        cur=con.cursor()
        cur.execute("UPDATE users SET name=?,email=?,phone=? WHERE name=?",(name,email,phone,names))
        con.commit()
    return redirect("/users")
    
    

if __name__=='__main__': 
    app.run(port=5000,debug=True)