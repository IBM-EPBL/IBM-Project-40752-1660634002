import sqlite3

con=sqlite3.connect("persons.db")
print("successfullly connected");

con.execute("CREATE TABLE persons (name TEXT,email TEXT,phone TEXT ,password TEXT)")

print("table created")
con.close()