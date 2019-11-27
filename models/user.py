from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    firstname = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    lastname = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    enrollment = db.Column(db.String(25), nullable=True)
    dhcba_member = db.Column(db.Integer, default=0)
    bar_no = db.Column(db.String(20),nullable=True)
    verified = db.Column(db.Integer, nullable=False, default=0)
    device_id = db.Column(db.String(255))
    registered_on = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, email, firstname, phone, lastname, password, verified, enrollment, dhcba_member, bar_no, device_id):
        self.email = email
        self.firstname = firstname
        self.phone = phone
        self.enrollment = enrollment
        self.dhcba_member = dhcba_member
        self.bar_no =  bar_no
        self.lastname = lastname
        self.password = password
        self.verified = verified
        self.device_id = device_id
