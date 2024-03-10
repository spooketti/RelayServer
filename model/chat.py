from init import db, app
from werkzeug.security import check_password_hash,generate_password_hash
from datetime import datetime

class DM(db.Model):
    __tablename__ = "dm"
    id = db.Column(db.Integer,primary_key=True)
    message = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    sender = db.Column(db.Integer,db.ForeignKey('users.id'))
    recipient = db.Column(db.Integer,db.ForeignKey('users.id'))
      
    
def initDMTable():
    with app.app_context():
        db.create_all()