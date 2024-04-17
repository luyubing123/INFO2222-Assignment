'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, abort, url_for
from flask_socketio import SocketIO
import db
import secrets

# import logging

# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

# secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()
socketio = SocketIO(app, debug=True)

# don't remove this!!
import socket_routes

# index page
@app.route("/")
def index():
    return render_template("index.jinja")

# login page
@app.route("/login")
def login():    
    return render_template("login.jinja")

# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    password = request.json.get("password")

    user =  db.get_user(username)
    if user is None:
        return "Error: User does not exist!"

    if user.password != password:
        return "Error: Password does not match!"

    return url_for('home', username=request.json.get("username"))

#  handle a postrequest when user click add button
@app.route("/home/addfriend", methods=["POST"])
def add_friend():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    friendname = request.json.get("friendname")
 
    user_to_add =  db.get_user(friendname)
    if user_to_add is None:
        return "Error: User does not exist!"
    
    if friendname == username:
        return "Error: Cann't add yourself"

    if db.friendship_exist(username,friendname):
        return  friendname + " has already been your friend"
    
    db.insert_friendrequest(username,friendname)
    return "Request send"

#  handle a postrequest when user click accept button
@app.route("/home/acceptrequest", methods=["POST"])
def accept_request():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    friendname = request.json.get("friendname")
    
    db.modify_status_request(username,friendname,"Accepted")
    db.insert_friendship(username,friendname)

    return username

#  handle a postrequest when user click reject button
@app.route("/home/rejectrequest", methods=["POST"])
def reject_request():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    friendname = request.json.get("friendname")
    
    db.modify_status_request(username,friendname,"Rejected")

    # db.insert_friendship(username,friendname)
    return username


# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")

# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)
    username = request.json.get("username")
    password = request.json.get("password")

    if db.get_user(username) is None:
        db.insert_user(username, password)
        return url_for('home', username=username)
    return "Error: User already exists!"


# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404



# home page, where the messaging app is
@app.route("/home")
def home():
    if request.args.get("username") is None:
        abort(404)
    
    # db.delete_all()

    # store current user's friends in a list
    friendship = []
    result1 = db.get_friendship_sent_from_you(request.args.get("username"))
    result2 = db.get_friendship_received_by_you(request.args.get("username"))
    for r in result1:
        friendship.append(r.friendname)
    for r in result2:
        friendship.append(r.username)

    friendrequest = []
    request_results = db.get_friendrequest(request.args.get("username"))
    for r in request_results:
        friendrequest.append(r.friendname +": " + r.status)

    received_pending_friendrequest = []
    received_results = db.get_received_friendrequest(request.args.get("username"))
    for r in received_results:
        if r.status == "Pending":
           received_pending_friendrequest.append(r.username)
    
    received_not_pending_friendrequest = []
    for r in received_results:
        if r.status != "Pending":
           received_not_pending_friendrequest.append(r.username + ": " + r.status)
         

    return render_template("home.jinja", username=request.args.get("username"), 
                           friendship = friendship,friendrequest = friendrequest,
                           received_pending_friendrequest = received_pending_friendrequest,
                           received_not_pending_friendrequest = received_not_pending_friendrequest)



if __name__ == '__main__':
    socketio.run(app, debug=True)
