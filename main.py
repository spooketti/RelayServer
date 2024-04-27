from flask import Flask, request, jsonify, make_response, Response
from threading import Thread
from init import app, socketio
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import or_
from authToken import token_required
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from init import db, cors
import time
from model.user import Users, initUserTable
from model.channel import Channel, initChannelTable
from model.server import Servers, initServerTable
from model.message import Message, initMessageTable
from model.serverUser import ServerUser, initServerUser
import datetime
import os


@app.route('/')
def home():
    return "Relay's Server"

@app.before_request
def before_request():
    # Check if the request came from a specific origin
    allowed_origin = request.headers.get('Origin')
    if allowed_origin in ['http://localhost:4100', 'http://172.27.233.236:8080', 'https://spooketti.github.io']:
        cors._origins = allowed_origin
        
@app.route("/signup/", methods=["POST"])
def signup():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    user = Users(userID = data["userID"], password=hashed_password, username=data["username"],pfp=data["pfp"]) 
    db.session.add(user)  
    db.session.commit()    
    token = jwt.encode({'userID' : user.userID, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'], algorithm="HS256")
    resp = Response('{"jwt":"'+token+'"}')
    resp.set_cookie("jwt", token,
                                max_age=3600,
                                secure=True,
                                httponly=True,
                                path='/',
                                samesite='None',  # This is the key part for cross-site requests
                                domain="172.27.233.236"
                                )
    return resp

@app.route('/auth/', methods=['GET'])
@token_required
def auth(current_user):
    
    return jsonify({'pfp': current_user.pfp,
                    "username":current_user.username,
                    "userID":current_user.userID,
                    "joindate":current_user.date
                    })
    
@app.route('/createServer/',methods=["POST"])
@token_required
def createServer(current_user):
    data = request.get_json()
    server = Servers(name = data["name"],pfp = data["pfp"])
    db.session.add(server)  
    db.session.commit() 
    server_user = ServerUser(userID=current_user.id,serverID=server.id,userPermission="admin")   
    db.session.add(server_user)
    db.session.commit()
    return "Server Created"

    

    
    
    

@socketio.on("connect")
def test_connect(auth):
    print(auth)

    
@app.route('/login/', methods=['POST'])  
def login_user(): 
    data = request.get_json()
    loginID = data["userID"]
    loginPW = data["password"]
    user = Users.query.filter_by(userID=loginID).first()   
    if check_password_hash(user.password, loginPW):
        token = jwt.encode({'userID' : user.userID, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'], algorithm="HS256")
        resp = Response('{"jwt":"'+token+'"}')
        resp.set_cookie("jwt", token,
                                max_age=3600,
                                secure=True,
                                httponly=True,
                                path='/',
                                samesite='None',  # This is the key part for cross-site requests
                                domain="172.27.233.236"
                                )
        return resp


    return make_response('Invalid Credentials',  401, {'Authentication': '"login required"'})

    

def run():
  #app.run(host='0.0.0.0',port=6221)
  socketio.run(app, host="0.0.0.0",port=6221)

initUserTable()
initChannelTable()
initServerTable()
initMessageTable()
initServerUser()
run()