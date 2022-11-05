from flask import Flask, render_template, request, redirect, jsonify, make_response, url_for,flash
import sqlite3
import re
import hashlib
from flask_login import (login_required, login_user, logout_user)
import uuid
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
bcrypt = Bcrypt(app)
salt = "5gz"


app.config["KEY"] = "Hello"
app.secret_key="Rajubai"


def verify(token):
    data = jwt.decode(token, "Hello", algorithms='HS256')
    return data["email"]

def user():
    token = request.cookies.get('token-user')
    data=jwt.decode(token,"Hello",algorithms='HS256')
    return data["id"]



# -----------------------------------------RECRUITER LOGIN/SIGNIN FUNCTIONS-------------------------------------------------


@app.route("/hr/signin", methods=('GET', 'POST'))
def hrSignIn():
    if request.method == "GET":
        return render_template("./sign/hrsignin.html")
    else:
        email = request.form["email"]
        password = request.form["password"]
        with sqlite3.connect('hr.db') as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT email FROM RECRUITER WHERE email=?", (email,))
            user = cursor.fetchone()
            if user == None:
                flash('Invalid email/password','alert alert-danger')
                return redirect("/hr/feed")
            else:
                db_password = password+salt
                pw_hash = hashlib.md5(db_password.encode())

                cursor.execute(
                    "SELECT email,password FROM RECRUITER WHERE email=?", (email,))
                details = cursor.fetchone()
                print(details)
                if pw_hash.hexdigest() == details[1]:
                    token = jwt.encode({"email": email, 'exp': datetime.utcnow(
                    )+timedelta(minutes=30)}, "Hello", algorithm='HS256')
                    print(token)

                    response = make_response(
                        redirect("/hr/feed"))
                    response.set_cookie('token', '')
                    response.set_cookie('token-user', '')
                    response.set_cookie('token', token)
                    return response

                else:
                    flash('Invalid email/password','alert alert-danger')
                    return redirect("/hr/signin")


@app.route("/hr/signup", methods=("GET", "POST"))
def hrSignUp():
    if request.method == "GET":
        return render_template("./sign/hrsignup.html")
    else:
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        confirm = request.form["re-password"]
        if email:
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

            def check(email):
                if (re.fullmatch(regex, email)):
                    flash('Invalid email/password','alert alert-danger')
                    return  redirect("/hr/signup")
                else:
                    flash('Invalid email/password','alert alert-danger')
                    return redirect("/hr/signup")
        if password != confirm:
            flash('Invalid email/password','alert alert-danger')
            return redirect("/hr/signup")
        else:
            with sqlite3.connect('hr.db') as connection:
                cursor = connection.cursor()
                cursor.execute(
                    """ SELECT email FROM RECRUITER WHERE email=? """, (email,))
                user = cursor.fetchone()
                print(user)
                if user == None:
                    key = uuid.uuid1().hex
                    print(key)

                    db_password = password+salt
                    pw_hash = hashlib.md5(db_password.encode())

                    cursor.execute("INSERT INTO RECRUITER (name,email,phone,password,id) VALUES (?,?,?,?,?)", (
                        name, email, phone, pw_hash.hexdigest(), key))
                    connection.commit()
                    flash('Account created successfully','alert alert-success')
                    return redirect("/hr/signup")
                else:
                    flash('Invalid Credintials','alert alert-danger')
                    return redirect("/hr/signup")


@app.route("/hr/logout")
def logout():
    response = make_response(redirect("/hr/signin"))
    response.set_cookie('token', '')
    return response


@app.route("/hr/feed")
def hrFeed():
    try:
        token = request.cookies.get('token')
        data = jwt.decode(token, "Hello", algorithms='HS256')
        with sqlite3.connect("hr.db") as connection:
               connection.row_factory=sqlite3.Row
               cursor=connection.cursor()
               cursor.execute(""" SELECT author_id,post_id,author_name,title,description FROM POSTS """)
               data=cursor.fetchall()
               data.reverse()
               return render_template("./feed/feed.html",data=data)
        
    except:
        return redirect("/hr/signin")
       
@app.route("/hr/feed/<id>")
def hrOneFeed(id):
    try:
        token = request.cookies.get('token')
        data = jwt.decode(token, "Hello", algorithms='HS256')

        print(id)
        return render_template("./feed/oneFeed.html")
    except:
        return redirect("/hr/signin")


