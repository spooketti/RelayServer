from init import db, app
import time

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer,primary_key=True)
    user = db.Column(db.Integer,db.ForeignKey('users.id'))
    date = db.Column(db.Integer,default=time.time())
    content = db.Column(db.Text)
    image = db.Column(db.Text)
    channel = db.Column(db.Integer,db.ForeignKey('channels.id'))
      
    
def initMessageTable():
    with app.app_context():
        db.create_all()
