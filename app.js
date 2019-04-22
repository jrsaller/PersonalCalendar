var serverLocation = "http://localhost:8080/events"
var hostServerURL = "https://personal-calendar.herokuapp.com"
var submitbutton = document.querySelector("#submit-button");
var eventList = document.querySelector("#eventList");
var editForm = document.querySelector("#edit-form");
var submitLogin = document.querySelector("#submit-login");
var submitRegister = document.querySelector("#submit-register")
var interface = document.querySelector("#interface")
var loginSection = document.querySelector("#login")
var registerNames = document.querySelector("#finishregisterarea")
var finReg = document.querySelector("#finish-register")
var problemdiv = document.querySelector("#problem")

//page loads:
//load data
//      if 200
//            displayData
//      if 401
//            display Login or register Form
//               _login form code
//                   if 201:
//                      displayData
//                   elif 422:
//                      
//                   if 401:
//                      problem
//                  


submitRegister.onclick = function() {
        var username = document.querySelector("#submit-username")
        var password = document.querySelector("#submit-password")
        registerNames.style.display = "block"
        registerNames.style.textAlign = "center"
        problemdiv.innerHTML = "<h3>Enter your first and last name to complete registration</h3>"
        finReg.onclick = function() {
            var firstname = document.querySelector("#firstname")
            var lastname = document.querySelector("#lastname")
            var messageToSend = "email="+encodeURIComponent(username.value)
            messageToSend += "&password=" + encodeURIComponent(password.value)
            messageToSend += "&firstname=" + encodeURIComponent(firstname.value)
            messageToSend += "&lastname=" + encodeURIComponent(lastname.value)
            fetch(hostServerURL + "/users" , {
                                    body: messageToSend,
                                    method: "POST",
                                    credentials:"include",
                                    headers: {"content-Type": "application/x-www-form-urlencoded"}
             }).then(function(response) {
                 console.log("STATUS CODE: " + response.status)
                 if (response.status == 201) {
                    console.log("SUCCESSFUL REGISTER")
                    problemdiv.innerHTML = "<h3>Successful register,press Submit to log in!</h3>"
                    registerNames.style.display = "none"
                 } else if (response.status == 422 ){
                    console.log("There was a problem")
                    problemdiv.innerHTML = "<h3>Unable to Register...</h3>"
                 } else {
                    problemdiv.innerHTML = "<h3>Unexpected error code received from the server, contact ADMIN</h3>"
                 }

            
            });
        }

}
submitLogin.onclick = function() {
        var username = document.querySelector("#submit-username")
        var password = document.querySelector("#submit-password")
    var messageToSend = "email=" + encodeURIComponent(username.value)
    messageToSend += "&password=" + encodeURIComponent(password.value)
    fetch(hostServerURL + "/session" , {
                                body: messageToSend,
                                method: "POST",
                                credentials:"include",
                                headers: {"content-Type": "application/x-www-form-urlencoded"}
    }).then(function(response) {
             
        console.log("STATUS CODE: " + response.status)
        if (response.status == 201) {
                console.log("SUCCESSFUL LOGIN")
                //interface.style.display = "block"
                //loginSection.style.display = "none"
                showData()
        }else {
                problemdiv.innerHTML = "<h3>Unable to Log In...</h3>"
        }

        
   });

}






