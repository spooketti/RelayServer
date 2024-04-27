from init import db, app
from werkzeug.security import check_password_hash,generate_password_hash
from datetime import datetime

class ServerUser(db.Model):
    __tablename__ = "server_user"
    userID = db.Column(db.Integer, db.ForeignKey('users.id'))
    serverID = db.Column(db.Integer,db.ForeignKey('servers.id'))
    userPermission = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    id = db.Column(db.Integer,primary_key=True)
    #users = db.relationship('User', secondary=user_server_association,back_populates='servers')
    
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
      
    
def initServerUser():
    with app.app_context():
        db.create_all()