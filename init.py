from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask("Relay Server")
cors = CORS(app, supports_credentials=True)
dbURI = 'sqlite:///sqlite.db'
app.config['SQLALCHEMY_DATABASE_URI'] = dbURI
app.config['SECRET_KEY'] = "test" #os.getenv("SECRET_KEY")
db = SQLAlchemy(app)    
socketio = SocketIO(app, cors_allowed_origins="*")

# Images storage
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # maximum size of uploaded content
app.config['UPLOAD_EXTENSIONS'] = ['.jpeg','.jpg', '.png', '.gif']  # supported file types
app.config['UPLOAD_FOLDER'] = 'upload/'  # location of user uploaded content