@app.route("/hr/application")
def hrApplication():
    try:
        token = request.cookies.get('token')
        email = verify(token)
        print(email)
        with sqlite3.connect('hr.db') as connection:
            connection.row_factory= sqlite3.Row
            cursor=connection.cursor()
            cursor.execute(""" SELECT author_hr,post_id,user_id,viewed FROM APPLICATIONS WHERE author_hr=?""",(email,))
            data=cursor.fetchall()
            details=[]
            if data:
                application=[]
                if data:
                    for x in data:
                        with sqlite3.connect('hr.db') as connection:
                            # connection.row_factory=sqlite3.Row
                            cursor=connection.cursor()
                            cursor.execute("""SELECT name,about,designation,id FROM USERS WHERE id=?""",(x["user_id"],))
                            user=cursor.fetchone()
                            cursor.execute(""" SELECT title,designation,id FROM OPENINGS WHERE id=?""",(x["post_id"],))
                            post=cursor.fetchone()
                            a=x["viewed"]
                            print(post)
                            
                            if user and post :
                                if x["viewed"]:

                                    application=(user+post+("viewed",)  )
                                else :
                                    application=(user+post)    
                            print(application)
                            details.append(application)
                            connection.commit()
                    print(details)
                    details.reverse()
                    return render_template("./application/applications.html",data=details)
                else:
                    return render_template("./application/applications.html")    
            else:
                return render_template("./application/applications.html")        
    except Exception as e:
        print("Failed")
        print(e)
        return redirect("/hr/signin")

@app.route("/hr/view/<id>")
def viewApplication(id):
    try:
        search=request.args['search']
        print("search",search)
        token=request.cookies.get('token')
        email=verify(token)
        with sqlite3.connect('hr.db') as connection:
            connection.row_factory=sqlite3.Row
            cursor=connection.cursor()
            cursor.execute(""" SELECT viewed FROM APPLICATIONS   WHERE post_id=? AND user_id=?""",(search,id,))
            isviewed=cursor.fetchone()
            print("view",isviewed["viewed"])
            if isviewed["viewed"]==None:
                cursor.execute(""" UPDATE  APPLICATIONS SET viewed=?  WHERE post_id=? AND user_id=?""",("viewed",search,id,))
                cursor.fetchone()
            
            cursor.execute(""" SELECT name,email,phone,about,designation,school,skills,project,description FROM USERS WHERE id=? """,(id,))
            user=cursor.fetchone()
            print(user[0])
            return render_template('./application/view_application.html',data=user)
    except Exception as e:
        print(e)
        return "/hr/signin"    


@app.route("/hr/application/<id>")
def hrOneApplication(id):
    try:
        token = request.cookies.get('token')
        email = verify(token)
        with sqlite3.connect('hr.db') as connection:
            connection.row_factory= sqlite3.Row
            cursor=connection.cursor()
            cursor.execute(""" SELECT author_hr,post_id,user_id FROM APPLICATIONS WHERE author_hr=?""",(email))
            data=cursor.fetchall()
            print(data)
            print("finished")
            return "success"
            
        print(email)

        return render_template("./application/oneApplication.html")
    except:
        return redirect("/hr/signin")

# TO VIEW THE PROFILE
@app.route("/hr/profile")
def hrProfile():
    try:
        token = request.cookies.get('token')
        email = verify(token)
        print(email)
        with sqlite3.connect('hr.db') as connection:
            cursor=connection.cursor()
            cursor.execute("""
            
            SELECT name,
            email,
            about_me,
            designation,
            experience ,
            url ,
            company_name ,
            company_description ,
            location ,
            website ,
            in_url 
             FROM RECRUITER WHERE email=?""", (email,))
            data=cursor.fetchone()
            print(data) 
            if not data:
                return redirect("/hr/logout")
            else:
                return render_template("./profile/viewProfile.html",data=data)


            

        
    except Exception as e:
        print(e)
        return redirect("/hr/signin")

