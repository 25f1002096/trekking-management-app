from flask import Flask,redirect,url_for,make_response,render_template,request,session
from flask import current_app as app 
from .model import * 
from .database import db 
from flask_sqlalchemy import SQLAlchemy 
from flask_login import UserMixin,login_user,logout_user,login_manager,current_user,login_required
from flask_bcrypt import Bcrypt
bcrypt=Bcrypt(app)

@app.login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/directingToDashboard/', methods=['GET','POST'])  
def direct_to_dash():  #login logic 
    if request.method=='POST':
        name=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()
        
        

        if user:
            pas_s=user.password
            checked=bcrypt.check_password_hash(pas_s,password)
            
            if checked is True:
                login_user(user)
                if user.role=="Admin":
                    return redirect(url_for('adm_dash'))
                elif user.role=="Trek_Staff":
                    
                    return render_template('staff.html')
                elif user.role=="Trekker":
                    return render_template('user.html')#route link dena baaki hai 
                else:
                    return {'message':'Something went wrong'}
            else:
                return {'message':'Incorrect Password'}

        else:
            return {'message':'you are not a vaild user'}

    else:
        return render_template('login.html')


@app.route('/signinStaff/', methods=["GET","POST"])
def tekStaff():
    if request.method =='POST':
        username=request.form.get('username')
        email=request.form.get('email')
        contact=request.form.get('contact')
        pwd=request.form.get('password')
        n_pwd=bcrypt.generate_password_hash(pwd)
        new_user=User(user_name=username, email=email, password=n_pwd, role=Trek_Staff)
        new_user2=Trek_satff(staff_name=username, contact=contact,email=email)
        db.session.add(new_user)
        db.session.add(new_user2)
        db.session.commit()
        return render_template('staff.html')

    else:
        return render_template('stafsignin.html')


@app.route('/signinTrekker/', methods=['GET','POST'])
def usersignin():
    if request.method=='POST':
        username=request.form.get('username')
        email=request.form.get('email')
        
        pwd=request.form.get('password')
        new_pass=bcrypt.generate_password_hash(pwd)
        new_user=User(user_name=username, email=email, password=new_pass, role=Trekker)
        new_user2=Trekker(user_name=username)
        db.session.add(new_user)
        db.session.add(new_user2)
        db.session.commit()
        return render_template('user.html')

    else:
        return render_template('stafsignin.html')

# admin dashboard 
@login_required
@app.route('/adminDashboard/', methods=['GET','POST'])
def adm_dash():

    if current_user.role=='Admin':
        count_booking=Booking.query.count()
        count_staff=Trek_staff.query.count()
        count_treks=Trek.query.count()
        count_users=Trekker.query.count()
        data1=None
        data2=None 

        wait_staff=Trek_staff.query.filter_by(status='blacklist').all()
        approved_staff=Trek_staff.query.filter_by(status='blacklist').all()
        treks=Trek.query.all()
        if request.method=='POST':
            search_data=request.form.get('query')
            data1=User.query.filter_by(user_name=search_data).all()
            data2=Trek.query.filter_by(Trek_name=search_data).all()
            return render_template('admindash.html',data1=data1,data2=data2,count_User=count_users, count_staff=count_staff, count_treks=count_treks,count_booking=count_booking)
            
        else:
            
            return render_template('admindash.html',count_User=count_users, count_staff=count_staff, count_treks=count_treks,count_booking=count_booking)

    else:
        return {'message':'forbidden_acess'},403 


#trekstaff dashboard logic 
@login_required 
@app.route('/staffDashboard/', methods=['GET', 'POST'])
def staff_dash():
    if current_user.role=='Trek_Staff':
        #logic is yet to be defined
        pass 





    






        











                

                













