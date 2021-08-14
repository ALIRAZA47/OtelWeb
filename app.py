from flask import Flask
import os
import pyrebase
import json
from flask.helpers import url_for
from flask import render_template, request, redirect, session


# set templates dir
app_dir = os.getcwd()
template_dir = os.path.join(app_dir, "templates")
app = Flask(__name__, template_folder = template_dir)
app.secret_key = 'afw3rt5tfgse2453ve'



# firebase
config = {
    "apiKey": "AIzaSyCuDF4Z0YhDD8wNSN7HVCAmjLuK4obT310",
    "authDomain": "otelapp-e877d.firebaseapp.com",
    "databaseURL": "https://otelapp-e877d-default-rtdb.firebaseio.com",
    "projectId": "otelapp-e877d",
    "storageBucket": "otelapp-e877d.appspot.com",
    "messagingSenderId": "829229912602",
    "appId": "1:829229912602:web:78a85eb73bbe50e2cef7a3",
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

# getting data from firebase
db_resp = db.child("main").child("hotelsList").get() 
hotelsData = []   
for h in db_resp.each():
    hotelsData.append(h.val())

hotelName = " "
# print(rows)

'''  App routes here   '''
# index route
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(email,password)
        current_user = None
        if(email and password):
            db_resp_users = db.child("usersWeb").get()
            users = []
            user_email = email
            for u in db_resp_users.each():
                users.append(u.val())
            # now get current user's data
            current_user = None

            for user in users:
                if user['email'] == user_email:
                    current_user = user
            
            # now render profile activity
            if current_user:
                try:
                    authRes = auth.sign_in_with_email_and_password(email, password)
                    session['user'] = email
                    return render_template("index.html", data=hotelsData)
                except:
                    return render_template("login.html", login_error = "Wrong Credentials")
            else:
                return render_template("login.html", login_error = "User Does Not Exist")
        else:
            return render_template("login.html", login_error = "Email and Password cannot be left blank")
    return redirect(url_for("home"))    

# Home route
@app.route("/home", methods=["GET", "POST"])
def home():
    try:
        if session['user']:
            return render_template("index.html", data=hotelsData)
        else:
            return render_template("login.html")
    except :
        return render_template("login.html")

# Signup route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        comfirm_pass = request.form['confirmpassword']
        phone = request.form['phone']
        address = request.form['address']
        cnic = request.form['cnic']
        try:
            if password == comfirm_pass:
                auth.create_user_with_email_and_password(email, password)
                user = {
                    "name":name,
                    "email":email,
                    "phone":phone,
                    "address":address,
                    "cnic":cnic
                }
                db.child("usersWeb").child(str(name)).set(user)
                return render_template("signup.html", signup_success = "User Has Been Created.. Continue Login!")
            else:
                return render_template("signup.html", signup_error="Passwords Do not Match")

        except:
            return render_template("signup.html", signup_error="Couldn' Create User")
    else:
        return render_template("signup.html")

# Show hotel rooms
@app.route("/hotelRooms", methods=["GET", "POST"])
def hotelRooms():
    if request.method == "POST":
        hotelName = request.form["hotelName"]
        # print("\n\n\n\n"+hotelName)
        # return (hotelName)
        db_resp_rooms = db.child("main").child("hotelsList").child(hotelName).child("rooms").get()
        img = (storage.child("Hotel Ali/05/two-dBed.jpg").get_url(None))
        print("\n\n\n") 
        roomsData = []   
        for h in db_resp_rooms.each():
            roomsData.append(h.val())
        return render_template("hotelRooms.html", rooms_data=roomsData, hotelName= hotelName, img=img)
        # return (str(roomsData))
    return render_template("404.html")

# Book room route
@app.route("/bookRoom", methods=["GET", "POST"])
def bookroom():
    try:
        if(session['user']):
            if request.method == "POST":
                hotelName = request.form['bookRoom']
                data = hotelName.split(',')
                name = data[0]
                roomNum = data[1]
                name = name[2:]
                name = name[:-1]
                
                r = roomNum[2:]
                roomNum = r[:-2]
                a = int(roomNum)
                try:
                    db.child("main").child("hotelsList").child(name).child("rooms").child(str(a)).child("currentStatus").set("Pending")
                    db_resp_rooms = db.child("main").child("hotelsList").child(name).child("rooms").get() 
                    roomsData = []   
                    for h in db_resp_rooms.each():
                        roomsData.append(h.val())
                    return render_template("hotelRooms.html", rooms_data=roomsData, hotelName= name)
                except :
                    return ("Naah Baba Naah")
    except:
        return render_template("login.html", login_error = "Please Login..")
# Logout Route
@app.route("/logout", methods=["GET", "POST"])
def logout():
    print("\n\n\n"+session['user'])
    session.pop('user')

    return render_template("login.html")

# Prfile Route
@app.route("/profile")
def profile():
    user_email = session['user']
    # retrieve users from RTDB
    db_resp_users = db.child("usersWeb").get()
    users = []
    for u in db_resp_users.each():
        users.append(u.val())
    # now get current user's data
    current_user = None

    for user in users:
        if user['email'] == user_email:
            current_user = user
    
    # now render profile activity
    if current_user:
        return render_template("profile.html", profile_data = current_user)
    else:
        return redirect(url_for("home"))

# Run app
if __name__ == '__main__':
    app.run(debug=True)
    