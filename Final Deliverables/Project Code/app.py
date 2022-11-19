from flask import Flask, render_template, request, redirect, jsonify, make_response, url_for,flash
import sqlite3
from markupsafe import escape
import re
import hashlib
#python_dotenv
from dotenv import load_dotenv
load_dotenv()

import uuid
import jwt
from datetime import datetime, timedelta
import ibm_db 
import os
import base64
import random

import ibm_boto3
from ibm_botocore.client import Config,ClientError
import glob
from werkzeug.utils import secure_filename

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
app = Flask(__name__)

ALLOWED_EXTENSIONS = {'jpg'}

UPLOAD_FOLDER = './static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER





#IBM CLOUD OBJECT STORAGE...............................................................................
COS_ENDPOINT=os.getenv("COS_ENDPOINT")
COS_API_KEY_ID=os.getenv("COS_API_KEY_ID")
COS_INSTANCE_CRN=os.getenv("COS_INSTANCE_CRN")
bucket_name=os.getenv("BUCKET_NAME")
cos=ibm_boto3.resource("s3",
ibm_api_key_id=COS_API_KEY_ID,
ibm_service_instance_id=COS_INSTANCE_CRN,
config=Config(signature_version="oauth"),
endpoint_url=COS_ENDPOINT)



salt = os.getenv("SALT")

ibm_key=os.getenv("DB_CONNECT")
SID_KEY=os.getenv("SID_KEY")
EMAIL_SENDER=os.getenv("SENDER")
SID_SENDER={"name":"Hire-Up","email":EMAIL_SENDER}
ibm_conn=ibm_db.connect(ibm_key,'','')




 
app.config["KEY"] = "Hello"
app.secret_key=os.getenv("FLASK_KEY")
jwt_key=os.getenv("JWT_KEY")
print(jwt_key)

