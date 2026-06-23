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
    return app 

app=create_app()

#from application.model import * 

from application.controler import * 
if __name__=="__main__":
    with app.app_context():
        db.create_all()
        admin=User.query.filter_by(role='admin').first()
        if admin is None:
            admin=User(user_name='pammi_kumari', email='adminEmail@gmail.com',password='iamadmin',role='admin')
            db.session.add(admin)
            db.session.commit()
        

    app.run(debug=True)