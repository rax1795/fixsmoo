from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, EqualTo
from flask_wtf.file import FileField, FileRequired, FileAllowed
from app.models import *
from app import images


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

user = UserType.query.all()
userlist = []
for i in user:
    userlist.append(i.list())

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    usertype = SelectField('User', choices=userlist)
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

building = Building.query.all()
buildinglist = []
for i in building:
    buildinglist.append(i.list())

location = Location.query.all()
locationlist = []
for i in location:
    locationlist.append(i.list())

severity = Severity.query.all()
severitylist = []
for i in severity:
    severitylist.append(i.list())

facility = Facility.query.all()
facilitylist = []
for i in facility:
    facilitylist.append(i.list())

status = CaseStatus.query.all()
statuslist = []
for i in status:
    statuslist.append(i.list())

class CaseForm(FlaskForm):
    building = SelectField('Where on campus is the issue?', choices=buildinglist)
    level = SelectField('What level is it on?', choices=[])
    location = SelectField('What location is it at?', choices=locationlist)
    unit = StringField('What is the closest room or facility number? (eg. GSR2-02)', validators=[DataRequired()])
    facility = SelectField('What facility item has an issue?', choices=facilitylist)
    description = TextAreaField('Please describe the issue', validators=[DataRequired()],)
    photo = FileField('Any photos of the issue?',validators=[FileRequired()])
    severity = SelectField('How severe is the issue?', choices=severitylist)
    submit = SubmitField('Submit')

class EditCaseForm(FlaskForm):
    building = SelectField('building', choices=buildinglist)
    level = SelectField('level', choices=[])
    location = SelectField('location', choices=locationlist)
    unit = StringField('RoomNum', validators=[DataRequired()])
    facility = SelectField('Faility', choices=facilitylist)
    description = TextAreaField('User Description', validators=[DataRequired()],)
    severity = SelectField('How severe is the issue?', choices=severitylist)
    submit = SubmitField('Submit')

class EditAdminCaseForm(FlaskForm):
    building = SelectField('building', choices=buildinglist)
    level = SelectField('level', choices=[])
    location = SelectField('location', choices=locationlist)
    unit = StringField('RoomNum', validators=[DataRequired()])
    facility = SelectField('Faility', choices=facilitylist)
    description = TextAreaField('User Description', validators=[DataRequired()],)
    severity = SelectField('How severe is the issue?', choices=severitylist)
    adminComments = TextAreaField('Admin Comments')
    status = SelectField('status', choices=statuslist)
    submit = SubmitField('Submit')

class CaseSearchForm(FlaskForm):
    caseid = StringField('CaseID', validators=[DataRequired()])
    search = SubmitField('Search')


case = Case.query.all()
caseList = []
for i in user:
    caseList.append(i.list())


class FilterForm(FlaskForm):
    building = SelectField('Building', choices=buildinglist)
    facility = SelectField('Facilities', choices=facilitylist)
    status = SelectField('Status', choices=statuslist)
    severity = SelectField('Severity', choices=severitylist)
    submit = SubmitField('Filter')
