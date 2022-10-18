import ibm_db

con=ibm_db.connect(,"","")
print("connected...")



sql="""CREATE TABLE Users(
    
    name varchar(255),
    phone varchar(255),
    email varchar(255),
    password varchar(255)
);"""

ibm_db.exec_immediate(con,sql)

print("added successfully")















# import sqlite3

# con=sqlite3.connect("users.db")
# print("successfullly connected");

# con.execute("CREATE TABLE users (name TEXT,email TEXT,phone TEXT ,password TEXT)")

# print("table created")
# con.close()