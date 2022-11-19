import ibm_db

connection=ibm_db.connect("DATABASE=bludb;HOSTNAME=9938aec0-8105-433e-8bf9-0fbb7e483086.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32459;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=pps68497;PWD=aAvllD0pQNIuQo4q",'','')





sql=""" CREATE TABLE RECRUITER (
    name varchar(255),
    phone varchar(255) ,
    email varchar(255) ,
    password varchar(255), 
    id varchar(255) ,
    about_me varchar(255),
    designation varchar(255),
    experience varchar(255),
    url varchar(255),
    company_name varchar(255),
    company_description varchar(255),
    location varchar(255),
    website varchar(255),
    in_url varchar(255),
    token varchar(255),
    isVerified varchar(255) )  """
ibm_db.exec_immediate(connection,sql)



sql=""" CREATE TABLE OPENINGS (
    id varchar(255),
    title varchar(255),
    company_name varchar(255),
    designation varchar(255),
    salary_range varchar(255),
    skills_required varchar(255),
    roles_responsibilities varchar(255),
    company_description varchar(255),
    location varchar(255),
    website varchar(255),
    author varchar(255) NOT NULL )  """
print("successfully added")    

ibm_db.exec_immediate(connection,sql)

sql="""CREATE TABLE USERS
 (id varchar(255),
  name varchar(255),
  email varchar(255),
  phone varchar(255) ,
  password varchar(255),
  about varchar(255), 
  designation varchar(255),
  school varchar(255),
  skills varchar(255),
  project varchar(255),
  description varchar(255),
  token varchar(255),
    isVerified varchar(255))"""
ibm_db.exec_immediate(connection,sql)

sql="""CREATE TABLE POSTS (
    author_name varchar(255),
    author_id varchar(255),
    post_id varchar(255),
    title varchar(255),
    description varchar(255),
 url varchar(255),
   video_url varchar(255)

)  """ 

ibm_db.exec_immediate(connection,sql)

sql="""CREATE TABLE APPLICATIONS 
    (author_hr varchar(255),
    post_id varchar(255),
    user_id varchar(255),
    viewed varchar(255))
    

  """

ibm_db.exec_immediate(connection,sql)
print("All inserted")