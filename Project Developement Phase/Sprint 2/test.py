recruiter_skill="java"
import sqlite3

b="html"
b.upper()

def skillExist (a=recruiter_skill):
    with sqlite3.connect('hr.db') as connection:
        # connection.row_factory=sqlite3.Row
        cursor=connection.cursor()
        cursor.execute(""" SELECT skills FROM USERS """)
        data=cursor.fetchall()        
        for x in data:
            if type(x[0])==str:

                # print(type(x[0]))
                c=x[0].upper().find(a.upper())
                if c>=0:
                    print("Skills Exist")
                else:
                    print("Does not Exist")    

            else :
                return print("no")    


           
        return None



# skillExist(recruiter_skill)





