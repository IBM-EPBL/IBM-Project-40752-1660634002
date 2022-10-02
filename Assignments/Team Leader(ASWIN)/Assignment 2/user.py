import sqlite3

conn = sqlite3.connect('users.db')
print("Opened database successfully")

conn.execute('CREATE TABLE students (name TEXT,phone TEXT,email TEXT, password TEXT)')
print("Table created successfully")
conn.close()
