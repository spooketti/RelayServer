from flask import Flask, request, jsonify, make_response, Response
from threading import Thread
from init import app, socketio
from flask_sqlalchemy import SQLAlchemy 
from flask_socketio import join_room
from sqlalchemy import and_
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
def before_request(): #provided by teacher John Mortenson
    allowed_origin = request.headers.get('Origin')
    if allowed_origin in ['http://localhost:4100', 'http://172.27.233.236:8080']:
        cors._origins = allowed_origin
        
@socketio.on('join') # a room is used to choose who to send data to
def join(room):
    join_room(room)
        
@app.route("/signup/", methods=["POST"]) #provided by teacher John Mortensen
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
                                samesite='None',  # cite
                                domain="172.27.233.236"
                                )
    return resp

@app.route('/auth/', methods=['GET']) #check if the user exists
@token_required
def auth(current_user):
    
    return jsonify({'pfp': current_user.pfp,
                    "username":current_user.username,
                    "userID":current_user.userID,
                    "joindate":current_user.date,
                    "bio":current_user.bio
                    })
    
@app.route('/createServer/',methods=["POST"]) #creates server 
@token_required
def createServer(current_user):
    data = request.get_json()
    server = Servers(name = data["name"],pfp = data["pfp"])
    db.session.add(server)  
    db.session.commit() 
    server_user = ServerUser(userID=current_user.id,serverID=server.id,userPermission="admin")   #server user is who exists in a server 
    db.session.add(server_user)
    db.session.commit()
    return jsonify({
        "name":data["name"],
        "pfp":data["pfp"],
        "serverID":server.id
    })

@app.route('/getServer/',methods=["GET"])
@token_required
def getServer(current_user):
    dbServerList = ServerUser.query.filter_by(userID=current_user.id).all()
    serverList = []
    for server in dbServerList:
        current_server = Servers.query.filter_by(id=server.serverID).first()
        serverList.append({
            'name':current_server.name,
            'pfp':current_server.pfp,
            'serverID':server.serverID
        })
    return jsonify({'servers': serverList})


@socketio.on("createChannel")
@token_required
def createChannel(current_user,json, methods=['POST']):
    channel = Channel(name = json["name"],serverID=json["serverID"])
    db.session.add(channel)  
    db.session.commit() 
    payload = {
        "channelID":channel.id,
        "name":json["name"]
    }
    socketio.emit("recieveChannelCreate",payload,room=f'Server:{json["serverID"]}')

@app.route('/getServerChannels/',methods=["POST"])
@token_required
def getServerChannels(current_user):
    data = request.get_json()
    dbChannelList = 0
    if(data["serverID"] == None):
        return jsonify({"error":"Body Missing!"})
    try:
        dbChannelList = Channel.query.filter_by(serverID = data["serverID"]).all()
    except:
        return jsonify({"error":"Server Does Not Exist!"})
    channelList = []
    serverName = Servers.query.filter_by(id=data["serverID"]).first().name
    for channel in dbChannelList:
        channelList.append({
            "name":channel.name,
            "channelID":channel.id
        })
    return jsonify({'channels': channelList,
                    'serverName':serverName})


    
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
                                samesite='None',  # cite
                                domain="172.27.233.236"
                                )
        return resp


    return make_response('Invalid Credentials',  401, {'Authentication': '"login required"'})

@socketio.on("sendServerMessage") #socketio to make the app realtime
@token_required
def sendServerMessage(current_user,json, methods=['GET', 'POST']):
    data = json
    message = Message(content = data["content"],channel=data["channel"],image=data["image"],user=current_user.id)
    db.session.add(message)  
    db.session.commit() 
    payload = {
        "name":current_user.username,
        'pfp':current_user.pfp,
        'message':data["content"],
        'date':message.date
    }
    socketio.emit("recieveServerMessage",payload,room=data["channel"])
    


@app.route('/getServerMessage/',methods=["POST"]) #query the server messages
@token_required
def getServerMessage(current_user):
    data = request.get_json()
    queryOffset = data["offset"]
    queryChannel = data["channel"]
    dbMessageList = Message.query.filter_by(channel=queryChannel).order_by(db.desc(Message.id)).offset(queryOffset).limit(5).all()
    messageList = []
    for message in dbMessageList:
        messageUser = Users.query.filter_by(id=message.user).first()
        messageList.append({
            'name':messageUser.username,
            'pfp':messageUser.pfp,
            'message':message.content,
            'date':message.date
        })
    channelName = Channel.query.filter_by(id=queryChannel).first().name
    return jsonify({'messages': messageList,
                    "channelName":channelName})

@app.route('/joinServer/',methods=["POST"])
@token_required
def joinServer(current_user):
    data = request.get_json()
    if(Servers.query.filter_by(id=data["serverID"]).first() is None):
        return "Invalid Server ID"
    if(ServerUser.query.filter(and_(ServerUser.userID==current_user.id, ServerUser.serverID==data["serverID"])).first() is not None):
        return "Already Joined"
        
    server_user = ServerUser(userID=current_user.id,serverID=data["serverID"],userPermission="default")   
    db.session.add(server_user)
    db.session.commit()
    return "Server Joined"
    


def run():
  socketio.run(app, host="0.0.0.0",port=6221)

initUserTable()
initChannelTable()
initServerTable()
initMessageTable()
initServerUser()
run()