from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models.user import db


class Compare_data(db.Model):
    """ Compare_data Model for storing and compare scrapped data"""
    __tablename__ = "compare_data"
    id = db.Column(db.Integer, primary_key=True)
    cause_list = db.Column(db.TEXT)
    nominated_counsel = db.Column(db.TEXT)
    judges_roster = db.Column(db.TEXT)

    registered_on = db.Column(db.DateTime, default=datetime.now())

    def __init__(self,id, cause_list=cause_list, nominated_counsel=nominated_counsel, judges_roster=judges_roster):
        self.id = id
        self.cause_list = cause_list
        self.nominated_counsel = nominated_counsel
        self.judges_roster = judges_roster
