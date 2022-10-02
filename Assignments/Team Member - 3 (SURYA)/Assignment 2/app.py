from flask import Flask,render_template,request,redirect
import sqlite3 as sql

app=Flask(__name__,static_folder="static")

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/signin')
def signinpage():
    return render_template('signin.html')

@app.route("/signup")
def signuppage():
    return render_template("signup.html")

@app.route('/about')
def aboutpage():
    return render_template('about.html')

#database connection    

@app.route('/signup', methods=['POST','GET'])
def submitpage():
    if(request.method =='POST'):
        try:
            name=request.form['name'];
            email=request.form['email'];
            phone=request.form['phone'];
            password=request.form['password'];
            

            with sql.connect("items.db") as con:
                
                cur=con.cursor();
                cur.execute("INSERT INTO items (name,email,phone,password) VALUES (?,?,?,?)",(name,email,phone,password))
                con.commit()
                msg="Successfully added..!!";
            return msg
        
        except:
            con.rollback();
            msg="error in adding";
        finally:
            return redirect("/users")
            con.close();



@app.route("/users")
def userspage():
    with sql.connect("items.db") as con:
        
        con.row_factory=sql.Row

        
        cur=con.cursor()
        cur.execute("SELECT * FROM items")
        users=cur.fetchall();
    
    return render_template("users.html",users=users)


@app.route("/edit/<name>")
def editpage(name):
    
    with sql.connect("items.db") as con:
        cur=con.cursor()
        cur.execute("SELECT * FROM items WHERE name=?",(name,))
        user=cur.fetchone();
        print(user)
    return render_template("update.html",user=user )

        
        

@app.route("/delete/<name>")
def deletepage(name):
    with sql.connect("items.db") as con:
        cur=con.cursor()
        cur.execute("DELETE  FROM items WHERE name=?",(name,))
        return redirect("/users")
        

@app.route("/edit/<names>",methods=['POST'])
def updatepageb(names):
    name=request.form['name'];
    email=request.form['email'];
    phone=request.form['phone'];
    with sql.connect("items.db") as con:
        cur=con.cursor()
        cur.execute("UPDATE items SET name=?,email=?,phone=? WHERE name=?",(name,email,phone,names))
        con.commit()
    return redirect("/users")
    
    

if __name__=='__main__': 
    app.run(debug=True)