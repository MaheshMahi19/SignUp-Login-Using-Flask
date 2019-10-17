# This file contains an example Flask-User application.
# To keep the example simple, we are applying some unusual techniques:
# - Placing everything in one file
# - Using class-based configuration (instead of file-based configuration)
# - Using string-based templates (instead of file-based templates)

from flask import *
from pymongo import MongoClient
import re
from datetime import timedelta

sesslifetime = timedelta(days=7)
db = MongoClient().test.users

app = Flask(__name__)
app.config["PERMANENT_SESSION_LIFETIME"] = sesslifetime
app.config["SECRET_KEY"] = "nothingissecretknow?"


def validOrNot(username,password,email=None):
    match = re.match(r"^[a-zA-Z0-9_]+$",username)
    err = ""
    if len(username) < 4 or username == "" or match == None:
        err = "Please Check Username"
    elif len(password) < 6 or password == "":
        err = "Please Check Password"
    elif email is not None:
        dot = email.find(".")
        if email == "" or email.find("@") == -1 or dot == -1 or len(email[dot+1:]) not in range(2,5):
            err = "Email Format is Malformed!.. ;("
    return err


@app.route("/user/login",methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("/flask_user/userlogin.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        err = validOrNot(username, password)
        if err:
            return render_template("/flask_user/userlogin.html",err=err)
        else:
            useres = db.find_one({"username":username})
            mailres = db.find_one({"email":username})
            if useres or mailres:
                org = useres["org"] if useres is not None else mailres["org"]
                print(org)
                print(useres)
                session["userlogged"] = True
                return redirect(url_for('orgHome', org=org))
def checkEU(username,email):
    userCheck = db.find_one({"username":username})
    print(userCheck)
    emailc = db.find_one({"email":email})
    print(emailc)
    if userCheck:
        err = "Username Already there in Usage!"
        return err
    elif emailc:
        err = "There is another Mail Registered.! Try another ;)"
        return err
    else:
        return None


@app.route("/user/register",methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("/flask_user/userreg.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        mail = request.form["email"]
        org = request.form["org"]
        user_eErr = checkEU(username,mail)
        err = validOrNot(username,password)
        if err:
            return render_template("flask_user/userreg.html",err=err)
        elif user_eErr:
            return render_template("flask_user/userreg.html",err=user_eErr)
        else:
            #succ = "You've Registered Successfully!..Now you can Login"
            try:
                userDet = {"username":username,"email":mail,"password":password,"org":org}
                res = db.insert_one(userDet)
                if res:
                    return redirect(url_for("login", thisis="success"))
                else:
                    render_template("flask_user/userreg.html",err="Server Error Try again/Contact US")
            except:
                return redirect(url_for("home"))
        


@app.route("/home",)
def home():
    username = "Mahesh"
    return render_template("flask_user/userlogin.html", username=username)


@app.route("/orgs/<org>/home")
def orgHome(org):
    org = org
    username = "Mahesh"
    return render_template("flask_user/userlogin.html", username=username,org=org)


@app.route("/user/logout")
def logout():
    session.pop("userlogged")
    return redirect("/home")


if __name__ == "__main__":
    app.run()