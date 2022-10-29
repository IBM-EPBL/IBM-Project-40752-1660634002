import sqlite3

connection=sqlite3.connect('hr.db')

connection.execute(""" CREATE TABLE OPENINGS (
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

print("Table created successfully")

connection.close()