from flask import Flask, request, jsonify, make_response, Response
from threading import Thread
from init import app
from flask_sqlalchemy import SQLAlchemy 
from authToken import token_required
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from init import db, cors
import time
import datetime
import os


@app.route('/')
def home():
    return "Relay's Server"

@app.before_request
def before_request():
    # Check if the request came from a specific origin
    allowed_origin = request.headers.get('Origin')
    if allowed_origin in ['http://localhost:4100', 'http://172.27.233.236:3000', 'https://spooketti.github.io']:
        cors._origins = allowed_origin

def run():
  app.run(host='0.0.0.0',port=6221)

run()