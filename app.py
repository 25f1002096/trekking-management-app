from flask import Flask
#from flask_restful import Api 
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from functools import wraps 
 
app=None
from application.database import db 
def create_app():
    app=Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///trekking-management-app.sqlite3'
    app.config['SECRET_KEY']='12%^&*FGTRvgab!(*)bnHJvcxzO???:"((***&&&}))'
    db.init_app(app)
    app.app_context().push()
    login_manager=LoginManager()
    login_manager.init_app(app)
    login_manager.login_view='login'
    return app 

app=create_app()

#from application.model import * 

from application.controler import * 
if __name__=="__main__":
    with app.app_context():
        db.create_all()
        admin=User.query.filter_by(role='admin').first()
        if admin is None:
            pin='iamadmin'
            hash_pin=bcrypt.generate_password_hash(pin)
            admin=User(user_name='pammi_kumari', email='adminEmail@gmail.com',password=hash_pin,role='Admin')
            
            db.session.add(admin)
            db.session.commit()
            
        

    app.run(debug=True,use_reloader=False)