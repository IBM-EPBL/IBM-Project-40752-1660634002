import sqlite3

conn = sqlite3.connect('students.db')
print("Opened database successfully")

conn.execute('CREATE TABLE students (name TEXT,contact TEXT)')
print("Table created successfully")
conn.close()
