from flask import Flask,redirect,url_for,make_response,render_template,request,session,flash 
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
                    flash('logedin successfully', 'success')
                    return redirect(url_for('adm_dash'))
                elif user.role=="Trek_Staff":
                    flash('logedin successfully', 'success')
                    return redirect(url_for('staff_dash'))
                elif user.role=="Trekker":
                    flash('logedin successfully', 'success')
                    return redirect(url_for('user_dash')) #route link dena baaki hai,ab ho gya 
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
        flash('signin successfully', 'success')
        return redirect(url_for('staff_dash')) #route link dena baaki hai

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
        return redirect(url_for('user_dash')) #route link dena baaki hai 

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


# creat trek logic 
@login_required
@app.route('/createTrek/byadmin/', methods=['GET','POST'])
def create_trek():
    staff_id=Trek_staff.query.all() 
    if request.method=='POST':
        trek_name=request.form.get('trek_name')
        location=request.form.get('location')
        difficulty=request.form.get('difficulty')
        duration=request.form.get('duration')
        total_slot=request.form.get('slot')
        s_date=request.form.get('start')
    
        e_date=request.form.get('end_date')
        rute=request.form.get('rute')
        assigned_staff=request.form.getlist('staff')
        status=request.form.get('status')
        status2=request.form.get('mark')
        new_trek=Trek(Trek_name=trek_name, Difficulty=difficulty,route=rute, Duration=duration,status=status, status2=status2, location=location, s_date=s_date, e_date=e_date, total_slot=total_slot)
        db.session.add(new_trek)
        
        for row in assigned_staff:
            ides=Trek_satff.query.get(row)
            new_trek.assigned_staff=ides 
            
        db.session.commit()





    else:
        return render_template('createtreks.html', data=staff_id)




#trekstaff dashboard logic 
@login_required 
@app.route('/staffDashboard/', methods=['GET', 'POST'])
def staff_dash():
    if current_user.role=='Trek_Staff':
        staff_id=current_user.user_id 
        if request.method=='GET':
            assigned_treks = Trek_staff_association.query.filter_by(staff_id=staff_id).count()
            staff = Trek_staff.query.filter_by(staff_id=staff_id).first()
            total=0 #total_participants 
            
            open_treks=0
            if staff:
                status=staff.status 
                treks_Ides=staff.treks_assigned 
                
                for trekid in treks_Ides:
                    if trekid.status=='Open':
                        open_treks +=1
                    participants=trekid.total_slot-trekid.Available_slot
                    total += participants  
            return render_template('staff.html' status=status, assigned_treks=assigned_treks, total_participants=total, open_treks=open_treks, trek_Ides=treks_Ides)


        else:
            pass 
            #logic is yet to be defined 

#manage_trek logic 
@login_required
@app.route('/manageTrek/<trek_id>/', methods=['GET','POST'])
def manageTrek(trek_id):
    trek=Trek.query.filter_by(trek_id=trek_id).first()
    if request.method=='POST':
        
        total_slot=request.form.get('total_slot')
        status=request.form.get('status')
        mark=request.form.get('mark')
        if mark=="1":
            trek=Trek.query.filter_by(trek_id=trek_id).update(dict(status2='start'))
            db.session.commit()
        elif mark=="2":
            trek=Trek.query.filter_by(trek_id=trek_id).update(dict( status='complete'))
            db.session.commit()

           


        if status=="2":
            trek=Trek.query.filter_by(trek_id=trek_id).update(dict( status='Open'))
            db.session.commit()
        else:
            trek=Trek.query.filter_by(trek_id=trek_id).update(dict(status='Closed'))
            db.session.commit() 
        
        flash('Update successfully', 'success')
        return redirect(url_for('adm_dash'))

        

        

    else:
        user_id=current_user.user_id
        staff = Trek_staff.query.filter_by(staff_id=user_id).first()
        assigned_treks=staff. treks_assigned #list of trek id 
        if current_user.role=='Trek_Staff' and trek_id in assigned_treks:
               trek_booking=assigned_treks.book #list of book id  
               participant_number=len(terk_booking)
               
               return render_template('manageTrek.html', trek=trek, trek_booking=trek_booking, participant=participant)



@login_required
@app.route('/userDashboard/', methods=['GET', 'POST'])
def user_dash():
    if current_user.role == 'Trekker':
        pass 





    






        











                

                













