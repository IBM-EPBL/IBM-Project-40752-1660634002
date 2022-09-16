from flask import Flask,render_template,url_for,request,redirect

app=Flask(__name__, static_folder='static')

@app.route("/")
def homePage():
    return render_template('home.html')


@app.route("/about")
def aboutPage():
    return render_template("about.html")

@app.route("/signin")
def signinpage():
    return render_template('signin.html')

@app.route("/signup",methods=["GET","POST"])
def signuppage():
    if request.method=="POST":
        val=request.form
        print(val["name"])
        return redirect("/")
    else:    
        return render_template('signup.html')