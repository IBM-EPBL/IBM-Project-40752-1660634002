import ibm_db

connection=ibm_db.connect("")
sql="""CREATE TABLE Persons (
    
    name varchar(255),
    phone varchar(255),
    email varchar(255),
    password varchar(255)
);"""

ibm_db.exec_immediate(connection,sql)

print("DATABASE ADDED SUCCESSFULLY")