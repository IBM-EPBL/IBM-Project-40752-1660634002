import sqlite3

con=sqlite3.connect("users.db")
print("successfullly connected");

con.execute("CREATE TABLE users (name TEXT,email TEXT,phone TEXT ,password TEXT)")

print("table created")
con.close()