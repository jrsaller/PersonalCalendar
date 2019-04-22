#included sqlite3 library with python
import os
import psycopg2
import psycopg2.extras
import urllib.parse

#def dict_factory(cursor,row):
#    d = {}
#    for idx,col in enumerate(cursor.description):
#        d[col[0]] = row[idx]
#    return d

class EventsDB:
    def __init__(self):
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
        
        self.connection = psycopg2.connect(
            cursor_factory=psycopg2.extras.RealDictCursor,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def createEventsTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS events(id SERIAL PRIMARY KEY,title VARCHAR(255),date VARCHAR(255),time VARCHAR(255),description VARCHAR(255),location VARCHAR(255))")
        self.connection.commit()

    def createUsersTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users(id SERIAL PRIMARY KEY,firstname VARCHAR(255),lastname VARCHAR(255),email VARCHAR(255),password VARCHAR(255))")
        self.connection.commit()

    def createEvent(self,id,title,date,time,description,location):
        #IF YOU EVER CONCATENATE DIRECTLY INTO YOUR QUERY STRING, YOU DONE MESSED UP
        sql = "INSERT INTO events (id , title , date, time, description, location) VALUES( %s , %s , %s, %s , %s , %s )"
        self.cursor.execute(sql,[id,title,date,time,description,location])
        self.connection.commit()
        return

    def getAllEvents(self):
        self.cursor.execute("SELECT * FROM events")
        return self.cursor.fetchall()
    
    def getEvent(self,id):
        query = "SELECT * FROM events WHERE id=%s"
        self.cursor.execute(query,[id])
        result = self.cursor.fetchone()
        if result == "" or result == None:
            return None
        else:
            return result

    def deleteEvent(self,id):
        if self.getEvent(id) != None:
            sql = "DELETE FROM events WHERE id = %s"
            self.cursor.execute(sql,[id])
            self.connection.commit()
            return True
        else:
            return False
    def editEvent(self,id,name,date,time,description,location):
        if self.getEvent(id) != "":
            sql = "UPDATE events SET title=%s,date=%s,time=%s,description=%s,location=%s WHERE id = %s"
            self.cursor.execute(sql,[name,date,time,description,location,id])
            self.connection.commit()
            return True
        else:
            return False
    
    def getMaxID(self):
        self.cursor.execute("SELECT MAX(id) FROM events")
        result = self.cursor.fetchone()
        if "max" in result:
            return result["max"]
        else:
            return 0

    def getMaxUser(self):
        self.cursor.execute("SELECT MAX(id) FROM users")
        result = self.cursor.fetchone()
        if "max" in result:
            return result["max"]
        else:
            return 0
    
    def getUserByEmail(self,email):
        sql = "SELECT * FROM users WHERE email = %s"
        self.cursor.execute(sql,[email])
        result = self.cursor.fetchone()
        if result == "" or result == None:
            return None
        else:
            return result
    def registerUser(self,fname,lname,email,password):
        sql = "INSERT INTO users(id,firstname,lastname,email,password) VALUES(%s,%s,%s,%s,%s)"
        print(password)
        print("password on register")
        num = self.getMaxUser()
        if (num == None) :
            num = 0
        self.cursor.execute(sql,[num+1,fname,lname,email,password])
        self.connection.commit()
        return











#connects me to my database, spawns a connection
#conn = sqlite3.connect("messages.db")

###need a cursor, allows you to get your data from the database
###basically a hand on the data
#cursor = conn.cursor()

###cursor is usually the go to

###equivalent to typing on the command line in sqlite
#cursor.execute("INSERT INTO log (id , name , message) VALUES( 234 , 'Steven' , 'I like trains' )")
#conn.commit()
###Only commit if you have a side effect/result  from the data

###no need to commit here because we only read, we dont change the data at all
#cursor.execute("SELECT * FROM log")
#result = cursor.fetchall()
###if nothing is found in fetchall, it returns an empty list

#print(result)

