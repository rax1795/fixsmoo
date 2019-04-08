from flask import render_template, flash, redirect, url_for, request, jsonify, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db, login, images
from app.forms import *
from app.models import *
from werkzeug.utils import secure_filename
from app.chart_initialisation import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine,DateTime
from datetime import datetime

@app.route('/index')
@login_required
def index():
    user = current_user.get_id()
    user=User.query.filter_by(id=user).first() 
    return render_template('index.html', title='Home', user=user)

@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html', title='Home')

@app.route('/loginadmin', methods=['GET', 'POST'])
def loginadmin():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data,userType='U5').first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login')),flash('Invalid username or password or you are not authorized')
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashboard')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/guestlogin', methods=['GET', 'POST'])
def guestlogin():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.query.filter_by(username="guest").first()
    login_user(user)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('index')
    return redirect(next_page)

@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    case = Case.query.all()
    val1=0
    val2=0
    val3=0

    for i in case:
        eachCase = i.serialize()
        if eachCase['caseStatus'] == 'S01':
            val1 += 1
        else:
            val1=val1
        if eachCase['caseStatus'] == "S02":
            val2 += 1
        else:
            val2=val2
        if eachCase['caseStatus'] == "S03":
            val3 += 1
        else:
            val3=val3
    caseid = ''
    dtnow= (datetime.now()).strftime("%d-%m-%y %H:%M")
    print(dtnow)
    engine = create_engine('postgresql://admin1:password@localhost:5432/fixsmoo', convert_unicode=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    searchlist=[]
    # potential_duplicate = check_duplicate()
    potential_duplicate = {}
    if request.method=="POST":
        try:
            if request.form['check']:
                potential_duplicate = check_duplicate()
                if len(potential_duplicate) == 0:
                    potential_duplicate = {"None":{"Nothing":0}}
                return render_template('dashboard.html',title='Dashboard', values1=val1,values2=val2,values3=val3, searchlist=searchlist,potential_duplicate=potential_duplicate,timenow=dtnow,active="duplicatetab")
        except:
            try:
            # if len(request.form['searchcaselog'])>0:
                caseid = request.form['searchcaselog']
                searchtable = session.query(CaseLog,CaseStatus,Case,Building,Location,User).filter(CaseLog.caseID == caseid).filter(CaseLog.caseID==Case.caseID).filter(CaseLog.caseStatus==CaseStatus.statusID).filter(Case.building==Building.buildingID).filter(Case.location==Location.locationID).filter(Case.userID==User.id).all()
                searchlist=caseLogRetrieve(searchtable)
                return render_template('dashboard.html',title='Dashboard', values1=val1,values2=val2,values3=val3,searchlist=searchlist,potential_duplicate=potential_duplicate,timenow=dtnow,active = "searchtab")
            except:
                searchtable = session.query(CaseLog,CaseStatus,Case,Building,Location,User).filter(CaseLog.caseID==Case.caseID).filter(CaseLog.caseStatus==CaseStatus.statusID).filter(Case.building==Building.buildingID).filter(Case.location==Location.locationID).filter(Case.userID==User.id).all()
                searchlist=caseLogRetrieve(searchtable)
                return render_template('dashboard.html',title='Dashboard', values1=val1,values2=val2,values3=val3, searchlist=searchlist,potential_duplicate=potential_duplicate,timenow=dtnow,active="searchtab")
    else:
        searchtable = session.query(CaseLog,CaseStatus,Case,Building,Location,User).filter(CaseLog.caseID==Case.caseID).filter(CaseLog.caseStatus==CaseStatus.statusID).filter(Case.building==Building.buildingID).filter(Case.location==Location.locationID).filter(Case.userID==User.id).all()
        searchlist=caseLogRetrieve(searchtable)
        return render_template('dashboard.html',title='Dashboard', values1=val1,values2=val2,values3=val3, searchlist=searchlist,potential_duplicate=potential_duplicate,timenow=dtnow,active="dashboardtab")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, userType=form.usertype.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login')), flash('Congratulations, you are now a registered user!')
    return render_template('registration.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/success/<caseid>',methods=['GET', 'POST'])
@login_required
def success(caseid):
    casel = CaseLog(caseID=caseid,caseStatus='S01')
    db.session.add(casel)
    db.session.commit()
    user = current_user.get_id()
    user=User.query.filter_by(id=user).first()
    user.points = user.points + 1
    return render_template('caseid.html', caseid=caseid)

@app.route('/report',methods=['GET', 'POST'])
@login_required
def report():
    form = CaseForm()
    form.level.choices =[(building.buildingDesc, building.buildingDesc) for building in Building.query.filter_by(buildingID='B02').all()]
    user = current_user.get_id()
    if request.method == 'POST':
        filename = secure_filename(images.save(request.files['photo']))
        url = images.url(filename)
        case = Case(photoFilename=filename,photoURL=url, building=form.building.data,location=request.form['location'],level=request.form['level'],
                            roomNum=form.unit.data,typeOfFacility=request.form['facility'],severity=form.severity.data, comments=form.description.data,userID=user)
        db.session.add(case)
        db.session.commit()
        # db.session.refresh(case)
        createGroupedBar()
        createBar()
        backlogPie()
        buildingPie()
        case_id = str(case.caseID)
        return redirect(url_for('success', caseid=case_id))
    return render_template('report.html', title='Case Reporting', form=form)

@app.route('/facility/<location>')
def facility(location):
    location = Location.query.filter_by(locationID=location).first()
    facArray = []
    facobj = {}
    factag = location.facilitiesTag
    factag = factag.split('_')
    for i in factag:
        string = str(i)
        facility = Facility.query.filter_by(facilityID=string).first()
        facobj = {}
        facobj['id'] = str(facility.facilityID)
        facobj['facility'] = str(facility.facilityDesc)
        facArray.append(facobj)
    return jsonify({'facilitys':facArray})

@app.route('/floor/<building>')
def floor(building):
    building = Building.query.filter_by(buildingID=building).first()
    lvlArray = []
    lvlobj = {}
    minlvl = building.minLevel
    maxlvl = building.maxLevel
    if minlvl != None:
        if minlvl[0] == 'B':
            lvlobj = {}
            lvlobj['id'] = minlvl
            lvlobj['lvl'] = minlvl
            lvlArray.append(lvlobj)
            for x in range(1, (int(maxlvl[1])+1)):
                lvlobj = {}
                lvlobj['id'] = 'L'+str(x)
                lvlobj['lvl'] = 'L'+str(x)
                lvlArray.append(lvlobj)
        else:
            for x in range(int(minlvl[1]), (int(maxlvl[1])+1)):
                lvlobj = {}
                lvlobj['id'] = 'L'+str(x)
                lvlobj['lvl'] = 'L'+str(x)
                lvlArray.append(lvlobj)
    else:
        lvlobj = {}
        lvlobj['id'] = building.buildingDesc
        lvlobj['lvl'] = building.buildingDesc
        lvlArray.append(lvlobj)
    return jsonify({'levels':lvlArray})

@app.route('/location/<building>')
def location(building):
    building = Building.query.filter_by(buildingID=building).first()
    locArray = []
    locobj = {}
    loctag = building.locationTag
    loctag = loctag.split('_')
    print(loctag)
    for i in loctag:
        string = str(i)
        location = Location.query.filter_by(locationID=string).first()
        locobj = {}
        locobj['id'] = str(location.locationID)
        locobj['location'] = location.locationDesc
        locArray.append(locobj)
    return jsonify({'locations':locArray})


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    usertype = UserType.query.filter_by(userTypeID=user.userType).first()
    case = Case.query.filter_by(userID=user.id)
    return render_template('profile.html', user=user, usertype=usertype, case=case)

@app.route('/search',methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        caseid = request.form['search']
        case = Case.query.filter_by(caseID=caseid).first()
        if case is None:
            user = current_user.get_id()
            user = User.query.filter_by(id=user).first()
            return redirect(url_for('user', username=user.username)),flash('CaseID does not exist, please search again')
        else:
            return redirect(url_for('casedetail', caseid=caseid))


@app.route('/edit_case/<caseid>', methods=['GET', 'POST'])
@login_required
def edit_case(caseid):
    form = EditCaseForm()
    case = Case.query.filter_by(caseID=caseid).first()
    status = CaseStatus.query.filter_by(statusID=case.caseStatus).first()
    severity = Severity.query.filter_by(severityID=case.severity).first()
    building = Building.query.filter_by(buildingID=case.building).first()
    facility = Facility.query.filter_by(facilityID=case.typeOfFacility).first()
    location = Location.query.filter_by(locationID=case.location).first()
    if request.method == 'POST':
    # if form.validate_on_submit():
        case.severity = form.severity.data
        case.building = form.building.data
        case.location = form.location.data
        case.level = form.level.data
        case.roomNum = form.unit.data
        case.typeOfFacility = form.facility.data
        case.comments = form.description.data
        db.session.commit()
        casel = CaseLog(caseID=caseid,caseStatus=status.statusID)
        db.session.add(casel)
        db.session.commit()
        createGroupedBar()
        createBar()
        backlogPie()
        buildingPie()
        return redirect(url_for('casedetail',caseid=case.caseID)),flash('Your changes have been saved.')
    elif request.method == 'GET':
        form.severity.data = case.severity 
        form.building.data = case.building
        form.location.data = case.location
        form.level.data = case.level
        form.unit.data = case.roomNum
        form.facility.data = case.typeOfFacility
        form.description.data = case.comments
    return render_template('editcasedetails.html', title='Edit Profile',
                           form=form, case=case, status=status, severity=severity, building=building, facility=facility,
                           location=location)

@app.route('/edit_caseadmin/<caseid>', methods=['GET', 'POST'])
@login_required
def edit_caseadmin(caseid):
    form = EditAdminCaseForm()
    case = Case.query.filter_by(caseID=caseid).first()
    status = CaseStatus.query.filter_by(statusID=case.caseStatus).first()
    severity = Severity.query.filter_by(severityID=case.severity).first()
    building = Building.query.filter_by(buildingID=case.building).first()
    facility = Facility.query.filter_by(facilityID=case.typeOfFacility).first()
    location = Location.query.filter_by(locationID=case.location).first()
    if request.method == 'POST':
    # if form.validate_on_submit():
        case.caseStatus = form.status.data
        case.severity = form.severity.data
        case.building = form.building.data
        case.location = form.location.data
        case.level = form.level.data
        case.roomNum = form.unit.data
        case.typeOfFacility = form.facility.data
        case.comments = form.description.data
        case.adminComments = form.adminComments.data
        db.session.commit()
        casel = CaseLog(caseID=caseid,caseStatus=form.status.data)
        db.session.add(casel)
        db.session.commit()
        createGroupedBar()
        createBar()
        backlogPie()
        buildingPie()
        return redirect(url_for('casedetailadmin',caseid=case.caseID)),flash('Your changes have been saved.')
    elif request.method == 'GET':
        form.status.data = case.caseStatus 
        form.severity.data = case.severity 
        form.building.data = case.building
        form.location.data = case.location
        form.level.data = case.level
        form.unit.data = case.roomNum
        form.facility.data = case.typeOfFacility
        form.description.data = case.comments
        form.adminComments.data = case.adminComments
    return render_template('editcasedetailsadmin.html', title='Edit Profile',
                           form=form, case=case, status=status, severity=severity, building=building, facility=facility,
                           location=location)


@app.route('/viewdatabase',methods=['GET'])
def view():
    user = UserType.query.all()
    list = []
    for i in user:
        list.append(i.list())
    print(list)
    return jsonify(list)
    # user = UserType.query.with_entities(UserType.userTypeID)
    # print(user)
    # liset = ''
    # for i in user:
    #     liset += str(i)
    # return liset


@app.route('/cases')
def cases():
    case = Case.query.all()
    list = []
    for i in case:
        list.append(i.serialize())
    return jsonify(list)

@app.route('/status')
def status():
    return render_template('checkstatus.html', title='Check Status')

@app.route('/leaderboard')
@login_required 
def leaderboard():
    user = User.query.filter(User.username != 'guest').order_by(User.points.desc()).limit(10)
    tupplelist = []
    for i in user:
        name = i.username
        points = i.points
        users = (name,points)
        tupplelist.append(users)
    length = len(tupplelist)
    return render_template('leaderboard1.html', title='View Leaderboard', users=tupplelist, length=length)

@app.route('/explore')
def explore():
    return render_template('explore.html', title='Explore Page')

@app.route('/casedetail/<caseid>')
def casedetail(caseid):
    id = int(current_user.get_id())
    user=User.query.filter_by(id=id).first() 
    case = Case.query.filter_by(caseID=caseid).first()
    status = CaseStatus.query.filter_by(statusID=case.caseStatus).first()
    severity = Severity.query.filter_by(severityID=case.severity).first()
    building = Building.query.filter_by(buildingID=case.building).first()
    facility = Facility.query.filter_by(facilityID=case.typeOfFacility).first()
    location = Location.query.filter_by(locationID=case.location).first()
    return render_template('casedetail.html', title='Case Detail Page',case=case, status=status, severity=severity,
                                building=building, facility=facility, location=location,id=id,user=user)

@app.route('/casedetailadmin/<caseid>')
def casedetailadmin(caseid):
    id = int(current_user.get_id())
    user=User.query.filter_by(id=id).first() 
    case = Case.query.filter_by(caseID=caseid).first()
    status = CaseStatus.query.filter_by(statusID=case.caseStatus).first()
    severity = Severity.query.filter_by(severityID=case.severity).first()
    building = Building.query.filter_by(buildingID=case.building).first()
    facility = Facility.query.filter_by(facilityID=case.typeOfFacility).first()
    location = Location.query.filter_by(locationID=case.location).first()
    return render_template('casedetailadmin.html', title='Case Detail Page',case=case, status=status, severity=severity,
                                building=building, facility=facility, location=location,id=id,user=user)

@app.route('/caselist',methods=['GET','POST'],defaults={'page':1}) #
@app.route('/caselist/<int:page>',methods=['GET','POST'])
def caselist(page):
    merge = Case.query.join(CaseStatus,Building,Severity,Facility).with_entities(CaseStatus.statusDesc,Building.buildingDesc,Severity.severityDesc,\
        Facility.facilityDesc,Case.caseID,Case.comments,Case.dateTime,Case.building,\
        Case.typeOfFacility,Case.severity, Case.caseStatus, Case.photoURL)
    form = FilterForm()
    if form.validate_on_submit():
        b = form.building.data
        f = form.facility.data
        st = form.status.data
        se = form.severity.data
        filter_case = Case.query.filter_by(building=b).filter_by(typeOfFacility=f).filter_by(caseStatus=st).filter_by(severity=se)\
            .join(CaseStatus,Building,Severity,Facility).with_entities(CaseStatus.statusDesc,Building.buildingDesc,Severity.severityDesc,\
        Facility.facilityDesc,Case.caseID,Case.comments,Case.dateTime,Case.photoURL)
        pages = filter_case.paginate(error_out=False)
        return render_template('caselist.html',title='caselist',pages=pages,form=form)
    try: 
        print(pages)
    except:
        pages = merge.paginate(per_page=12, page=page,error_out=False)
    return render_template('caselist.html',title='caselist',pages=pages,form=form)

@app.route('/GetCaseDetails/', methods=['GET'])
def getCaseDetails():
    if 'caseID' in request.args:
        try:
            caseID = int(request.args.get('caseID'))
            case = Case.query.filter_by(caseID=caseID).all()
            return jsonify([c.serialize() for c in case])
        except AttributeError:
            return "Invalid ID, please try a different ID."

    if 'caseStatus' in request.args:
        try:
            caseStatus = request.args.get('caseStatus')
            case = Case.query.filter_by(caseStatus=caseStatus).all()
            return jsonify([c.serialize() for c in case])
        except AttributeError:
            return "Invalid case status, please try a different case status."

    if 'dateTime' in request.args:
        try:
            dateTime = request.args.get('dateTime')
            dateTime = datetime.strptime(dateTime, "%d-%m-%Y")
            maxDay = dateTime + timedelta(days=1)
            minDay = dateTime - timedelta(days=1)
            case = Case.query.filter(and_(
                                        Case.dateTime < maxDay,
                                        Case.dateTime > minDay
                                        )
                                    )
            return jsonify([c.serialize() for c in case])
        except AttributeError:
            return "Invalid dateTime, please try a different dateTime."

    if 'building' in request.args:
        try:
            building = request.args.get('building')
            case = Case.query.filter_by(building=building).all()
            return jsonify([c.serialize() for c in case])
        except AttributeError:
            return "Invalid building, please try a different building."

    if 'location' in request.args:
        try:
            location = request.args.get('location')
            case = Case.query.filter_by(location=location).all()
            return jsonify([c.serialize() for c in case])
        except AttributeError:
            return "Invalid location, please try a different location."

    if 'severity' in request.args:
        try:
            severity = request.args.get('severity')
            case = Case.query.filter_by(severity=severity).all()
            return jsonify([c.serialize() for c in case])
        except AttributeError:
            return "Invalid location, please try a different location."

    if 'fixedDate' in request.args:
        try:
            fixedDate = request.args.get('fixedDate')
            fixedDate = datetime.strptime(fixedDate, "%d-%m-%Y")
            maxDay = fixedDate + timedelta(days=1)
            minDay = fixedDate - timedelta(days=1)
            case = Case.query.filter(and_(
                                        Case.fixedDate < maxDay,
                                        Case.fixedDate > minDay
                                        )
                                    )
            return jsonify([c.serialize() for c in case])
        except AttributeError:
            return "Invalid dateTime, please try a different dateTime."
        
    else:
        case = Case.query.all()
        return jsonify([c.serialize() for c in case])



@app.route('/GetUserPoints/', methods=['GET'])
def getUserPoints():
    if 'username' in request.args:
        try:
            username = request.args.get('username')
            user = User.query.filter_by(username=username).all()
            return jsonify([u.serialize() for u in user])
        except AttributeError:
            return "Invalid username, please try a different username."

    if 'minPoints' in request.args and 'maxPoints' in request.args: 
        try:
            maxPoints = int(request.args.get('maxPoints'))
            
            minPoints = int(request.args.get('minPoints'))
            user = User.query.filter(and_(
                                        User.points <= maxPoints,
                                        User.points >= minPoints)
                                    )
            return jsonify([u.serialize() for u in user])
        except AttributeError:
            return "Invalid points entered, please input a number in parameter."

    if 'minPoints' in request.args:
        try:
            
            minPoints = int(request.args.get('minPoints'))
            user = User.query.filter(User.points >= minPoints)
            return jsonify([u.serialize() for u in user])
        except AttributeError:
            return "Invalid points entered, please input a number in parameter."

    if 'maxPoints' in request.args:
        try:
            maxPoints = int(request.args.get('maxPoints'))
            user = User.query.filter(User.points <= maxPoints)
            return jsonify([u.serialize() for u in user])
        except AttributeError:
            return "Invalid points entered, please input a number in parameter."
    
    if 'userType' in request.args:
        try:
            userType = request.args.get('userType')
            user = User.query.filter_by(userType=userType).all()
            return jsonify([u.serialize() for u in user])
        except AttributeError:
            return "Invalid userType, please try a different userType."
    else:
        user = User.query.all()
        return jsonify([u.serialize() for u in user])


@app.route('/PostCaseReporting', methods=["POST"])
def createCase():
    building = request.json['building']
    location = request.json['location']
    try:
        level = request.json['level']
    except:
        level = None
    try:
        roomNum = request.json['roomNum'] #what is emails?
    except:
        roomNum = None
    typeOfFacility = request.json['typeOfFacility']
    severity = request.json['severity']
    comments = request.json['comments']

    try:
        new_case = Case(building=building, location=location, level=level, roomNum=roomNum,  typeOfFacility=typeOfFacility, severity=severity, comments=comments, userID=4) #guest account has userID of 4 #creating student object w only name and team
        db.session.add(new_case)
        db.session.commit() #this must be done before adding address
        return ("Successfully Posted!")
    except Exception:
        return ("Posting error")

