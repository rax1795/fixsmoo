from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    userType = db.Column(db.String, db.ForeignKey('userType.userTypeID'), unique=False, nullable=False)
    points = db.Column(db.Integer, unique=False, nullable=True, default=0)
    password_hash = db.Column(db.String(128), nullable=False)
    
    cases = db.relationship("Case", backref="usr", uselist=True, cascade='all')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def serialize(self): 
        return {
            'username': self.username, 
            'points': self.points,
            'usertype': self.userType
            }

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class UserType(db.Model):
    __tablename__ = 'userType'
    userTypeID = db.Column(db.String, primary_key=True)
    userType = db.Column(db.String, unique=True, nullable=False)
    
    users = db.relationship("User", backref="usrtype")
    def serialize(self): 
        return {  
            'userTypeID': self.userTypeID, 
            'usertype': self.userType
            }

    def list(self): 
        tupple = (self.userTypeID, self.userType)
        return tupple

class Case(db.Model):
    __tablename__ = 'case'
    
    caseID = db.Column(db.Integer, primary_key=True)
    caseStatus = db.Column(db.String, db.ForeignKey('caseStatus.statusID'), unique=False, nullable=False, default='S01')
    dateTime = db.Column(db.DateTime, unique=False, index=True, default=datetime.utcnow)
    photoFilename = db.Column(db.String, default=None, nullable=True)
    photoURL = db.Column(db.String, default=None, nullable=True) #but ensure photo is compulsory field in field validation for fixsmoo app
    building = db.Column(db.String, db.ForeignKey("building.buildingID"), unique=False, nullable=False)
    location = db.Column(db.String, db.ForeignKey("location.locationID"), unique=False, nullable=False)
    level = db.Column(db.String, unique=False, nullable=True) #compulsory if building selected
    roomNum = db.Column(db.String, unique=False, nullable=True) #compulsory in buildings: free field
    typeOfFacility = db.Column(db.String, db.ForeignKey("facility.facilityID"), unique=False, nullable=False)
    severity = db.Column(db.String, db.ForeignKey("severity.severityID"), unique=False, nullable=False)
    comments = db.Column(db.String, unique=False, nullable=False)
    fixedDate = db.Column(db.DateTime, unique=False, nullable=True)
    adminComments = db.Column(db.String, unique=False, nullable=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'))
    check = db.Column(db.Integer, unique=False, nullable=False, default=0) # only contain 0 and 1, 0 for uncheck 1 for checked

    caseLogs = db.relationship("CaseLog", backref="cse", uselist=True, cascade='all')

    def __repr__(self):
        return '<Case {}>'.format(self.caseID)
    
    def serialize(self): 
        return {
            'caseID': self.caseID,
            'caseStatus': self.caseStatus,
            'dateTime': self.dateTime,
            'building': self.building,
            'location': self.location,
            'level': self.level,
            'roomNum': self.roomNum,
            'typeOfFacility': self.typeOfFacility,
            'severity': self.severity,
            'fixedDate': self.fixedDate,
            'comments': self.comments,
            'userID': self.userID
             }
             
    def serializeadmin(self): 
        return {
            'caseID': self.caseID,
            'caseStatus': self.caseStatus,
            'dateTime': self.dateTime,
            'building': self.building,
            'location': self.location,
            'level': self.level,
            'roomNum': self.roomNum,
            'typeOfFacility': self.typeOfFacility,
            'severity': self.severity,
            'fixedDate': self.fixedDate,
            'comments': self.comments,
            'check':self.check
             }


class Location(db.Model):
    __tablename__ = 'location'
    
    locationID = db.Column(db.String, primary_key=True)
    locationDesc = db.Column(db.String, unique=True, nullable=False)
    facilitiesTag = db.Column(db.String, unique=False, nullable=False)

    cases = db.relationship("Case", backref="lction", uselist=True, cascade='all')

    def list(self): 
        tupple = (self.locationID, self.locationDesc)
        return tupple

class Building(db.Model):
    __tablename__ = 'building'
    
    buildingID = db.Column(db.String, primary_key=True)
    buildingDesc = db.Column(db.String, unique=True, nullable=False)
    minLevel = db.Column(db.String, unique=False, nullable=True)
    maxLevel = db.Column(db.String, unique=False, nullable=True)
    locationTag = db.Column(db.String,unique=False,nullable=False)

    cases = db.relationship("Case", backref="bldg", uselist=True, cascade='all')
    
    def list(self): 
        tupple = (self.buildingID, self.buildingDesc)
        return tupple

class Facility(db.Model):
    __tablename__ = 'facility'
    
    facilityID = db.Column(db.String, primary_key=True)
    facilityDesc = db.Column(db.String, unique=True, nullable=False)

    cases = db.relationship("Case", backref="faclty", uselist=True, cascade='all')

    def list(self): 
        tupple = (self.facilityID, self.facilityDesc)
        return tupple

class Severity(db.Model):
    __tablename__ = 'severity'
    
    severityID = db.Column(db.String, primary_key=True)
    severityDesc = db.Column(db.String, unique=True, nullable=False)

    cases = db.relationship("Case", backref="svrty", uselist=True, cascade='all')

    def list(self): 
        tupple = (self.severityID, self.severityDesc)
        return tupple

class CaseStatus(db.Model):
    __tablename__ = 'caseStatus'
    
    statusID = db.Column(db.String, primary_key=True)
    statusDesc = db.Column(db.String, unique=True, nullable=False)

    cases = db.relationship("Case", backref="csestatus", uselist=True,cascade='all')
    caseLogs = db.relationship("CaseLog", backref="csestatus", uselist=True,cascade='all')

    def list(self): 
        tupple = (self.statusID, self.statusDesc)
        return tupple

class CaseLog(db.Model):
    __tablename__ = 'caseLog'
    
    logID = db.Column(db.Integer, primary_key=True)
    caseID = db.Column(db.Integer, db.ForeignKey("case.caseID"), unique=False, nullable=False)
    caseStatus = db.Column(db.String, db.ForeignKey("caseStatus.statusID"), unique=False, nullable=False)
    logDateTime = db.Column(db.DateTime, unique=False, nullable=False, default=datetime.utcnow)

    def serialize(self): 
        return {
            'logID': self.logID,
            'caseID': self.caseID,
            'caseStatus': self.caseStatus,
            'logDateTime': self.logDateTime
             }