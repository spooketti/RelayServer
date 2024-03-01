from init import db, app
from werkzeug.security import check_password_hash,generate_password_hash

class Users(db.Model):
    __tablename__ = "users"
    userID = db.Column(db.Text, unique=True)
    id = db.Column(db.Integer,primary_key=True)
    password = db.Column(db.Text)
    name = db.Column(db.Text)
    username = db.Column(db.Text)
    pfp = db.Column(db.Text)
    
    def update(self, oldPW, newPW,name,username,pfp):
        if not check_password_hash(self.password, oldPW):
            return "Password does not match"
        
        if not newPW.isspace() and newPW != "":
            self.password = generate_password_hash(newPW,method='sha256')
        
        if not name.isspace() and name != "":
            self.name = name
        
        if not username.isspace() and username != "":
            self.username = username
        
        if not pfp.isspace() and pfp != "":
            self.pfp = pfp
            
        db.session.commit()
        
        return "Success"
      
    
def initUserTable():
    with app.app_context():
        db.create_all()