# VIEW THE RECRUITERS PROFILE AND EDIT THE INFORMATION
@app.route("/hr/profile/edit")
def hrProfileEdit():
    try:
        token = request.cookies.get('token')
        email = verify(token)
        print(email)


        with sqlite3.connect('hr.db') as connection:
            cursor=connection.cursor()
            cursor.execute("""
            
            SELECT name,
            email,
            about_me,
            designation,
            experience ,
            url ,
            company_name ,
            company_description ,
            location ,
            website ,
            in_url ,
            id
             FROM RECRUITER WHERE email=?""", (email,))
            data=cursor.fetchone()
            print(data[11]) 
            if not data:
                return redirect("/hr/logout")
            else:
                return render_template("./profile/editProfile.html",data=data)


        return render_template("./profile/editProfile.html")
    except Exception as e:
        print(e)
        return redirect("/hr/signin")


@app.route("/hr/profile/edit/<id>",methods=("POST","GET"))
def profileEditIID(id):

    if request.method=="POST":
        
        token = request.cookies.get('token')
        print("post")
        try:
            print(token)
           
            email = verify(token)
            print(email)
            name=request.form["name"]
            
            about_me=request.form["about_me"]
            designation=request.form['designation']
            experience=request.form['experience']
            url=request.form['url']
            company_name=request.form['company_name']
            company_description=request.form['company_description']
            location=request.form["location_in"]
            website=request.form['website']


            print(email,name,about_me,designation,experience,location,website)
            if not id:
                return redirect("/hr/profile")
            
            with sqlite3.connect('hr.db') as connection:
                cursor=connection.cursor()
                cursor.execute("""SELECT id FROM RECRUITER WHERE email=?""",(email,))
                data=cursor.fetchone()
                if data[0]==id:
                    print( "verified")
                    cursor.execute("""
            
                    UPDATE RECRUITER  SET
                    name=?,   
                    about_me=?,
                    designation=?,
                    experience=?,
                    url=?,
                    company_name=? ,
                    company_description=? ,
                    location =?,
                    website=? 
                    
                    WHERE email=? """, (name,
                    about_me,
                    designation,
                    experience,
                    url,
                    company_name,
                    company_description ,
                    location,
                    website,
                    email))
                    connection.commit()
                    print("updated")
                    return redirect("/hr/profile")

        except Exception as e:
            print(e)
            return "failed"




@app.route("/hr/profile/pwd", methods=("GET", "POST"))
def hrProfileEditPWD():

    if request.method == "GET":

        try:
            token = request.cookies.get('token')
            email = verify(token)
            print(email)
            return render_template("./profile/passwordReset.html")

        except:
            return redirect("/hr/signin")

    else:
        try:
            token = request.cookies.get('token')
            email = verify(token)
            print(email)
            password = request.form["password"]
            newPWD = request.form['newPassword']
            confirmPWD = request.form['confirmPassword']
            print(password, newPWD, confirmPWD)
            return redirect("/hr/profile/pwd")
        except:
            return redirect("/hr/signin")

#VIEWING OPENING
@app.route("/hr/openings")
def hrOpenings():
    try:
        token = request.cookies.get('token')
        email = verify(token)
        with sqlite3.connect('hr.db') as connection:
            cursor=connection.cursor()
            cursor.execute(""" SELECT id,title,company_name,designation,salary_range,skills_required,roles_responsibilities,company_description,location,website,author FROM OPENINGS WHERE author=?""", (email,))
            data=cursor.fetchall()
            data.reverse()
            
            connection.commit()
            return render_template("./openings/viewOpening.html",data=data)
    except Exception as e:
        
    
        return redirect("/hr/signin")

# CREATION NEW OPENING
@app.route("/hr/openings/new", methods=('GET', 'POST'))
def hrOpeningsCreate():
    if request.method == 'GET':
        try:
            token = request.cookies.get('token')
            email = verify(token)
            

            return render_template("./openings/oneOpening.html")
        except:

            return redirect("/hr/signin")
    else:

        try:
            token = request.cookies.get('token')
            email = verify(token)
            
            title = request.form["title"]
            company_name = request.form["company_name"]

            designation = request.form["designation"]

            salary_range = request.form["salary_range"]
            skills_required = request.form["skills_required"]
            roles_responsibilities = request.form["roles_responsibilities"]
            company_description = request.form["company_description"]
            location = request.form["location"]
            website = request.form["website"]

            author = email
            
            with sqlite3.connect('hr.db') as connection:
                key = uuid.uuid1().hex
                cursor = connection.cursor()
                cursor.execute("INSERT INTO OPENINGS (id,title,company_name,designation,salary_range,skills_required,roles_responsibilities,company_description,location,website,author) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (
                    key, title, company_name, designation, salary_range, skills_required, roles_responsibilities, company_description, location, website, author))
                connection.commit()
                flash('You have successfully created the opening','alert alert-success')
                return redirect('/hr/openings')

        except Exception as e:
            print(e)
            return redirect('/hr/openings')


