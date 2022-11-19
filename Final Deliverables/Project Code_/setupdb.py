import sqlite3 as sqlite3

connection =sqlite3.connect("hr.db")
print("Database Created Successfully")
cursor=connection.cursor()
cursor.execute(""" CREATE TABLE RECRUITER (
    name TEXT,
    phone TEXT ,
    email TEXT NOT NULL UNIQUE,
    password TEXT, 
    id TEXT PRIMARY KEY,
    about_me TEXT,
    designation TEXT,
    experience TEXT,
    url TEXT,
    company_name TEXT,
    company_description TEXT,
    location TEXT,
    website TEXT,
    in_url TEXT )  """)

print("Table Recruiter Successfully")


cursor.execute(""" CREATE TABLE OPENINGS (
    id TEXT,
    title TEXT,
    company_name TEXT,
    designation TEXT,
    salary_range TEXT,
    skills_required TEXT,
    roles_responsibilities TEXT,
    company_description TEXT,
    location TEXT,
    website TEXT,
    author TEXT NOT NULL )  """)

print("Table Openings successfully")



print("successfullly connected");



cursor.execute("CREATE TABLE USERS (id TEXT, name TEXT,email TEXT,phone TEXT ,password TEXT,about TEXT, designation TEXT,school TEXT,skills TEXT,project TEXT,description TEXT)")
print("profile table created")

print("table created")


cursor.execute("""CREATE TABLE POSTS (
    author_name TEXT,
    author_id TEXT,
    post_id TEXT,
    title TEXT,
    description TEXT

)  """)
cursor.execute("""CREATE TABLE APPLICATIONS 
    (author_hr TEXT,
    post_id TEXT,
    user_id TEXT,
    viewed TEXT)
    

  """)
cursor.close()
print("added  successfully")


