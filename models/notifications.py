from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .user import db


class Notifications(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(255))
    userid = db.Column(db.String(100))
    cause_list = db.Column(db.Boolean,default=True)
    nominated_counsel = db.Column(db.Boolean,default=True)
    judges_roster = db.Column(db.Boolean,default=True)
    bar_notifications = db.Column(db.Boolean,default=True)
    notices = db.Column(db.Boolean, default=True)
    events = db.Column(db.Boolean, default=True)
    obituary = db.Column(db.Boolean, default=True)
    electioncommittee = db.Column(db.Boolean, default=True)
    registered_on = db.Column(db.DateTime, default=datetime.now())

    def __init__(self,device_id, userid, cause_list=True, nominated_counsel=True, judges_roster=True, bar_notifications=True, notices=True, events=True, obituary=True, electioncommittee=True):

        self.device_id = device_id
        self.userid = userid
        self.cause_list = cause_list
        self.nominated_counsel = nominated_counsel
        self.judges_roster = judges_roster
        self.bar_notifications = bar_notifications
        self.notices = notices
        self.events = events
        self.obituary = obituary
        self.electioncommittee = electioncommittee