# DELETEING THE  OPENINGS
@app.route("/hr/opening/<id>")
def deleteOpening(id):
    try:
        token = request.cookies.get('token')
        email = verify(token)
        with sqlite3.connect('hr.db') as connection:
            cursor=connection.cursor()
            cursor.execute(""" SELECT id FROM OPENINGS WHERE id=?""",(id,))
            
            data=cursor.fetchone()
            if not data:
                return redirect("/hr/openings")
            else:
                print(data[0])
                cursor.execute(""" DELETE FROM OPENINGS WHERE id=? """,(data[0],))
                cursor.execute(""" DELETE FROM  APPLICATIONS WHERE post_id=? """,(data[0],))
                connection.commit()
                flash('Deleted Successfully','alert alert-danger')
                return  redirect("/hr/openings") 

    except Exception as e:
        connection.commit()
        print(e)    
        return "null"




#Editing the openings
@app.route("/hr/openings/edit/<id>",methods=('GET','POST'))
def hrOpeningsOne(id):
    if request.method=="GET":
        try:
            token = request.cookies.get('token')
            email = verify(token)
            print(email)
            if not id:
                return render_template("./openings/oneOpening.html")
            with sqlite3.connect('hr.db') as connection:
                cursor=connection.cursor()
                cursor.execute("""SELECT id,author FROM OPENINGS WHERE id=? """,(id,))
                data=cursor.fetchone()
                if not data :
                    return redirect("/hr/openings")    
                elif email== data[1]:
                    cursor.execute(""" SELECT 
                    id,
                    title,company_name,
                    designation,
                    salary_range,
                    skills_required,
                    roles_responsibilities,
                    company_description,
                    location,website,
                    author
                    FROM OPENINGS WHERE id=?""", (id,))
                    data=cursor.fetchone()
                    connection.commit()
                    
                    return render_template("./openings/editing.html",data=data)
                else:
                    return redirect("/hr/openings")   
            return render_template("./openings/oneOpening.html")
        except Exception as e:
            print(e)
            return redirect("/hr/signin")
    else:


        token = request.cookies.get('token')
        email = verify(token)
        
        title = request.form["title"]
        company_name = request.form["company_name"]
        designation = request.form["designation"]
        salary_range = request.form["salary_range"]
        skills_required = request.form["skills_required"]
        roles_responsibilities = request.form["roles_responsibilities"]
        company_description = request.form["company_description"]
        location = request.form["location"]
        website = request.form["website"]
        author = email
        with sqlite3.connect('hr.db') as connection:
                cursor=connection.cursor()
                cursor.execute("""SELECT id,author FROM OPENINGS WHERE id=? """,(id,))
                data=cursor.fetchone()
                if not data :
                    return redirect("/hr/openings")    
                elif email== data[1]:
                    cursor.execute("""
                    UPDATE OPENINGS SET 
                    title=?,
                    company_name=?,designation=?,
                    salary_range=?,
                    skills_required=? ,
                    roles_responsibilities=? ,
                    company_description=?,
                    location=?,
                    website=?

                    WHERE id=? """,(title,
                    company_name,designation,
                    salary_range,
                    skills_required ,
                    roles_responsibilities ,
                    company_description,
                    location,
                    website,
                    id
))
                    data=cursor.fetchone()
                    connection.commit()
                    flash('Opening Updated Successfully','alert alert-success')
                    return redirect("/hr/openings")
                else:
                    return redirect("/hr/openings") 


# Viewing an application
@app.route("/hr/openings/view/<id>")
def viewOpenings(id):
    token = request.cookies.get('token')
    try:
        email = verify(token)
        print(email)
        with sqlite3.connect('hr.db') as connection:
            cursor=connection.cursor()
            cursor.execute(""" SELECT 
                    id,
                    title,company_name,
                    designation,
                    salary_range,
                    skills_required,
                    roles_responsibilities,
                    company_description,
                    location,website,
                    author
                    FROM OPENINGS WHERE id=?""", (id,)) 
            data=cursor.fetchone() 
            connection.commit()
            print(data)
            if not data:
                return redirect('/hr/openings')
            else:
                
                return render_template("./openings/viewOneopening.html",details=data)    

    



    except Exception as e:
        print(e)
        return redirect("/hr/openings")   







