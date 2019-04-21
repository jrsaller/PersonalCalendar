import os,base64

class SessionStore:
    def __init__(self):
        self.sessions = {}
        return

    def generateSessionID(self):
        rnum = os.urandom(32)
        rstr = base64.b64encode(rnum).decode("utf-8")
        return rstr

    def getSessionData(self,sessionID):
        if sessionID in self.sessions:
            return self.sessions[sessionID]
        else:
            return None

    def createSession(self):
        sessionID = self.generateSessionID()
        print("Generated new session with ID: " + sessionID)
        self.sessions[sessionID] = {}
        return sessionID

