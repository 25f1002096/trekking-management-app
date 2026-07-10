from flask import Flask,redirect,url_for,make_response,render_template,request,session,flash 
from flask import current_app as app 
from .model import * 
from .database import db 
from flask_sqlalchemy import SQLAlchemy 
from datetime import date ,datetime
from flask_login import UserMixin,login_user,logout_user,login_manager,current_user,login_required
from flask_bcrypt import Bcrypt
bcrypt=Bcrypt(app)

@app.login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
        exist_email=User.query.filter_by(email=email).first()
        if exist_email:
            return {'message':'please signin with another email'}
        else:
            new_user=User(user_name=username, email=email, password=n_pwd, role='Trek_Staff')
            new_user2=Trek_staff(staff_name=username, contact=contact,email=email)
            
            db.session.add(new_user)
            db.session.add(new_user2)
            db.session.commit()
            login_user(new_user)
            flash('signin successfully', 'success') 
            return redirect(url_for('staff_dash')) #route link dena baaki hai

    else:
        return render_template('stafsignin.html')


@app.route('/signinTrekker/', methods=['GET','POST'])
def usersignin():
    if request.method=='POST':
        username=request.form.get('username')
        email=request.form.get('email')
        exist=User.query.filter_by(email=email).first()
        pwd=request.form.get('password')
        new_pass=bcrypt.generate_password_hash(pwd)
        if exist:
            return {'message':'please signin with another email'}
        else:
            new_user=User(user_name=username, email=email, password=new_pass, role='Trekker')
            new_user2=Trekker(user_name=username,email=email)
            db.session.add(new_user)
            db.session.add(new_user2)
            db.session.commit() 
            login_user(new_user)
            flash('signin successfully', 'success') 
            return redirect(url_for('user_dash')) #route link dena baaki hai 

    else:
        return render_template('usersign.html')

# admin dashboard 
@login_required 
@app.route('/adminDashboard/', methods=['GET','POST'])
def adm_dash():
    #print(current_user.__dict__) 
    if current_user.role=='Admin':
        count_booking=Booking.query.count()
        count_staff=Trek_staff.query.count()
        count_treks=Trek.query.count()
        count_users=Trekker.query.count()
        data1=None
        data2=None 

        wait_staff=Trek_staff.query.filter_by(status='blacklist').all()
        approved_staff=Trek_staff.query.filter_by(status='approved').all()
        treks=Trek.query.all()
        if request.method=='POST':
            search_data=request.form.get('seaq')
            data1=Trek_staff.query.filter(Trek_staff.staff_name.ilike(f'%{search_data}%')).all()
            data2=Trek.query.filter(Trek.Trek_name.ilike(f'%{search_data}%')).all() 
            return render_template('admindash.html',data1=data1,data2=data2,count_User=count_users, count_staff=count_staff, count_treks=count_treks,count_booking=count_booking,wait_staff=wait_staff, approved_staff=approved_staff, treks=treks)
            
        else:
            
            return render_template('admindash.html',count_User=count_users, count_staff=count_staff, count_treks=count_treks,count_booking=count_booking,wait_staff=wait_staff, approved_staff=approved_staff, treks=treks)
 

#blacklisting/approving staff
@login_required 
@app.route('/blacklist/staff/<staff_id>/')
def black_staff(staff_id):
    staff=Trek_staff.query.filter_by(staff_id=staff_id).first()
    if staff.status=='blacklist':
        staff.status='approved'
        db.session.commit()
    else:
        staff.status='blacklist'
        db.session.commit()
    flash('action done successfully','success')
    return redirect(url_for('adm_dash'))


#all user seen in admin dashboard
@login_required
@app.route('/admin/user/', methods=['GET','POST'])
def user():
    user=Trekker.query.all()
    book=Booking.query.all()
    if request.method=='POST':
        user_id=request.form.get('user_id')
        trekker=Trekker.query.filter_by(user_id=user_id).first()
        if trekker.status=='notblacklist':
            trekker.status='blacklist'
        else:
            trekker.status='notblacklist'
        db.session.commit()
        return render_template('useradmin.html', user=user,book=book)

    
    else:
        return render_template('useradmin.html', user=user,book=book)



# creat trek logic 
@login_required
@app.route('/createTrek/byadmin/', methods=['GET','POST'])
def create_trek():
    staff_id=Trek_staff.query.all()
    today=date.today() 
    if request.method=='POST':
        trek_name=request.form.get('trek_name')
        location=request.form.get('location')
        difficulty=request.form.get('difficulty')
        duration=request.form.get('duration')
        total_slot=request.form.get('slot')
        s_date=request.form.get('start')
        ss_date=datetime.strptime(s_date, "%Y-%m-%d").date()
    
        e_date=request.form.get('end_date')
        ee_date=datetime.strptime(e_date, "%Y-%m-%d").date()
        rute=request.form.get('rute')
        assigned_staff=request.form.getlist('staff')
        status=request.form.get('status')
        status2=request.form.get('mark')

        new_trek=Trek(Trek_name=trek_name, Difficulty=difficulty,route=rute, Duration=duration,status=status, status2=status2, location=location, s_date=ss_date, e_date=ee_date, total_slot=total_slot, Available_slot=total_slot)
        db.session.add(new_trek)

        print(assigned_staff)
    
        if assigned_staff:
            for row in assigned_staff:
                staff_member=Trek_staff.query.filter_by(staff_id=row).first()
                if staff_member:

                    new_trek.assigned_staff.append(staff_member) 
                
        db.session.commit()
        

        return redirect(url_for('adm_dash'))


    else:
        return render_template('createtreks.html', data=staff_id, today=today)


