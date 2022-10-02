import sqlite3

con=sqlite3.connect("items.db")
print("successfullly connected");

con.execute("CREATE TABLE items (name TEXT,email TEXT,phone TEXT ,password TEXT)")

print("table created")
con.close()