function showData() {
        var activeDay = document.querySelector(".tablinksactive").innerHTML
        var currentPlace = document.querySelector("eventList")
        //console.log(currentPlace)
        //console.log(activeDay)
        fetch(hostServerURL + "/events",{ credentials:"include" }).then(function(response) {
            console.log(response.status)
            if (response.status == 401 || response.status == 422){
                //SHOW LOGIN/REGISTER FORM
                interface.style.display = "none"
                loginSection.style.display = "block"
                problemdiv.innerHTML = "<h3>You must be signed in to access this data</h3>"
                //currentPlace.InnerHTML = "You need to sign in!!!!"
                //interface.style.display = "block"
            }else if (response.status == 200) {
                response.json().then(function(data) {
                    //SHOW APPROPRIATE DIVS FOR DATA
                
                interface.style.display = "block"
                loginSection.style.display = "none"
                console.log("Heres your data",data);
                eventList.innerHTML = "";
                data.sort(function(a,b) {
                                            var timelist1 = a["time"].split(" ");
                                            var time1 = Number(timelist1[0]);
                                            if (timelist1[1] == "PM") {
                                                time1+=12;
                                            }
                                            var timelist2 = b["time"].split(" ");
                                            var time2 = Number(timelist2[0]);
                                            if (timelist2[1] == "PM") {
                                                time2+=12;
                                            }
                                            return time1-time2
                                        });
                data.forEach(function(element) {
                    if (element["date"] == activeDay) {
                        //in here you could make a div, append other elements to that div, and append that div into your list
                        var event = document.createElement("div")
                        var child = document.createElement("h3");
                        var description = document.createElement("p");
                        child.innerHTML = element["date"] + " @ " + element["time"] + ":" + element["title"];
                        event.appendChild(child);
                        description.innerHTML = element["description"]
                        var deleteButton = document.createElement("button");
                        var editButton = document.createElement("button");
                        deleteButton.innerHTML = "Delete";
                        editButton.innerHTML = "Edit";
                        deleteButton.onclick = function() {
                            var proceed = confirm(`DELETE ${child.innerHTML}? `)
                            if (proceed) {
                                deleteEvent(element.id);
                            }
                        }

                        editButton.onclick = function() {
                            confirm("Check the form to edit your event");
                            editForm.style.display = "block";
                            var nameEdit = document.querySelector("#name-edit");
                            var dateEdit = document.querySelector("#date-edit");
                            var timeEdit = document.querySelector("#time-edit");
                            var descriptionEdit = document.querySelector("#description-edit");
                            var locationEdit = document.querySelector("#location-edit");
                            var submitEditButton = document.querySelector("#submit-edit-button");
                            nameEdit.value = element["title"]
                            dateEdit.value = element["date"]
                            timeEdit.value = element["time"]
                            descriptionEdit.value = element["description"]
                            locationEdit.value = element["location"]
                            submitEditButton.onclick = function() {
                                editEvent(element["id"],nameEdit.value,dateEdit.value,timeEdit.value,descriptionEdit.value,locationEdit.value);
                            }
                            
                        }


                        event.appendChild(description);
                        event.appendChild(deleteButton);
                        event.appendChild(editButton);
                        eventList.appendChild(event);
                    }
                });
                })
                                
            //}else if(response.status!= 201) {
                //SOMETHIGN WEIRD hAPPENED< MAYBE TELL THE USER SOMETHIGN HAPPENED
            } else {
                problemdiv.innerHTML="<h2>OH NO! There was a problem talking to the server</h2>"
            }
                
        })

};
        
var deleteEvent = function(id) {
    fetch (hostServerURL + `/events/${id}`, {
        method:"DELETE",
        credentials:"include"
    }).then(function(response) {
        console.log("Event Deleted");
        showData();
        //REFRESH THE LOG
    })
}

var editEvent = function(id,name,date,time,description,location) {
    var messageToSend = "title=" + encodeURIComponent(name);
    messageToSend += "&date=" + encodeURIComponent(date);
    messageToSend += "&time=" + encodeURIComponent(time);
    messageToSend += "&description=" + encodeURIComponent(description);
    messageToSend += "&location=" + encodeURIComponent(location);
    messageToSend += "&id=" + encodeURIComponent(id);
    console.log("Message to send: " + messageToSend);
    fetch(hostServerURL + "/events/" + id , {
        body:messageToSend,
        method: "PUT",
        credentials:"include",
        headers: {"content-Type": "application/x-www-form-urlencoded"}

    }).then(function(response) {
        console.log(response);
        showData();
        editForm.style.display = "none";
    })
    
}

function openDay(evt,day) {

    tablink = document.querySelector(".tablinksactive");
    tablink.className=tablink.className.replace("active","");
    evt.currentTarget.className +="active";
    showData()

}


submitbutton.onclick = function() {
    var name = document.querySelector("#name-submission")
    console.log(name)
    var date = document.querySelector("#date-submission")
    var time = document.querySelector("#time-submission")
    var description = document.querySelector("#description-submission")
    var location = document.querySelector("#location-submission")
    var messageToSend = "title=" + encodeURIComponent(name.value);
    messageToSend += "&date=" + encodeURIComponent(date.value);
    messageToSend += "&time=" + encodeURIComponent(time.value);
    messageToSend += "&description=" + encodeURIComponent(description.value);
    messageToSend += "&location=" + encodeURIComponent(location.value);
    console.log("Message to send: " + messageToSend);
    fetch(hostServerURL + "/events" , {
                                body: messageToSend,
                                method: "POST",
                                credentials:"include",
                                headers: {"content-Type": "application/x-www-form-urlencoded"}
    }).then(function(response) {
        console.log(response);
        showData();
    });
    name.value = "";
    date.value = "";
    time.value = "";
    description.value = "";
    location.value = "";
}


showData();