#edit trek by admin 
@login_required
@app.route('/admin/trek/edit/<trek_id>/', methods=['GET','POST'] )
def edit_trek(trek_id):
    trek=Trek.query.filter_by(trek_id=trek_id).first()
    data=trek.assigned_staff
    today=date.today()
    if request.method=='POST':
        trek_name=request.form.get('trek_name')
        location=request.form.get('location')
        difficulty=request.form.get('difficulty')
        duration=request.form.get('duration')
        rute=request.form.get('rute')
        total_slot=request.form.get('slot')
        s_date=request.form.get('start')
        ss_date=datetime.strptime(s_date, "%Y-%m-%d").date()
        e_date=request.form.get('end_date')
        ee_date=datetime.strptime(e_date,"%Y-%m-%d").date()
        assign_staff=request.form.getlist('staff')
        status=request.form.get('status')
        status2=request.form.get('mark')

        trek.Trek_name=trek_name 
        trek.Difficulty=difficulty 
        trek.route=rute 
        trek.Duration=duration 
        trek.status=status 
        trek.status2=status2 
        trek.location=location 
        trek.s_date=ss_date 
        trek.e_date=ee_date 
        trek.total_slot=total_slot 
        trek.assigned_staff=assign_staff 
        trek.Available_slot=int(total_slot)-len(trek.book) 
        db.session.commit() 
        return redirect(url_for('adm_dash'))

    else:
        return render_template('editTrekadm.html', trek=trek, data=data,today=today)
    

#remove trek logic  admin section 
@login_required 
@app.route('/admin/trek/remove/<trek_id>/')
def remove_trek(trek_id):
    if current_user.role=='Admin':
        trek=Trek.query.filter_by(trek_id=trek_id).first()
        staff=Trek_staff_association.query.filter_by(trek_id=trek_id).delete()
        
        db.session.delete(trek)
        db.session.commit()
        return redirect(url_for('adm_dash'))

# trek_staff history admin section 
@login_required 
@app.route('/admin/staff/history/<staff_id>/')
def staff_history(staff_id):
    staff=Trek_staff.query.filter_by(staff_id=staff_id).first()
    assigned_treks=staff.treks_assigned 
    return render_template('staffadmhis.html',assigned_treks=assigned_treks)





#trekstaff dashboard logic 
@login_required 
@app.route('/staffDashboard/', methods=['GET', 'POST'])
def staff_dash():
    if current_user.role=='Trek_Staff':
        staff_id=current_user.email 
        real_staff_id=Trek_staff.query.filter_by(email=staff_id).first() #<trek_staff 1>
        print(staff_id)
        print(real_staff_id)
        if request.method=='GET':
            assigned_treks = Trek_staff_association.query.filter_by(staff_id=real_staff_id.staff_id).count()
            staff = Trek_staff.query.filter_by(email=staff_id).first()
            print(staff)
            total=0 #total_participants 
            status='None'
            treks_Ides=[]
            open_treks=0
            if staff:
            
                status=staff.status 
                treks_Ides=staff.treks_assigned 
                    
                for trekid in treks_Ides:
                        if trekid.status=='Open':
                            open_treks +=1
                        participants=trekid.total_slot-trekid.Available_slot
                        total += participants 
            print(status) 
            print(treks_Ides)
            return render_template('staff.html', status=status, assigned_treks=assigned_treks, total_participants=total, open_treks=open_treks, trek_Ides=treks_Ides)


        
            #logic is yet to be defined 