# ---------------------------------------------------RECRUITER FUNCTIONS FINISHED --------------------------------------

#----------------------------------------------------USER FUNCTION STARTED ---------------------------------------------

@app.route("/user/signin",methods=["POST","GET"])
def userlogin():
    if request.method=="GET":
        return render_template("./user/signin.html")

    else:
        email=request.form["email"]
        password=request.form["password"]
        print(email,password)

        with sqlite3.connect("hr.db") as con:
            cursor=con.cursor()
            cursor.execute("SELECT email,password,id FROM users WHERE email=?",(email,))
            user=cursor.fetchone()
            db_password=password+salt
            pw_hash = hashlib.md5(db_password.encode()).hexdigest()
            
            
            if not email or not password or not user:
                flash('Invalid Credentials','alert alert-danger')
                return render_template("./user/signin.html")

            if user:
                if pw_hash==user[1]:
                    token = jwt.encode({"id": user[2], 'exp': datetime.utcnow(
                    )+timedelta(minutes=30)}, "Hello", algorithm='HS256')
                    print(token)

                    response = make_response(
                        redirect("/user/newsfeed"))
                    response.set_cookie('token', '')    
                    response.set_cookie('token-user', '')    
                    response.set_cookie('token-user', token)
                    return response

                else:

                    flash('Invalid Credentials','alert alert-danger')
                    return redirect("/user/signin")

            else:
                flash('Invalid Credentials','alert alert-danger')
                return redirect("/user/signin")



@app.route("/user/signup",methods=["POST","GET"])
def signup():
    if request.method=="GET":
        return render_template("./user/signup.html")

    else:
        name=request.form["name"]
        email=request.form["email"]
        phone=request.form["number"]
        password=request.form["password"]
        re_password=request.form["re-password"]
        key=uuid.uuid1().hex
        print(name,email,phone,password,re_password,key)

        if not name or not email or not phone or not password or not re_password:

            flash('Incorrect Credentials','alert alert-danger')
            return redirect("/user/signup")
        with sqlite3.connect('hr.db') as connection:
            cursor=connection.cursor()
            cursor.execute("""SELECT id FROM USERS WHERE email=?""",(email,))
            data=cursor.fetchone()

        if password==re_password and not data:
            print("password matched")

            with sqlite3.connect("hr.db") as con:
                db_password=password+salt
                pw_hash = hashlib.md5(db_password.encode())
                cur=con.cursor();
                cur.execute("INSERT INTO users (id,name,email,phone,password) VALUES (?,?,?,?,?)",(key,name,email,phone,pw_hash.hexdigest()))
                con.commit()

                print("successfully added")
                flash('Account Created Successfully','alert alert-success')
                return redirect("/user/signin")
        else:
            flash('Incorrect Credentials','alert alert-danger')
            return redirect("/user/signup")


@app.route("/user/profile")
def userprofile():
    try:
        id=user()
        with sqlite3.connect('hr.db') as connection:
            connection.row_factory=sqlite3.Row
            cursor=connection.cursor()
            cursor.execute(""" SELECT id ,name,email,phone,password,about,designation,school,skills,project,description FROM USERS WHERE id=?""",(id,))
            data=cursor.fetchall()
            print(data)
            return render_template("./user/profile.html",data=data)
        
    
    except Exception as e:
        print("failed   ")
        print(e)  
        return redirect("/user/signin")

@app.route("/user/profile/editprofile",methods=["POST","GET"])
def editProfiles():

    try:
        id=user()
    


        if request.method=="GET":
            try:
                with sqlite3.connect('hr.db') as connection:
                    connection.row_factory=sqlite3.Row
                    cursor=connection.cursor()
                    cursor.execute(""" SELECT id,name,about,designation,school,skills,phone,project,description FROM USERS WHERE id=? """,(id,))
                    data=cursor.fetchall()
                    print(data)
                    connection.commit()
                    return render_template("./user/editprofile.html",data=data)

            except Exception as e:
                    print(e)
                    return "fail"
        else:
            name=request.form["name"]
            about=request.form["about"]
            phone=request.form["phone"]
            designation=request.form["designation"]
            school=request.form["school"]
            skills=request.form["skills"]
            project=request.form["project"]
            description=request.form["description"]

            print(name,about,phone,designation,school,skills,project,description)

            with sqlite3.connect("hr.db") as con:
                cursor=con.cursor()
                cursor.execute("UPDATE  USERS SET name=?,about=?,phone=?,designation=?,school=?,skills=?,project=?,description=? WHERE id=? ",
                (name,about,phone,designation,school,skills,project,description,id))
                con.commit()
                flash('Profile updated successfully','alert alert-success')

                
                return redirect("/user/profile")
    except Exception as e:
        print(e)
        return redirect("/user/signin")

