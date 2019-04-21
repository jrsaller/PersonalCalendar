#s19-authentication-jrsaller
## Name of Resource, name of each attribute
### Resource : 
        events
        session
        users
### Attributes of events:
        date
        description
        id
        location
        time
        title
### Attributes of session:
        email 
        password
### Attributes of users:
        firstname
        lastname
        email
        password
        

### Database Schema
    CREATE TABLE events (   id INTEGER PRIMARY KEY,
                            title TEXT,
                            date TEXT,
                            time TEXT,
                            description TEXT,
                            location TEXT
                            );
    
    CREATE TABLE users (    id INTEGER PRIMARY KEY,
                            firstname TEXT,
                            lastname TEXT,
                            email TEXT,
                            password TEXT,
                            );

### All REST endpoints including name, HTTP Method, and path for each
|METHOD NAME|HTTP METHOD|PATH|
|-----------|-----------|----|
|handleEventList|GET|/events|
|handleEventRetrieve|GET|/events/id|
|handleEventCreate|POST|/events|
|handleEventUpdate|PUT|/events/id|
|handleEventDelete|DELETE|/events/id|
|handleSessionCreate|POST|/session|
|handleRegisterUser|POST|/users|

### Password Hashing Method
This project uses bcrypt for password encryption.
