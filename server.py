from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from http import cookies
import json
from database import EventsDB
from session_store import SessionStore
import bcrypt
import sys


#SELF.SESSION WILL BE THE USER TALKING TO YOU
#SOMEWHERE IN CODE YOU NEED
#
#ON AUTHENTICATE, send 201 , SELF.SESSION["userID"] = user["ID"]

#GENERAL VALIDATION ERROR 422
#

#CANT RUN COOKIE AND SESSION STORE STUFF WITH POSTMAN



gSessionStore = SessionStore()

class MyRequestHandler(BaseHTTPRequestHandler):
    
    def isLoggedIn(self):
        if "userid" in self.session:
            return True
        else:
            return False
    
    def handle401(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate","Not Authorized")

        self.end_headers()
	
    def end_headers(self):
        self.sendCookie()
        self.send_header("Access-Control-Allow-Origin",self.headers["Origin"])
        self.send_header("Access-Control-Allow-Credentials","true")
        BaseHTTPRequestHandler.end_headers(self)

    def loadCookie(self):
        #if cookie received use it
        if "Cookie" in self.headers:
            print("COOKIE FOUND")
            self.cookie = cookies.SimpleCookie(self.headers["Cookie"])
        else:
            #new cookie
            self.cookie = cookies.SimpleCookie()
    
    def sendCookie(self):
        for morsel in self.cookie.values():
            self.send_header("Set-Cookie",morsel.OutputString())
 
    def loadSession(self):
        self.loadCookie()
        print("Checking for session")
        if "sessionID" in self.cookie:
            #SESSION ID FOUND IN COOKIE
            #cookie received from user,theyve been here before
            sessionID = self.cookie["sessionID"].value
            self.session = gSessionStore.getSessionData(sessionID)
            if self.session == None:
                #NO SESSION ID FOUND IN THE SESSION STORE
                #person gave me a cookie, but I dont have it in my session store
                print("NEW SESSION FOR SESSION STORE")
                sessionID = gSessionStore.createSession()
                self.cookie["sessionID"] = sessionID
                self.session = gSessionStore.getSessionData(sessionID)
            else:
                print("Found their session!")
        else:
            #NO SESSION ID FOUND IN COOKIE
            #new user
            print("NO SESSION IN COOKIE")
            sessionID = gSessionStore.createSession()
            self.cookie["sessionID"] = sessionID
            self.session = gSessionStore.getSessionData(sessionID)
        return


    def handleSessionCreate(self):
        length = self.headers["Content-Length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        parsed_body = parse_qs(body)

        email = parsed_body["email"][0]
        print(email)
        password = parsed_body["password"][0]

        db = EventsDB()
        user = db.getUserByEmail(email)
        if user == None :
            #Try to create a session, but got nothing back when looking for them in the database
            self.handle401()
        else:
            print(password)
            print(password.encode("utf-8"))
            print(user["password"])
            print(user["password"].encode())
            if bcrypt.hashpw(password.encode("utf-8"),user["password"].encode()) == user["password"].encode():
                #print("GOOD PASSWORD")
                #The user has been Authenticated
                self.session["userid"] = user["id"]
                self.send_response(201)
                self.end_headers()
            else:
                #Not authenticated
                print("BAD PASSWORD")
                self.handle401()

    def handleRegisterUser(self):
        length = self.headers["Content-Length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        parsed_body = parse_qs(body)
        email = parsed_body["email"][0]
        password = parsed_body["password"][0]
        fname = parsed_body["firstname"][0]
        lname = parsed_body["lastname"][0]
        db = EventsDB()
        if db.getUserByEmail(email) == None:
            encodedPass = password.encode()
            salt = bcrypt.gensalt()
            hashPass = bcrypt.hashpw(encodedPass,salt)
            db.registerUser(fname,lname,email,hashPass)
            self.send_response(201)
            self.end_headers()
            self.wfile.write(bytes("User successfully registered!","utf-8"))
            print("Registered")
        else:
            self.send_response(422)
            print("!!!REGISTER ERROR")
            self.end_headers()
            self.wfile.write(bytes("User already registered!","utf-8"))
     
       
    def handleEventList(self):
        if self.isLoggedIn():
            self.send_response(200)
            self.send_header("Content-type","application/json")
            self.end_headers()
            db = EventsDB()
            getEvents = db.getAllEvents()
            self.wfile.write(bytes(json.dumps(getEvents), "utf-8"))
        else:
            self.handle401()

        return
    
    def handleEventCreate(self):
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        print("the text body:", body)
        parsed_body = parse_qs(body)
        print("the parsed body:", parsed_body)
        
        #name = parsed_body["name"][0]
        #cuisine = parsed_body["cuisine"][0]
        db = EventsDB()
        ID = db.getMaxID() + 1
        title = parsed_body["title"][0]
        date = parsed_body["date"][0]
        time = parsed_body["time"][0]
        description = parsed_body["description"][0] 
        location = parsed_body["location"][0]        
        # save the restaurant!
        
        db.createEvent(ID,title,date,time,description,location)

        self.send_response(201)
        self.end_headers()
        self.wfile.write(bytes("Event Added!","utf-8"))

        return
    
    
    def handleEventRetrieve(self,id):
        db = EventsDB()
        event = db.getEvent(id)
        if event == None:
            self.handleNotFound("Retrieve")
        else:
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(event),"utf-8"))
        return
    
    def handleEventUpdate(self,id):
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        print("the text body:", body)
        parsed_body = parse_qs(body)
        print("the parsed body:", parsed_body)
        
        #name = parsed_body["name"][0]
        #cuisine = parsed_body["cuisine"][0]
        db = EventsDB()
        title = parsed_body["title"][0]
        date = parsed_body["date"][0]
        time = parsed_body["time"][0]
        description = parsed_body["description"][0] 
        location = parsed_body["location"][0]        
        # save the restaurant!
        
        db.editEvent(id,title,date,time,description,location)

        self.send_response(201)
        self.end_headers()
        self.wfile.write(bytes("Event Updated!","utf-8"))

        return

    def handleEventDelete(self,id):
        db = EventsDB()
        if db.deleteEvent(id):
            self.send_response(200)
            self.send_header("Content-type","text/plain")
            self.end_headers()
            self.wfile.write(bytes("Item deleted","utf-8"))
        else:
            self.handleNotFound("Delete")
    
    def handleNotFound(self,method):
        self.send_response(404)
        self.send_header("Content-type","text/plain")
        self.end_headers()
        self.wfile.write(bytes("Not found on " + method,"utf-8"))
        return
    
    def do_GET(self):
        self.loadSession()
        if self.isLoggedIn():
            parts = self.path.split("/")[1:]
            collection = parts[0]
            if len(parts) > 1 and parts[1] != "":
                id = parts[1]
            else:
                id = None
            if collection == "events":
                #print("SHOW EVENTS PLEASE")
                if id == None:
                    self.handleEventList()
                else:
                    self.handleEventRetrieve(id)
            else:
                self.handleNotFound("Get")

            return
        else:
            #print("HELP")
            #self.handleSessionCreate()
            if self.path == "/events":
                self.send_response(401)
                self.end_headers()
                self.wfile.write(bytes("401: Cannot access data when not logged in","utf-8"))
            else:
                self.send_response(422)
                self.end_headers()
                self.wfile.write(bytes("422: Cannot get when not logged in","utf-8"))


    def do_POST(self):
        self.loadSession()
        if self.isLoggedIn():
            if self.path == "/events":
                self.handleEventCreate()
            else:
                self.handleNotFound("Post")
        else:
            if self.path == "/users":
                self.handleRegisterUser()
            elif self.path == "/session":
                self.handleSessionCreate()
            else:
                self.handleNotFound("Post")
        return

    def do_PUT(self):
        self.loadSession()
        if self.isLoggedIn():
            parts = self.path.split("/")[1:]
            collection = parts[0]
            if len(parts) > 1:
                id = parts[1]
            else:
                id = None
            db = EventsDB()
            if collection == "events":
                if id == None or db.getEvent(id) == None or id == "":
                    self.handleNotFound("Put")
                else:
                    self.handleEventUpdate(id)
            else:
                self.handleNotFound("Put")
        else:
            self.send_response(422)
            self.end_headers()
        return

    def do_DELETE(self):
        self.loadSession()
        if self.isLoggedIn():
            parts = self.path.split("/")[1:]
            collection = parts[0]
            if len(parts) >1:
                id = parts[1]
            else:
                id = None
            db = EventsDB() 
            if collection == "events":
                if id == None or db.getEvent(id) == None:
                    self.handleNotFound("Delete")
                else:
                    self.handleEventDelete(id)
            else:
                self.handleNotFound("Delete")

            return
        else:
            self.send_response(422)
            self.end_headers()


    def do_OPTIONS(self):
        self.loadSession()
        self.send_response(200)
        #ALLOWS THE FOLLOWING OPTIONS
        self.send_header("Access-Control-Allow-Methods","GET,POST,PUT,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-type")
        self.end_headers()


def run():
    db = EventsDB()
    db.createEventsTable()
    db.createUsersTable()
    db = None
    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    listen = ("0.0.0.0", port)
    server = HTTPServer(listen, MyRequestHandler)
    print("Server listening on","{}:{}".format(*listen))
    server.serve_forever()

run()







