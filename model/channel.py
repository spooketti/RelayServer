from init import db, app

class Channel(db.Model):
    __tablename__ = "channels"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.Text)
    serverID = db.Column(db.Integer,db.ForeignKey('servers.id'))
      
    
def initChannelTable():
    with app.app_context():
        db.create_all()