def delete_item(bucket_name, object_name):
    try:
        cos.delete_object(Bucket=bucket_name, Key=object_name)
        print("Item: {0} deleted!\n".format(object_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to delete object: {0}".format(e))       


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def multi_part_upload(bucket_name, item_name, file_path):
    try:
        print("Starting file transfer for {0} to bucket: {1}\n".format(
            item_name, bucket_name))
        # set 5 MB chunks
        part_size = 1024 * 1024 * 5

        # set threadhold to 15 MB
        file_threshold = 1024 * 1024 * 15

        # set the transfer threshold and chunk size
        transfer_config = ibm_boto3.s3.transfer.TransferConfig(
            multipart_threshold=file_threshold,
            multipart_chunksize=part_size
        )

        # the upload_fileobj method will automatically execute a multi-part upload
        # in 5 MB chunks for all files over 15 MB
        with open(file_path, "rb") as file_data:
            cos.Object(bucket_name, item_name).upload_fileobj(
                Fileobj=file_data,
                Config=transfer_config
            )

        print("Transfer for {0} Complete!\n".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to complete multi-part upload: {0}".format(e))


def sendinblue(SID_KEY,SID_SENDER,receiver,subject,html_content):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = SID_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    subject = subject
    sender = SID_SENDER
    replyTo = SID_SENDER
    html_content = html_content
    to = receiver
    params = {"parameter":"My param value","subject":"New Subject"}
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to,  reply_to=replyTo,html_content=html_content, sender=sender, subject=subject)
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(api_response)
    except ApiException as e:
        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)


def verify(token):
    data = jwt.decode(token, jwt_key, algorithms='HS256')
    return data["email"]

def user():
    token = request.cookies.get('token-user')
    data=jwt.decode(token,jwt_key,algorithms='HS256')
    return data["id"]




# -----------------------------------------RECRUITER LOGIN/SIGNIN FUNCTIONS-------------------------------------------------
@app.route("/")
def homeRoute():
    return render_template("./home.html")



@app.route("/hr/auth/<id>")
def authHR(id):
    try:
        if id:
            data = jwt.decode(id, jwt_key, algorithms='HS256')
            val=data["r_num"]
            mail=data["email"]
            sql=f""" SELECT email,isverified FROM RECRUITER WHERE token='{escape(val)}' AND email='{escape(mail)}' """

            stmt=ibm_db.exec_immediate(ibm_conn,sql)
            user=ibm_db.fetch_both(stmt)
            if user:
                if user["EMAIL"] and user["ISVERIFIED"] != "VERIFIED" : 
                    sql=f""" UPDATE RECRUITER SET isverified=? WHERE email='{escape(data["email"])}' """
                    prep_stmt=ibm_db.prepare(ibm_conn,sql)
                    ibm_db.bind_param(prep_stmt,1,"VERIFIED")
                    ibm_db.execute(prep_stmt)
                    return "<div><h1>Successfully Verified</h1><p>You have successfully verified your account</p></div>"
                else :
                    return "<h1>Wrong Operations</h1>"    
            else:
                return "Invalid"        
    except Exception as e:
        print(e)
        return "<h1>Invalid Token</h1>"

@app.route("/user/auth/<id>")
def authuser(id):
    try:
        if id:
            data = jwt.decode(id, jwt_key, algorithms='HS256')
            val=data["r_num"]
            mail=data["email"]
            sql=f""" SELECT email,isverified FROM USERS WHERE token='{escape(val)}' AND email='{escape(mail)}' """

            stmt=ibm_db.exec_immediate(ibm_conn,sql)
            user=ibm_db.fetch_both(stmt)
            if user["EMAIL"] and user["ISVERIFIED"] != "VERIFIED" : 
                sql=f""" UPDATE USERS SET isverified=? WHERE email='{escape(data["email"])}' """
                prep_stmt=ibm_db.prepare(ibm_conn,sql)
                ibm_db.bind_param(prep_stmt,1,"VERIFIED")
                ibm_db.execute(prep_stmt)
                return "<div><h1>Successfully Verified</h1><p>You have successfully verified your account</p></div>"
            else :
                return "<h1>Wrong Operations</h1>"    
    except Exception as e:
        print(e)
        return "<h1>Invalid Token</h1>"








@app.route("/hr/signin", methods=('GET', 'POST'))
def hrSignIn():
    if request.method == "GET":
        
        
        return render_template("./sign/hrsignin.html")
    else:
        email = request.form["email"]
        password = request.form["password"]
        sql=f"SELECT email FROM RECRUITER WHERE email='{escape(email)}'"
        stmt=ibm_db.exec_immediate(ibm_conn,sql)    
        user =ibm_db.fetch_tuple(stmt)
        if user == False:
            flash('Invalid email/password','alert alert-danger')
            return redirect("/hr/signin")
        else:
            db_password = password+salt
            pw_hash = hashlib.md5(db_password.encode())
            sql=f"SELECT email,password,isverified FROM RECRUITER WHERE email='{escape(email)}'"
            stmt=ibm_db.exec_immediate(ibm_conn,sql)
            details = ibm_db.fetch_tuple(stmt)
           

            if pw_hash.hexdigest() == details[1]:
                if (details[2] != "VERIFIED"):
                    flash("You have not Verified Your account Please to verify it ","alert alert-danger")
                    return redirect("/hr/signin")
                token = jwt.encode({"email": email, 'exp': datetime.utcnow(
                )+timedelta(minutes=30)}, jwt_key, algorithm='HS256')
                response = make_response(
                    redirect("/hr/feed"))
                response.set_cookie('token', '')
                response.set_cookie('token-user', '')
                response.set_cookie('token', token)
                return response
            else:
                flash('Invalid email/password ','alert alert-danger')
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
        elif (len(password) >6 == True):
            flash('Password should contain minimum 6 Characters','alert alert-danger')
            return redirect("/hr/signup")   
        else:
            sql=f" SELECT email FROM RECRUITER WHERE email='{escape(email)}'"
            stmt=ibm_db.exec_immediate(ibm_conn,sql)         
            user = ibm_db.fetch_row(stmt)
            if user == False:
                key = uuid.uuid1().hex
                db_password = password+salt
                pw_hash = hashlib.md5(db_password.encode())
                pwd=pw_hash.hexdigest()
                r_num=random.randint(1000, 9000)
                sql_cmd="""INSERT INTO RECRUITER (name,email,phone,password,id,token) VALUES (?,?,?,?,?,?) """
                sql=ibm_db.prepare(ibm_conn,sql_cmd)
                ibm_db.bind_param(sql,1,name)
                ibm_db.bind_param(sql,2,email)
                ibm_db.bind_param(sql,3,phone)
                ibm_db.bind_param(sql,4,pwd)
                ibm_db.bind_param(sql,5,key)
                ibm_db.bind_param(sql,6,r_num)
                ibm_db.execute(sql)
                token = jwt.encode({"email": email, "r_num":r_num}, jwt_key, algorithm='HS256')


                url="http://{}/hr/auth/{}".format(request.headers["host"],token)
                flash('Account created successfully and please do verify through email ','alert alert-success')
                receiver=[{"email":email,"name":name}]
                header=request.headers["host"]
                url="{}/hr/auth/{}".format(header,token)
                subject="Congratulations You have created your account Please verify your account "
                html_content='<html><body><h3> An account is created using the following email </h3><p>Please do verify your account by clicking the <a href="{{url}}"> link </a> {}</p></body></html>'.format(url)

                sendinblue(SID_KEY,SID_SENDER,receiver,subject,html_content)
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
        data = jwt.decode(token, jwt_key, algorithms='HS256')
        sql="SELECT author_id,author_name,title,description,video_url,url,image_url FROM POSTS"
        stmt=ibm_db.exec_immediate(ibm_conn,sql)
        students=[]
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
          students.append(dictionary)
          dictionary = ibm_db.fetch_both(stmt)
        students.reverse()
        return render_template("./feed/feed.html",data=students)
        
    except Exception as e:
        print(e)
        return redirect("/hr/signin")
       
@app.route("/hr/feed/<id>")
def hrOneFeed(id):
    try:
        token = request.cookies.get('token')
        data = jwt.decode(token, jwt_key, algorithms='HS256')

        return render_template("./feed/oneFeed.html")
    except:
        return redirect("/hr/signin")


@app.route("/hr/application") 
def hrApplication():
    try:
        token = request.cookies.get('token')
        email = verify(token)
        data=[]
        sql=f""" SELECT author_hr,post_id,user_id,viewed FROM APPLICATIONS WHERE author_hr='{escape(email)}'"""
        stmt=ibm_db.exec_immediate(ibm_conn,sql)
        item=ibm_db.fetch_both(stmt)
        while item != False:
    # print ("The Name is : ",  dictionary)
            data.append(item)
            item= ibm_db.fetch_both(stmt)
        details=[]
        if data:
            application=[]
            if data:
                for x in data:
                    sql=f"""SELECT name,about,designation,id,image_url FROM USERS WHERE id='{escape(x["USER_ID"])}'"""
                    stmt=ibm_db.exec_immediate(ibm_conn,sql)
                    user=ibm_db.fetch_tuple(stmt)
                    sql=f""" SELECT title,designation,id FROM OPENINGS WHERE id='{escape(x["POST_ID"])}'"""
                    stmt=ibm_db.exec_immediate(ibm_conn,sql)
                    post=ibm_db.fetch_tuple(stmt)

                    if user and post :
                        if x["VIEWED"]:
                            application=(user+post+("viewed",)  )
                        else :
                            application=(user+post)    
                    details.append(application)
                
                details.reverse()
                return render_template("./application/applications.html",data=details)
            else:
                return render_template("./application/applications.html")    
        else:
            return render_template("./application/applications.html")        
    except Exception as e:
        print(e)
        flash('Something went wrong','alert alert-danger')
        
        return redirect("/hr/signin")

@app.route("/hr/views/<id>")
def viewNewsfeeds(id):

    try:
       
       token=request.cookies.get('token')
       email=verify(token)
      
       
       sql=f""" SELECT name,email,phone,about,designation,school,skills,project,description,image_url,id FROM USERS WHERE id='{escape(id)}' """
       stmt=ibm_db.exec_immediate(ibm_conn,sql)
       user=ibm_db.fetch_both(stmt)
       return render_template('./application/view_application.html',data=user)
    except Exception as e:
        print(e)
        flash('Something went wrong','alert alert-danger')
        return redirect("/hr/signin")    


@app.route("/hr/view/<id>") 
def viewApplication(id):
    try:
        search=request.args['search']
        token=request.cookies.get('token')
        email=verify(token)
        sql=f""" SELECT viewed FROM APPLICATIONS   WHERE post_id='{escape(search)}' AND user_id='{escape(id)}'"""
        stmt=ibm_db.exec_immediate(ibm_conn,sql)
        isviewed=ibm_db.fetch_both(stmt)
        if isviewed["VIEWED"]==None:
            sql=""" UPDATE  APPLICATIONS SET viewed=?  WHERE post_id=? AND user_id=?"""
            view="VIEWED"
            prep_stmt=ibm_db.prepare(ibm_conn,sql)
            ibm_db.bind_param(prep_stmt,1,view)
            ibm_db.bind_param(prep_stmt,2,search)
            ibm_db.bind_param(prep_stmt,3,id)
            ibm_db.execute(prep_stmt)
            
        
        sql=f""" SELECT name,email,phone,about,designation,school,skills,project,description,image_url,id FROM USERS WHERE id='{escape(id)}' """
        stmt=ibm_db.exec_immediate(ibm_conn,sql)
        user=ibm_db.fetch_both(stmt)
        return render_template('./application/view_application.html',data=user)
    except Exception as e:
        print(e)
        flash('Something went wrong','alert alert-danger')
        return redirect("/hr/signin")   

@app.route("/hr/msg/<id>" ,methods=("GET","POST")) ##MAil Notifications
def viewApplicationPOST(id):
    try:
        token=request.cookies.get('token')
        email=verify(token)
        if request.method=="GET":

            return redirect("/hr/feed")
        else:
            msg=request.form["message"]
            sql=f""" SELECT name,email,phone FROM RECRUITER WHERE email='{escape(email)}' """
            stmt=ibm_db.exec_immediate(ibm_conn,sql)
            user=ibm_db.fetch_assoc(stmt)
            if user and msg and id:
                sql=f""" SELECT email FROM USERS WHERE id='{escape(id)}' """
                stmt=ibm_db.exec_immediate(ibm_conn,sql)
                user_Info=ibm_db.fetch_assoc(stmt)
                if user_Info:

                    subject=" An Recruiter has showed intrest in your Profile "
                    html_content="<html><body><h3> An Recruiter ({}) has showed intrest in your Profile </h3><p> {}</p> <h4>For more information</h4></body><p>Phone:{} </p> <p>email:{}</p></html>".format(user["NAME"],msg,user["PHONE"],user["EMAIL"])
                    receiver=[{"email":user_Info["EMAIL"]}]
                    sendinblue(SID_KEY,SID_SENDER,receiver,subject,html_content)
                    flash("Successfully notified the user " ,"alert alert-success")
                    return redirect("/hr/feed")
            flash("Something went wrong ","alert alert-danger")
            return  redirect("/hr/feed")    


    except Exception as e:
        print(e)
        return redirect("/hr/signin")

# TO ADD PROFILE PICTURE

@app.route("/hr/profile/img",methods=["GET","POST"])##Currently Working on this function............
def hrProfileImg():
    try:
        token = request.cookies.get('token')
        email = verify(token)
        if request.method=="GET":
            return render_template("/profile/add_image.html")
        else:
            file=request.files["image"]
            sql=f""" SELECT id,image_url FROM RECRUITER WHERE email='{escape(email)}' """
            stmt=ibm_db.exec_immediate(ibm_conn,sql)
            info=ibm_db.fetch_tuple(stmt)
            if info[1]==None:
                if file and allowed_file(file.filename) :
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    bucket = bucket_name
                    fname = info[0]
                    f = file
                    multi_part_upload(bucket, fname, "./static/uploads/{}".format(filename))
                    link="https://userphotos.s3.jp-tok.cloud-object-storage.appdomain.cloud/{}".format(fname)
                   
                    sql=f""" UPDATE RECRUITER SET image_url=? WHERE email='{escape(email)}' """
                    prep_stmt=ibm_db.prepare(ibm_conn,sql)
                    ibm_db.bind_param(prep_stmt,1,link)
                    ibm_db.execute(prep_stmt)
                    os.remove("./static/uploads/{}.jpg".format(filename))
                    flash("Successfully updated profile picture ","alert alert-success")    
                    return redirect("/hr/profile")
            else:
                if file and allowed_file(file.filename) :
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    bucket = bucket_name
                    fname = info[0]
                    f = file
                    multi_part_upload(bucket, fname, "./static/uploads/{}".format(filename))
                    os.remove("./static/uploads/{}".format(filename))
                    flash("You have updated your profile picture","alert alert-success")
                    return redirect("/hr/profile")
            flash('Uploaded images are missing/not in JPEG format',"alert alert-danger")    
            return  redirect("/hr/profile")  
                    

            

    except Exception as e:
        print(e)
        flash('Something went wrong','alert alert-danger')
        return redirect("/hr/signin")



# TO VIEW THE PROFILE
@app.route("/hr/profile") 
def hrProfile():
    try:
        token = request.cookies.get('token')
        email = verify(token)
        sql=f"""
            
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
            in_url,
            image_url 
             FROM RECRUITER WHERE email='{escape(email)}'"""
        stmt=ibm_db.exec_immediate(ibm_conn,sql)
        info=ibm_db.fetch_tuple(stmt)
        if not info:
            return redirect("/hr/logout")
        else:
            return render_template("./profile/viewProfile.html",data=info)    
    except Exception as e:
        print(e)
        flash('Something went wrong','alert alert-danger')
        return redirect("/hr/signin")

# VIEW THE RECRUITERS PROFILE AND EDIT THE INFORMATION==============================
@app.route("/hr/profile/edit") #******
def hrProfileEdit():
    try:
        token = request.cookies.get('token')
        email = verify(token)
        sql=f""" 
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
             FROM RECRUITER WHERE email='{escape(email)}'"""
        stmt=ibm_db.exec_immediate(ibm_conn,sql)
        data=ibm_db.fetch_tuple(stmt)
        
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
        try:
            email = verify(token)
            name=request.form["name"]     
            about_me=request.form["about_me"]
            designation=request.form['designation']
            experience=request.form['experience']
            url=request.form['url']
            company_name=request.form['company_name']
            company_description=request.form['company_description']
            location=request.form["location_in"]
            website=request.form['website']
            if not id:
                return redirect("/hr/profile")
            
            sql=f"SELECT id FROM RECRUITER WHERE email='{escape(email)}'"
            stmt=ibm_db.exec_immediate(ibm_conn,sql)
            data=ibm_db.fetch_tuple(stmt)
            
            if data[0]==id:
                sql=f"""
        
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
                
                WHERE email='{escape(email)}' """
                prep_stmt=ibm_db.prepare(ibm_conn,sql)
                ibm_db.bind_param(prep_stmt, 1, name)
                ibm_db.bind_param(prep_stmt, 2, about_me)
                ibm_db.bind_param(prep_stmt, 3, designation)
                ibm_db.bind_param(prep_stmt, 4, experience)
                ibm_db.bind_param(prep_stmt, 5, url)
                ibm_db.bind_param(prep_stmt, 6, company_name)
                ibm_db.bind_param(prep_stmt, 7, company_description)
                ibm_db.bind_param(prep_stmt, 8, location)
                ibm_db.bind_param(prep_stmt, 9, website)
                ibm_db.execute(prep_stmt)
                return redirect("/hr/profile")

        except Exception as e:
            print(e)
            return redirect("/hr/signin")




@app.route("/hr/profile/pwd", methods=("GET", "POST"))
def hrProfileEditPWD():

    if request.method == "GET":

        try:
            token = request.cookies.get('token')
            email = verify(token)
            return render_template("./profile/passwordReset.html")

        except:
            return redirect("/hr/signin")

    else:
        try:
            token = request.cookies.get('token')
            email = verify(token)
            password = request.form["password"]
            newPWD = request.form['newPassword']
            confirmPWD = request.form['confirmPassword']
            sql=f""" SELECT password FROM RECRUITER WHERE email='{escape(email)}' """
            stmt=ibm_db.exec_immediate(ibm_conn,sql)
            user=ibm_db.fetch_both(stmt)
            if (user):
                db_password = password+salt
                pw_hash = hashlib.md5(db_password.encode())
                if user["PASSWORD"]==pw_hash.hexdigest() and newPWD==confirmPWD and password!=newPWD and len(newPWD)>=6:
                    new_pwd=newPWD+salt
                    new_hash=hashlib.md5(new_pwd.encode())
                    sql=f"UPDATE  RECRUITER SET password=? WHERE email='{escape(email)}'"
                    prep_stmt=ibm_db.prepare(ibm_conn,sql)
                    ibm_db.bind_param(prep_stmt,1,new_hash.hexdigest())
                    ibm_db.execute(prep_stmt)
                    flash("Password Changed Successfully","alert alert-success")
                    return  redirect("/hr/profile")
            else:
                flash("Password did not match/Entered Wrong Current Password","alert alert-danger")
                return  redirect("/hr/profile/pwd")        


            flash("Password did not match","alert alert-danger")
            return redirect("/hr/profile/pwd")
        except Exception as e:
            print(e)
            return redirect("/hr/signin")

#VIEWING OPENING
@app.route("/hr/openings") 
def hrOpenings():
    try:
        token = request.cookies.get('token')
        email = verify(token)
        sql=f"SELECT id,title,company_name,designation,salary_range,skills_required,roles_responsibilities,company_description,location,website,author FROM OPENINGS WHERE author='{escape(email)}'"
        stmt = ibm_db.exec_immediate(ibm_conn, sql)
        data=[]
        dictionary = ibm_db.fetch_tuple(stmt)
        while dictionary != False:
          data.append(dictionary)
          dictionary = ibm_db.fetch_both(stmt)

        data.reverse()

        return render_template("./openings/viewOpening.html",data=data)
    except Exception as e:
        print(e ,"This block")
        
    
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
            skills_required = request.form["skills_required"].upper()
            roles_responsibilities = request.form["roles_responsibilities"]
            company_description = request.form["company_description"]
            location = request.form["location"]
            website = request.form["website"]
            author = email
            key = uuid.uuid1().hex
            sql=f"""SELECT image_url FROM RECRUITER WHERE email='{escape(email)}' """
            stmt=ibm_db.exec_immediate(ibm_conn,sql)
            image=ibm_db.fetch_assoc(stmt)
            sql="INSERT INTO OPENINGS (id,title,company_name,designation,salary_range,skills_required,roles_responsibilities,company_description,location,website,author,image_url) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
            prep_stmt=ibm_db.prepare(ibm_conn,sql)
            ibm_db.bind_param(prep_stmt,1,key)
            ibm_db.bind_param(prep_stmt,2,title)
            ibm_db.bind_param(prep_stmt,3,company_name)
            ibm_db.bind_param(prep_stmt,4,designation)
            ibm_db.bind_param(prep_stmt,5,salary_range)
            ibm_db.bind_param(prep_stmt,6,skills_required)
            ibm_db.bind_param(prep_stmt,7,roles_responsibilities)
            ibm_db.bind_param(prep_stmt,8,company_description)
            ibm_db.bind_param(prep_stmt,9,location)
            ibm_db.bind_param(prep_stmt,10,website)
            ibm_db.bind_param(prep_stmt,11,author)
            ibm_db.bind_param(prep_stmt,12,image["IMAGE_URL"])
            ibm_db.execute(prep_stmt)
            Total_skills=[]
            sql="SELECT email,skills,name FROM USERS "
            stmt=ibm_db.exec_immediate(ibm_conn,sql)
            user_skills=ibm_db.fetch_assoc(stmt)

            while user_skills != False:
                Total_skills.append(user_skills)
                user_skills=ibm_db.fetch_both(stmt)

            required_Job_Skills=skills_required.replace(" ","")
            req_skills=required_Job_Skills.split(",")
            user_list=[]

            for user in Total_skills:
                for skill in req_skills:
                    if user["SKILLS"]:
                        a=user["SKILLS"].upper().find(skill)
                        if a>=0:
                            user_list.append({"email":user["EMAIL"],"name":user["NAME"]})
                            break
                    
            if user_list:
                receiver=user_list
                subject="Based on your skillset an Job opening is updated"
                header=request.headers["host"]
                html_content="<html><body><h3>An Job alert is updated where it matches your Skillset </h3><p>Click <a href='{}/user/view_application/{}'>here</a> to view the application</p></body></html>".format(header,key)
                sendinblue(SID_KEY,SID_SENDER,receiver,subject,html_content)




            flash('You have successfully created the opening','alert alert-success')
            return redirect('/hr/openings')

        except Exception as e:
            print(e)
            return redirect('/hr/signin')


# DELETEING THE  OPENINGS
@app.route("/hr/opening/<id>") 
def deleteOpening(id):
    try:
        token = request.cookies.get('token')
        email = verify(token)
        sql=f""" SELECT id FROM OPENINGS WHERE id='{escape(id)}'"""
        stmt=ibm_db.exec_immediate(ibm_conn,sql)
        data=ibm_db.fetch_tuple(stmt)
        if not data:
            return redirect("/hr/openings")
        else:
            sql=f""" DELETE FROM OPENINGS  WHERE id='{escape(data[0])}' """
            ibm_db.exec_immediate(ibm_conn,sql)
            sql=f""" SELECT post_id FROM APPLICATIONS WHERE post_id='{escape(data[0])}'"""
            stmt=ibm_db.exec_immediate(ibm_conn,sql)
            applicant=ibm_db.fetch_row(stmt)
            if not applicant:
                flash('Deleted Successfully','alert alert-danger')
                return  redirect("/hr/openings") 

            else:

                sqls=f""" DELETE FROM  APPLICATIONS WHERE post_id='{escape(data[0])}' """
                ibm_db.exec_immediate(ibm_conn,sqls)
            
                flash('Deleted Successfully','alert alert-danger')
                return  redirect("/hr/openings") 

    except Exception as e:
        print(e)    
        return redirect("hr/signin")




#Editing the openings 
@app.route("/hr/openings/edit/<id>",methods=('GET','POST')) 
def hrOpeningsOne(id):
    if request.method=="GET":
        try:
            token = request.cookies.get('token')
            email = verify(token)
            if not id:
                return render_template("./openings/oneOpening.html")
            sql=f"""SELECT id,author FROM OPENINGS WHERE id='{escape(id)}' """
            stmt=ibm_db.exec_immediate(ibm_conn,sql)
            data=ibm_db.fetch_tuple(stmt)
            if not data :
                return redirect("/hr/openings")    
            elif email== data[1]:
                sql=f""" SELECT 
                id,
                title,company_name,
                designation,
                salary_range,
                skills_required,
                roles_responsibilities,
                company_description,
                location,website,
                author
                FROM OPENINGS WHERE id='{escape(id)}'"""
                stmt=ibm_db.exec_immediate(ibm_conn,sql)
                data=ibm_db.fetch_tuple(stmt)
                
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
        author= email
        sql=f"""SELECT id,author FROM OPENINGS WHERE id='{escape(id)}'"""
        stmt=ibm_db.exec_immediate(ibm_conn,sql)
        data=ibm_db.fetch_tuple(stmt)
        if not data :
            return redirect("/hr/openings")    
        elif email== data[1]:
            sql=f"""
            UPDATE OPENINGS SET 
            title=?,
            company_name=?,designation=?,
            salary_range=?,
            skills_required=? ,
            roles_responsibilities=? ,
            company_description=?,
            location=?,
            website=?
            WHERE id='{escape(id)}' """
            prep_stmt=ibm_db.prepare(ibm_conn,sql)
            ibm_db.bind_param(prep_stmt,1,title)
            ibm_db.bind_param(prep_stmt,2,company_name)
            ibm_db.bind_param(prep_stmt,3,designation)
            ibm_db.bind_param(prep_stmt,4,salary_range)
            ibm_db.bind_param(prep_stmt,5,skills_required)
            ibm_db.bind_param(prep_stmt,6,roles_responsibilities)
            ibm_db.bind_param(prep_stmt,7,company_description)
            ibm_db.bind_param(prep_stmt,8,location)
            ibm_db.bind_param(prep_stmt,9,website)
            ibm_db.execute(prep_stmt)
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
        sql=f""" SELECT 
                id,
                title,company_name,
                designation,
                salary_range,
                skills_required,
                roles_responsibilities,
                company_description,
                location,website,
                author
                FROM OPENINGS WHERE id='{escape(id)}'""" 
        stmt=ibm_db.exec_immediate(ibm_conn,sql)        
        data=ibm_db.fetch_tuple(stmt) 
        if not data:
            return redirect('/hr/openings')
        else:
            
            return render_template("./openings/viewOneopening.html",details=data)    
    



    except Exception as e:
        print(e)
        return redirect("/hr/signin")   







# ---------------------------------------------------RECRUITER FUNCTIONS FINISHED --------------------------------------

#----------------------------------------------------USER FUNCTION STARTED ---------------------------------------------

@app.route("/user/signin",methods=["POST","GET"]) #Completed
def userlogin():
    if request.method=="GET":
        return render_template("./user/signin.html")

    else:
        email=request.form["email"]
        password=request.form["password"]
        sql=f"""SELECT email,password,id,isverified FROM users WHERE email='{escape(email)}'"""
        stmt=ibm_db.exec_immediate(ibm_conn,sql)
        user=ibm_db.fetch_tuple(stmt)
        db_password=password+salt
        pw_hash = hashlib.md5(db_password.encode()).hexdigest()
        
        
        if not email or not password or not user:
            flash('Invalid Credentials','alert alert-danger')
            return render_template("./user/signin.html")
        if user:
            if (user[3] != "VERIFIED"):
                    flash("You have not Verified Your account Please to verify it ","alert alert-danger")
                    return redirect("/user/signin")
            if pw_hash==user[1]:
                token = jwt.encode({"id": user[2], 'exp': datetime.utcnow(
                )+timedelta(minutes=30)}, jwt_key, algorithm='HS256')
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



@app.route("/user/signup",methods=["POST","GET"]) #Completed
def signup():
    try:
        
        if request.method=="GET":
            return render_template("./user/signup.html")

        else:
            name=request.form["name"]
            email=request.form["email"]
            phone=request.form["number"]
            password=request.form["password"]
            re_password=request.form["re-password"]
            key=uuid.uuid1().hex

            if not name or not email or not phone or not password or not re_password:
                flash('Incorrect Credentials','alert alert-danger')
                return redirect("/user/signup")
            sql=f"""SELECT id FROM USERS WHERE email='{escape(email)}'"""
            stmt=ibm_db.exec_immediate(ibm_conn,sql)

            data=ibm_db.fetch_tuple(stmt)
            

            if password==re_password and not data :


                db_password=password+salt
                pw_hash = hashlib.md5(db_password.encode())
                r_num=random.randint(1000, 9000)
                sql=f"""INSERT INTO users (id,name,email,phone,password,token) VALUES (?,?,?,?,?,?) """
                prep_stmt=ibm_db.prepare(ibm_conn,sql)
                ibm_db.bind_param(prep_stmt,1,key)
                ibm_db.bind_param(prep_stmt,2,name)
                ibm_db.bind_param(prep_stmt,3,email)
                ibm_db.bind_param(prep_stmt,4,phone)
                ibm_db.bind_param(prep_stmt,5,pw_hash.hexdigest())
                ibm_db.bind_param(prep_stmt,6,r_num)
                ibm_db.execute(prep_stmt)
                token = jwt.encode({"email": email, "r_num":r_num}, jwt_key, algorithm='HS256')
                url="{}/user/auth/{}".format(request.headers["host"],token)
                flash('Account created successfully and please do verify through email ','alert alert-success')
                receiver=[{"email":email,"name":name}]
                header=request.headers["host"]
                url="{}/user/auth/{}".format(header,token)
                subject="Congratulations You have created your account Please verify your account "
                html_content="<html><body><h3>An Job alert is updated where it matches your Skillset </h3><p>Click here on the link {}</p></body></html>".format(url)
                sendinblue(SID_KEY,SID_SENDER,receiver,subject,html_content)


                return redirect("/user/signin")
            else:
                flash('Incorrect Credentials','alert alert-danger')
                return redirect("/user/signup")
    except Exception as e:
        print(e)
        return redirect("/user/signup")

#ADD image

@app.route("/user/profile/img",methods=["GET","POST"])##Currently Working on this function............
def userProfileImg():
    try:
        id=user()
        if request.method=="GET":
            return render_template("/user/add_image.html")
        else:
            file=request.files["image"]
            sql=f""" SELECT id,image_url FROM USERS WHERE id='{escape(id)}' """
            stmt=ibm_db.exec_immediate(ibm_conn,sql)
            info=ibm_db.fetch_tuple(stmt)
            if info[1]==None:
                if file and allowed_file(file.filename) :
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    bucket = bucket_name
                    fname = info[0]
                    f = file
                    multi_part_upload(bucket, fname, "./static/uploads/{}".format(filename))
                    link="https://userphotos.s3.jp-tok.cloud-object-storage.appdomain.cloud/{}".format(fname)
                   
                    sql=f""" UPDATE USERS SET image_url=? WHERE id='{escape(id)}' """
                    prep_stmt=ibm_db.prepare(ibm_conn,sql)
                    ibm_db.bind_param(prep_stmt,1,link)
                    ibm_db.execute(prep_stmt)
                    os.remove("./static/uploads/{}".format(filename))
                    flash("Successfully updated profile picture ","alert alert-success")    
                    return redirect("/user/profile")
            else:

                if file and allowed_file(file.filename) :
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    bucket = bucket_name
                    fname = info[0]
                    f = file
                    multi_part_upload(bucket, fname, "./static/uploads/{}".format(filename))
                    os.remove("./static/uploads/{}".format(filename))

                    flash("You have updated your profile picture ","alert alert-success")
                    return redirect("/user/profile")
            flash('Uploaded images are missing/not in JPEG format',"alert alert-danger")    
            return   redirect("/user/profile")  
                    

            

    except Exception as e:
        print(e)
        flash('Something went wrong','alert alert-danger')
        return redirect("/user/signin")




@app.route("/user/profile") #Completed
def userprofile():
    try:
        id=user()
        sql=f""" SELECT id ,name,email,phone,password,about,designation,school,skills,project,description,image_url FROM USERS WHERE id='{escape(id)}'"""
        val=[]
        stmt=ibm_db.exec_immediate(ibm_conn,sql)
        data=ibm_db.fetch_both(stmt)
        val.append(data)
        return render_template("./user/profile.html",data=val)
        
    
    except Exception as e:
        print(e)  
        return redirect("/user/signin")

@app.route("/user/profile/editprofile",methods=["POST","GET"]) ##Completed
def editProfiles():

    try:
        id=user()
    


        if request.method=="GET":
            try:
                sql=f""" SELECT id,name,about,designation,school,skills,phone,project,description FROM USERS WHERE id='{escape(id)}' """
                stmt=ibm_db.exec_immediate(ibm_conn,sql)
                data=ibm_db.fetch_both(stmt)
                return render_template("./user/editprofile.html",data=data)

            except Exception as e:
                    return redirect("/user/profile")
        else:
            name=request.form["name"]
            about=request.form["about"]
            phone=request.form["phone"]
            designation=request.form["designation"]
            school=request.form["school"]
            skills=request.form["skills"]
            project=request.form["project"]
            description=request.form["description"]


            sql=f"UPDATE  USERS SET name=?,about=?,phone=?,designation=?,school=?,skills=?,project=?,description=? WHERE id='{escape(id)}' "
            
            prep_stmt=ibm_db.prepare(ibm_conn,sql)
            ibm_db.bind_param(prep_stmt,1,name)
            ibm_db.bind_param(prep_stmt,2,about)
            ibm_db.bind_param(prep_stmt,3,phone)
            ibm_db.bind_param(prep_stmt,4,designation)
            ibm_db.bind_param(prep_stmt,5,school)
            ibm_db.bind_param(prep_stmt,6,skills)
            ibm_db.bind_param(prep_stmt,7,project)
            ibm_db.bind_param(prep_stmt,8,description)
            ibm_db.execute(prep_stmt)


            
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
@app.route("/user/jobs") #Descending_Order
def jobs():
    try:
        id=user()
        sql=""" SELECT  id,
            title,
            company_name,
            designation ,
            salary_range,
            skills_required,
            roles_responsibilities,
            company_description,
            location,
            website,
            image_url,
            author FROM OPENINGS """
        students=[]    
        
        stmt=ibm_db.exec_immediate(ibm_conn,sql)    
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
          # print ("The Name is : ",  dictionary)
          students.append(dictionary)
          dictionary = ibm_db.fetch_both(stmt)
          
        if students:
            students.reverse()
        
        return render_template("./user/jobs.html",data=students )
    
    except:
        return redirect("/user/signin")


@app.route("/user/view_application/<key>") #Completed
def viewOneJobOpenings(key):
    try:
        id=user()
        sql=f""" SELECT title,
                id,
                company_name,
                designation ,
                salary_range,
                skills_required,
                roles_responsibilities,
                company_description,
                location,
                image_url,
                website,
                author FROM OPENINGS WHERE id='{escape(key)}' """
        stmt=ibm_db.exec_immediate(ibm_conn,sql)
        data=ibm_db.fetch_both(stmt)
        
        sql=f""" SELECT name FROM RECRUITER WHERE email='{escape(data["AUTHOR"])}'  """
        stmt=ibm_db.exec_immediate(ibm_conn,sql)
        hr=ibm_db.fetch_tuple(stmt)
        

        sql=f""" SELECT author_hr FROM APPLICATIONS WHERE post_id='{escape(key)}' AND user_id='{escape(id)}'  """
        stmt=ibm_db.exec_immediate(ibm_conn,sql)
        isApplied=ibm_db.fetch_tuple(stmt)
        button_enable=False
        if isApplied:            
            button_enable=True
        
        return render_template("./user/jobs_view.html" ,data=data,hr=hr[0],button=button_enable)
    except Exception as e:
        print(e)
        return redirect("/user/signin")

@app.route("/user/apply/<job_id>") #Completed
def applicationApply(job_id):
    try:
        user_id=user()
        sql=f""" SELECT author FROM OPENINGS WHERE id='{escape(job_id)}' """
        stmt=ibm_db.exec_immediate(ibm_conn,sql)
        data=ibm_db.fetch_tuple(stmt)
        sql=""" INSERT INTO APPLICATIONS  (author_hr,post_id,user_id) VALUES (?,?,?) """
        prep_stmt=ibm_db.prepare(ibm_conn,sql)
        ibm_db.bind_param(prep_stmt,1,data[0])
        ibm_db.bind_param(prep_stmt,2,job_id)
        ibm_db.bind_param(prep_stmt,3,user_id)
        ibm_db.execute(prep_stmt)
        receiver=[{"email":data[0]}]
        subject="You Have a New Job application "
        html_content='<html><body><h3> An user have applied for your Job posting kindly check the platform for more.... </h3></p></body></html>'
        sendinblue(SID_KEY,SID_SENDER,receiver,subject,html_content)

        flash('Applied Successfully','alert alert-success') 
        return redirect("/user/jobs")
    except Exception as e:
        return redirect("/user/signin")




@app.route("/user/newsfeed")
def addproject(): #Completed
    try:
        id=user()
        try :
            posts=[]
            sql=""" SELECT author_id,post_id,author_name,title,description,url,video_url,image_url FROM POSTS """
            stmt=ibm_db.exec_immediate(ibm_conn,sql)
            data=ibm_db.fetch_both(stmt)
            while data != False:
              # print ("The Name is : ",  dictionary)
              posts.append(data)
              data = ibm_db.fetch_both(stmt)
            posts.reverse()
            return render_template("./user/newsfeed.html",data=posts)
        
        except Exception as e:
            print(e) 
            return redirect("/user/signin")    
    except Exception as e:
        print(e)
        return redirect('/user/signin')

@app.route("/user/feed/new",methods=("GET","POST"))#Completed----------------
def addfeednews():
    if request.method=="POST":
        try:
            id=user()
            title=request.form["title"]
            description=request.form["description"]
            video_url=request.form["video_url"]
            project_url=request.form["project_url"]
            if title and description and id :
                sql=f""" SELECT name,image_url FROM USERS WHERE id='{escape(id)}' """
                stmt=ibm_db.exec_immediate(ibm_conn,sql)
                name=ibm_db.fetch_tuple(stmt)
                if name:    
                    post_id=uuid.uuid1().hex
                    sql=""" INSERT INTO POSTS  (author_name,author_id,title,description,post_id,video_url,url,image_url) VALUES (?,?,?,?,?,?,?,?) """
                    prep_stmt=ibm_db.prepare(ibm_conn,sql)
                    ibm_db.bind_param(prep_stmt,1,name[0])
                    ibm_db.bind_param(prep_stmt,2,id)
                    ibm_db.bind_param(prep_stmt,3,title)
                    ibm_db.bind_param(prep_stmt,4,description)
                    ibm_db.bind_param(prep_stmt,5,post_id)
                    ibm_db.bind_param(prep_stmt,6,video_url)
                    ibm_db.bind_param(prep_stmt,7   ,project_url)
                    ibm_db.bind_param(prep_stmt,8  ,name[1])
                    ibm_db.execute(prep_stmt)
                    flash('Post uploded successfully','alert alert-success')
                    return redirect("/user/posts")
            else:
                flash('Incorrect Input data','alert alert-danger')
                return redirect("/user/newsfeed")
        except Exception as e:
            print(e,"Error")
            return redirect("/user/newsfeed")

    else:    
        try:
            id=user()
            return render_template("./user/create_feed.html")
        except Exception as e:
            print(e)
            return redirect('/user/signin')

@app.route("/user/posts")#Completed......
def userPost():
    try:
        id=user()
        try:
            posts=[]
            sql=f""" SELECT author_name,author_id,title,description,post_id,video_url,url,image_url FROM POSTS WHERE author_id='{escape(id)}' """
            stmt=ibm_db.exec_immediate(ibm_conn,sql)
            data=ibm_db.fetch_both(stmt)
            while data != False:
              # print ("The Name is : ",  dictionary)
              posts.append(data)
              data = ibm_db.fetch_both(stmt)
            if posts:
                posts.reverse()
            return render_template("./user/view_post.html",data=posts)
        except Exception as e:
            print(e)
            return redirect("/user/newsfeed")


    except Exception as e:
        print(e)
        return redirect("/user/signin")    

@app.route("/user/delete/<post_id>")# Completed
def userPostDelete(post_id):
    try:
        id=user()
        try:
            sql=f""" SELECT title FROM POSTS WHERE post_id='{escape(post_id)}' """
            stmt=ibm_db.exec_immediate(ibm_conn,sql)
            post=ibm_db.fetch_both(stmt)
           
            if post and id and post_id :
                sql=f""" DELETE FROM POSTS WHERE  post_id='{escape(post_id)}'"""
                ibm_db.exec_immediate(ibm_conn,sql)
                flash('Deleted successfully','alert alert-danger')
                return redirect("/user/posts")
            else:
                return redirect("/user/posts")    
        except Exception as e:
            print(e)
            return redirect("/user/posts")        
    except Exception as e:
        print(e)
        return redirect("/user/signin")


@app.route("/user/posts/edit/<post_id>",methods=("GET","POST")) #Completed------------------------
def editUser(post_id):
    if request.method=="GET":
        try:
            id=user()
            try:
                if post_id and id :
                    
                    sql=f"""SELECT author_id,post_id,title,description,url,video_url FROM POSTS WHERE post_id='{escape(post_id)}' """
                    stmt=ibm_db.exec_immediate(ibm_conn,sql)
                    data=ibm_db.fetch_tuple(stmt)
                    if id==data[0]:
                        
                        return render_template("./user/create_feed.html",data=data)
                    else:
                        return redirect("/user/posts")    
            except Exception as e :
                print(e)
                flash('Something went wrong','alert alert-danger')
                return redirect("/user/newsfeed")
        except Exception as e:
            print(e)
            flash('Something went wrong','alert alert-danger')
            return redirect("/user/signin")   
    else:
        try:
            id=user()
            try:
                title=request.form["title"]
                description=request.form["description"]
                video_url=request.form["video_url"]
                project_url=request.form["project_url"]
                sql=f""" SELECT author_id,post_id,title,description FROM POSTS WHERE post_id='{escape(post_id)}' """
                stmt=ibm_db.exec_immediate(ibm_conn,sql)     
                data=ibm_db.fetch_tuple(stmt)
                if id==data[0]:
                    sql=f""" UPDATE POSTS SET title=?,description=?,video_url=?,url=? WHERE post_id='{escape(post_id)}' """
                    prep_stmt=ibm_db.prepare(ibm_conn,sql)
                    ibm_db.bind_param(prep_stmt,1,title)
                    ibm_db.bind_param(prep_stmt,2,description)
                    ibm_db.bind_param(prep_stmt,3,video_url)
                    ibm_db.bind_param(prep_stmt,4,project_url)
                    ibm_db.execute(prep_stmt)
                    flash('Updated successfully','alert alert-success')
                    return redirect("/user/posts")
                flash('Something Went Wrong','alert alert-danger')
                return redirect("/user/posts")
            except:
                return redirect("/user/newsfeed")

        except Exception as e:
            print(e)
            flash('Something went wrong','alert alert-danger')
            return redirect("/user/signin")
            

@app.post("/user/search")
def UserSearch():
    try :
        id=user()
        search=request.form["search"]
        sql=""" SELECT skills_required,id,company_name,designation FROM OPENINGS """
        stmt=ibm_db.exec_immediate(ibm_conn,sql)
        arr=[]
        arrs=[]
        dictionary = ibm_db.fetch_tuple(stmt)
        while dictionary != False:
    # print ("The Name is : ",  dictionary)
            arr.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)
        
        for x in arr:
            if x[1]  :
                c=x[0].upper().find(search.upper())
                # print(c)
                if c>=0:
                
                    # print("works")
                    # print(x[0])
                    arrs.append({"ID":x[1],"SKILLS_REQUIRED":x[0],"COMPANY_NAME":x[2],"DESIGNATION":x[3]})            
                # print("None")
        arr.reverse()      
        return render_template("./user/jobs.html",data=arrs)


    except Exception as e:
        print(e)
        flash('Something went wrong','alert alert-danger')
        return redirect("/user/signin")
           


