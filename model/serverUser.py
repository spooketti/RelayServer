from init import db, app

class ServerUser(db.Model):
    __tablename__ = "server_user"
    userID = db.Column(db.Integer, db.ForeignKey('users.id'))
    serverID = db.Column(db.Integer,db.ForeignKey('servers.id'))
    userPermission = db.Column(db.Text)
    id = db.Column(db.Integer,primary_key=True)
      
    
def initServerUser():
    with app.app_context():
        db.create_all()