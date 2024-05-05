from init import db, app
import time

class Users(db.Model):
    __tablename__ = "users"
    userID = db.Column(db.Text, unique=True)
    id = db.Column(db.Integer,primary_key=True)
    password = db.Column(db.Text)
    username = db.Column(db.Text)
    pfp = db.Column(db.Text)
    bio = db.Column(db.Text)
    date = db.Column(db.Text,default=time.time())
      
    
def initUserTable():
    with app.app_context():
        db.create_all()