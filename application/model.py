from .database import db 
from flask_login import UserMixin,login_user,logout_user,login_manager,current_user
from datetime import datetime

#user class
class User(db.Model,UserMixin):
    __tablename__='user'
    user_id=db.Column(db.Integer,primary_key=True, autoincrement=True)
    user_name=db.Column(db.String(20), nullable=False)
    email=db.Column(db.String(100),nullable=False,unique=True)
    password=db.Column(db.String, nullable=False)
    role=db.Column(db.String, nullable=False)  #User (role: Admin / Trek_Staff / Trekker)

    def get_id(self):
        return str(self.user_id)




class Trek(db.Model):
    __tablename__='trek'
    trek_id=db.Column(db.Integer,primary_key=True, autoincrement=True)
    Trek_name=db.Column(db.String,nullable=False)
    Difficulty=db.Column(db.String,nullable=False) #Easy,Moderate,Hard
    route=db.Column(db.String,nullable=False)
    Duration=db.Column(db.String,nullable=False)
    Available_slot=db.Column(db.Integer,nullable=False)
    #assigned_staff_id=db.Column(db.String,nullable=False)
    status=db.Column(db.String,nullable=False, default='Closed') #Status (Pending / Approved / Open / Closed / Completed)
    location=db.Column(db.String,nullable=False)
    s_date=db.Column(db.DateTime,default=datetime.now)
    e_date=db.Column(db.DateTime)
    assigned_staff=db.relationship('Trek_staff',secondary="trek_staff_association",back_populates="treks_assigned")
    book=db.relationship('Booking', back_populates="trek") 

class Booking(db.Model): #many booking have one trekker
    __tablename__='booking'
    Book_id=db.Column(db.Integer,primary_key=True, autoincrement=True)
    user_id=db.Column(db.Integer,db.ForeignKey("trekker.user_id"), nullable=False)
    trek_id=db.Column(db.Integer,db.ForeignKey("trek.trek_id"), nullable=False)
    booking_date=db.Column(db.DateTime)
    status=db.Column(db.String,nullable=False)  #Booked / Cancelled / Completed
    payment_status=db.Column(db.String,nullable=False) #payed,not payed
    owener=db.relationship('Trekker', back_populates="booking")
    trek=db.relationship('Trek', back_populates="book")

class Trekker(db.Model): #it is user who use the app one treeker have many bokking
    __tablename__='trekker'
    user_id=db.Column(db.Integer, nullable=False,primary_key=True,autoincrement=True)
    
    user_name=db.Column(db.String, nullable=False)
    booking=db.relationship('Booking',back_populates="owener")
    status=db.Column(db.String,default='notblacklist')#blacklist,notblacklist


class Trek_staff(db.Model):
    __tablename__='trek_staff'
    staff_id=db.Column(db.Integer, nullable=False,primary_key=True,autoincrement=True)
    staff_name=db.Column(db.String, nullable=False)
    trek_id=db.Column(db.String,db.ForeignKey("trek.trek_id"), nullable=False)
    email=db.Column(db.String, nullable=False)
    treks_assigned=db.relationship('Trek',secondary="trek_staff_association", back_populates="assigned_staff") 
    status=db.Column(db.String, default='blacklist')#blacklist,approved 
    contact=db.Column(db.Integer,nullable=False) 


class Trek_staff_association(db.Model):
    __tablename__='trek_staff_association'
    staff_id=db.Column(db.Integer, db.ForeignKey('trek_staff.staff_id'), primary_key=True, nullable=False)
    trek_id=db.Column(db.Integer, db.ForeignKey('trek.trek_id'), primary_key=True, nullable=False)


    