@app.route("/user/logout")
def logoutUSer():
    response=make_response(redirect("/user/signin"))
    response.set_cookie('token-user','')

    return response
@app.route("/user/jobs")
def jobs():
    try:
        id=user()
        with sqlite3.connect('hr.db') as connection:
            connection.row_factory=sqlite3.Row
            cursor=connection.cursor()
            cursor.execute(""" SELECT  id,
                title,
                company_name,
                designation ,
                salary_range,
                skills_required,
                roles_responsibilities,
                company_description,
                location,
                website,
                author FROM OPENINGS """)
            data=cursor.fetchall()
            data.reverse()
            print(data)
            connection.commit()     
            return render_template("./user/jobs.html",data=data )
    
    except:
        return redirect("/user/signin")


@app.route("/user/view_application/<key>")
def viewOneJobOpenings(key):
    try:
        id=user()
        with sqlite3.connect('hr.db') as connection:
            connection.row_factory=sqlite3.Row
            cursor=connection.cursor()
            cursor.execute(""" SELECT title,
                id,
                company_name,
                designation ,
                salary_range,
                skills_required,
                roles_responsibilities,
                company_description,
                location,
                website,
                author FROM OPENINGS WHERE id=? """,(key,))
            data=cursor.fetchmany()
            cursor.execute(""" SELECT name FROM RECRUITER WHERE email=?  """,(data[0]["author"],))
            hr=cursor.fetchmany()
            cursor.execute(""" SELECT author_hr FROM APPLICATIONS WHERE post_id=? AND user_id=?  """,(key,id))
            isApplied=cursor.fetchone()
            button_enable=False
            if isApplied:            
                button_enable=True
                
                

            print(data[0]["author"])
            print(hr)
            return render_template("./user/jobs_view.html" ,data=data,hr=hr[0][0],button=button_enable)
    except Exception as e:
        print(e)
        return "failed"

@app.route("/user/apply/<job_id>")
def applicationApply(job_id):
    try:
        user_id=user()
        print(id)
        with sqlite3.connect('hr.db') as connection:
            print(job_id)
            
            cursor = connection.cursor()
            cursor.execute(""" SELECT author FROM OPENINGS WHERE id=? """ ,(job_id,))
            data=cursor.fetchall()
            print(data[0][0])
            cursor.execute(""" INSERT INTO APPLICATIONS  (author_hr,post_id,user_id) VALUES (?,?,?) """,(data[0][0],job_id,user_id))
            flash('Applied Successfully','alert alert-success')
            return redirect("/user/jobs")
    except Exception as e:
        print(e,"Happened")
        return "wrong"




@app.route("/user/newsfeed")
def addproject():
    try:
        id=user()
        try :
            with sqlite3.connect("hr.db") as connection:
                connection.row_factory=sqlite3.Row
                cursor=connection.cursor()
                cursor.execute(""" SELECT author_id,post_id,author_name,title,description FROM POSTS """)
                data=cursor.fetchall()
                data.reverse()
                return render_template("./user/newsfeed.html",data=data)
        
        except: 
            return redirect("/user/signin")    
    except Exception as e:
        print(e)
        return redirect('/user/signin')

@app.route("/user/feed/new",methods=("GET","POST"))
def addfeednews():
    if request.method=="POST":
        try:
            id=user()
            title=request.form["title"]
            description=request.form["description"]
            print(title,description,id)
            if title and description and id :
                with sqlite3.connect("hr.db") as connection:
                    post_id=uuid.uuid1().hex
                    cursor=connection.cursor()
                    cursor.execute(""" SELECT name FROM USERS WHERE id=? """,(id,))
                    name=cursor.fetchone()
                    print(name)
                    cursor.execute(""" INSERT INTO POSTS  (author_name,author_id,title,description,post_id) VALUES (?,?,?,?,?) """,(name[0],id,title,description,post_id))
                    flash('Post uploded successfully','alert alert-success')
            return redirect("/user/newsfeed")
        except Exception as e:
            print(e)
            return redirect("/user/newsfeed")

    else:    
        try:
            id=user()
            return render_template("./user/create_feed.html")
        except Exception as e:
            print(e)
            return redirect('/user/signin')

