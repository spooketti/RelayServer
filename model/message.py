from init import db, app
from werkzeug.security import check_password_hash,generate_password_hash
import time

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer,primary_key=True)
    user = db.Column(db.Integer,db.ForeignKey('users.id'))
    date = db.Column(db.Integer,default=time.time())
    content = db.Column(db.Text)
    image = db.Column(db.Text)
    channel = db.Column(db.Integer,db.ForeignKey('channels.id'))
    
    def update(self, oldPW, newPW,username,pfp):
        if not check_password_hash(self.password, oldPW):
            return "Password does not match"
        
        if not newPW.isspace() and newPW != "":
            self.password = generate_password_hash(newPW,method='sha256')
        
        if not username.isspace() and username != "":
            self.username = username
        
        if not pfp.isspace() and pfp != "":
            self.pfp = pfp
            
        db.session.commit()
        
        return "Success"
      
    
def initMessageTable():
    with app.app_context():
        db.create_all()