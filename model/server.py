from init import db, app
import time

class Servers(db.Model):
    __tablename__ = "servers"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.Text)
    pfp = db.Column(db.Text)
    date = db.Column(db.Integer,default=time.time())
      
    
def initServerTable():
    with app.app_context():
        db.create_all()