@app.route("/user/profile/pwd", methods=("GET", "POST"))
def userProfileEditPWD():

    if request.method == "GET":

        try:
            id=user()
            return render_template("./user/passwordReset.html")

        except Exception as e:
            print(e)
            return redirect("/user/signin")

    else:
        try:
            
            id=user()
        
            password = request.form["password"]
            newPWD = request.form['newPassword']
            confirmPWD = request.form['confirmPassword']
            sql=f""" SELECT password FROM USERS WHERE id='{escape(id)}' """
            stmt=ibm_db.exec_immediate(ibm_conn,sql)
            users=ibm_db.fetch_both(stmt)
            if (users):
                db_password = password+salt
                pw_hash = hashlib.md5(db_password.encode())
                if users["PASSWORD"]==pw_hash.hexdigest() and newPWD==confirmPWD and password!=newPWD and len(newPWD)>=6:
                    new_pwd=newPWD+salt
                    new_hash=hashlib.md5(new_pwd.encode())
                    sql=f"UPDATE  USERS SET password=? WHERE id='{escape(id)}'"
                    prep_stmt=ibm_db.prepare(ibm_conn,sql)
                    ibm_db.bind_param(prep_stmt,1,new_hash.hexdigest())
                    ibm_db.execute(prep_stmt)
                    flash("Password Changed Successfully","alert alert-success")
                    return  redirect("/user/profile")
            else:
                flash("Password did not match/Entered Wrong Current Password","alert alert-danger")
                return  redirect("/user/profile/pwd")        


            flash("Password did not match","alert alert-danger")
            return redirect("/user/profile/pwd")
        except Exception as e:
            print(e)
            return redirect("/user/signin")





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)