#manage_trek logic managed by staff
@login_required
@app.route('/manageTrek/<trek_id>/', methods=['GET','POST'])
def manageTrek(trek_id):
    trek=Trek.query.filter_by(trek_id=trek_id).first()
    c_oun=len(trek.book)
    trek.Available_slot=int(trek.total_slot)-c_oun 
    db.session.commit() 
    if request.method=='POST':
        
        total_slot=request.form.get('total_slot')
        status=request.form.get('status')
        mark=request.form.get('mark')
        av1=int(total_slot)- len(trek.book)
        trek1=Trek.query.filter_by(trek_id=trek_id).update(dict(total_slot=total_slot))
        trek2=Trek.query.filter_by(trek_id=trek_id).update(dict(Available_slot=av1))
        db.session.commit()
        if mark=="start":
            trek=Trek.query.filter_by(trek_id=trek_id).update(dict(status2='start'))
            db.session.commit()
        elif mark=="complete":
            trek=Trek.query.filter_by(trek_id=trek_id).update(dict( status='complete'))
            db.session.commit()

           


        if status=="Open":
            trek=Trek.query.filter_by(trek_id=trek_id).update(dict( status='Open'))
            db.session.commit()
        else:
            trek=Trek.query.filter_by(trek_id=trek_id).update(dict(status='Closed'))
            db.session.commit() 
        
        flash('Update successfully', 'success')
        return redirect(url_for('staff_dash'))


    else:
        user_email=current_user.email
        
        staff = Trek_staff.query.filter_by(email=user_email).first() #<trek_staff 1>
        #assigned_treks=staff. treks_assigned #list of trek id object  
        if current_user.role=='Trek_Staff' and staff in trek.assigned_staff :
               #trek_booking=[] #list of book id 
               #for row in assigned_treks:
               trek_booking=trek.book #list of book id object  
               participant_number=len(trek_booking)
               
               return render_template('manageTrek.html', trek=trek, trek_booking=trek_booking, participant=participant_number)



@login_required
@app.route('/userDashboard/', methods=['GET', 'POST'])
def user_dash():
    if current_user.role == 'Trekker':
        user=current_user.user_name
        user_id=current_user.email 
        
        status=Trekker.query.filter_by(email=user_id).first() 
        trek=Trek.query.filter_by(status='Open').all()
        location=db.session.query(Trek.location.distinct()).all()
        print(location)
        
           

        
        if request.method=="POST":
            search_data=request.form.get('search_data')
            difficulty=request.form.get('difficulty')
            location1=request.form.get('location')
            data='None'
            if search_data:
                trek_data=Trek.query.filter(Trek.Trek_name.ilike(f'%{search_data}%'))

            if difficulty and location1 :
                data=Trek.query.filter_by(Difficulty=difficulty,location=location1).all()

            elif difficulty or location :
                if difficulty:
                    data=Trek.query.filter_by(Difficulty=difficulty).all()
                else:
                    data=Trek.query.filter_by(location=location1).all() 
                    
                    
            return render_template('user.html',location=location,trek_data=trek_data,data=data,Treks=trek, user_id=status,user=user,status=status ) 

        else:
            return render_template('user.html',location=location,Treks=trek, user_id=status,user=user,status=status) 

    else:
        return {'message':'forbidend_acess'},403 

@login_required
@app.route("/booking/details/<trek_id>/" ) 
def booking(trek_id): # book trekking logic 
    trek=Trek.query.filter_by(trek_id=trek_id).first()
    user=current_user.user_name
    user_email=current_user.email 
    trekker=Trekker.query.filter_by(email=user_email).first()
    

    
    book=Booking(status='Booked', payment_status='payed',booking_date=date.today(), trek=trek, owener=trekker)
        
    db.session.add(book)    
    db.session.commit()
          
    trek.Available_slot=int(trek.Available_slot)-1
    db.session.commit()
    return render_template('book.html', book=book,user=user)


#booking cancle logic in user section 
@login_required 
@app.route('/user/booking/cancle/<book_id>/', methods=['GET','POST'])
def cancle_book(book_id):
    book=Booking.query.filter_by(Book_id=book_id).first()
    trek=book.trek 
    if request.method=='POST':
        cancle=request.form.get('cancle')
        if cancle:
            book.status="Cancelled"
            db.session.commit()
            
            trek.Available_slot=int(trek.Available_slot)+1
            db.session.commit()


            return redirect(url_for('user_dash'))

    else:
        return redirect(url_for('user_dash'))
        



@login_required
@app.route('/user/history/<user_id>/')
def userHistory(user_id):
    user=Trekker.query.get(user_id)
    booking=user.booking 
    
    return render_template('userhistory.html', booking=booking)


@login_required 
@app.route('/staff/dash/profile/', methods=['GET','POST'])
def profile():

    if request.method=='POST':
        staff_name=request.form.get('staff_name')
        email=request.form.get('email')
        contact=request.form.get('contact')
        data_staff=Trek_staff.query.filter_by(email=email).first()
        data_user=Trekker.query.filter_by(email=email).first()
        if data_staff:
            data_staff.staff_name=staff_name 
            data_staff.email=email 
            if contact:
             data_staff.contact=contact
        elif data_user:
            data_user.user_name=staff_name 
            data_user.email=email 
        
        user_table=User.query.filter_by(email=email).first()
        user_table.user_name=staff_name 
        user_table.email=email 
        db.session.commit() 

        if current_user.role=='Trek_Staff':
            return redirect(url_for('staff_dash'))
        else:
            return redirect(url_for('user_dash'))

    elif request.method=='GET':
        if current_user.role=="Trek_Staff":
            email=current_user.email 
            staff=Trek_staff.query.filter_by(email=email).first()
            return render_template('profile.html',staff=staff)

        else:
            email=current_user.email 
            user=Trekker.query.filter_by(email=email).first() 
            return render_template('profile.html',user=user)
         

    



            
            











    






        











                

                