@app.route("/user/posts")
def userPost():
    try:
        id=user()
        try:
            with sqlite3.connect("hr.db") as connection:
                connection.row_factory=sqlite3.Row
                cursor=connection.execute(""" SELECT author_name,author_id,title,description,post_id FROM POSTS WHERE author_id=? """,(id,))
                data=cursor.fetchall()
                data.reverse()
                connection.commit()
                
                return render_template("./user/view_post.html",data=data)
        except Exception as e:
            print(e)
            return redirect("/user/newsfeed")


    except Exception as e:
        print(e)
        return redirect("/user/signin")    

@app.route("/user/delete/<post_id>")
def userPostDelete(post_id):
    try:
        id=user()
        try:
            with sqlite3.connect('hr.db') as connection:
                cursor=connection.cursor()
                cursor.execute(""" SELECT title FROM POSTS WHERE post_id=? """,(post_id,))
                post=cursor.fetchone()
                print(post)
                if post and id and post_id :
                    cursor.execute(""" DELETE FROM POSTS WHERE  post_id=?""",(post_id,))
                    flash('Deleted successfully','alert alert-danger')
                    return redirect("/user/posts")
                else:
                    return redirect("/user/posts")    
        except Exception as e:
            print(e)
            return redirect("/user/posts")        
    except Exception as e:
        print(e)
        return redirect("/user/newsfeed")


@app.route("/user/posts/edit/<post_id>",methods=("GET","POST"))
def editUser(post_id):
    if request.method=="GET":
        try:
            id=user()
            try:
                if post_id and id :
                    with sqlite3.connect('hr.db') as connection:
                        connection.row_factory=sqlite3.Row
                        cursor=connection.cursor()
                        cursor.execute(""" SELECT author_id,post_id,title,description FROM POSTS WHERE post_id=? """,(post_id,))
                        data=cursor.fetchone()
                        connection.commit()
                        if id==data[0]:
                            
                            return render_template("./user/create_feed.html",data=data)
                        else:
                            return "l"    
            except Exception as e :
                print(e)
                return "Error"

        except Exception as e:
            print(e)
            return "failed"        
    else:
        try:
            id=user()
            try:
                title=request.form["title"]
                description=request.form["description"]
                with sqlite3.connect('hr.db') as connection:
                       connection.row_factory=sqlite3.Row
                       cursor=connection.cursor()
                       cursor.execute(""" SELECT author_id,post_id,title,description FROM POSTS WHERE post_id=? """,(post_id,))
                       data=cursor.fetchone()
                       if id==data[0]:
                           cursor.execute(""" UPDATE POSTS SET title=?,description=? WHERE post_id=? """,(title,description,post_id))
                           connection.commit()
                           flash('Updated successfully','alert alert-success')
                           return redirect("/user/posts")
            except:
                return redirect("/user/newsfeed")

        except Exception as e:
            print(e)
            return "error"


@app.post("/user/search")
def UserSearch():
    try :
        id=user()
        search=request.form["search"]
        print(search)

        with sqlite3.connect('hr.db') as connection:
            # connection.row_factory=sqlite3.Row
            cursor=connection.cursor()
            cursor.execute(""" SELECT skills_required,id,company_name,designation FROM OPENINGS """)
            data=cursor.fetchall()
            # print(data)
            # print(data[0]["skills_required"]  )
            arr=[]
            for x in data:
                print(x[0],x[1])
                if x[0]  :

                    c=x[0].upper().find(search.upper())
                    # print(c)
                    if c>=0:
                    
                        # print("works")
                        # print(x[0])
                        arr.append({"id":x[1],"skills_required":x[0],"company_name":x[2],"designation":x[3]})            
                    # print("None")
            arr.reverse()        
            return render_template("./user/jobs.html",data=arr)


    except Exception as e:
        print(e)
        return redirect("/user/signin")
           

    return "success"






if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)
