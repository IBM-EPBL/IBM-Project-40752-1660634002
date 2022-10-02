Name : ASWIN
Reg No:713919106005
College Name:Sri Ranganathar Institute Of Engineering and technology
Descprition:
    Assignment 2 (Database Integrated)

  Created an Flask App
  Added(Home page,About page)
  added bootstrap CDN
  added siginpage and signup page created html forms  
  added CRUD operations with sql3 
  used sql3 Database-CRUD(students-db)
  used IBM db2 Database

    

    
Routes:
     SQL3 DATABASE
  "/item"-Gives all the User in database
  "/add" -User can be created 
  "/delete/<name>"-User can be deleted From database
  "/edit/<name>"-User can be Edited

    IBM-DB2
  "/signup"-saves the users data to Cloud   
  "/signin"-finds the particular data of user

NOTE: THE CONNECTION STRING OF THE DATABASE(IBM-DB2) IS null TO AVOID THE USAGE OF DATABASE BY OTHERS  


// TO RUN SERVER = flask --debug run
// TO CREATE LOCALDATABASE (Tables,schema)= python3 setupdb.python3
// TO CREATE CLOUD_DATABASE (Tables,schema)=python3 db2.py
