from datetime import datetime, timedelta,date
from app.models import Case,CaseLog,CaseStatus,Building,User,UserType,Location
from sqlalchemy import and_, desc, cast, DATE,func,distinct,join, create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re
from app import db
engine = create_engine('postgresql://admin1:password@localhost:5432/fixsmoo', convert_unicode=True)
Session = sessionmaker(bind=engine)
session = Session()
# Plotly API keys============================================================================================
plotly.tools.set_credentials_file(username='xiaorongw', api_key='vOkqfPCsftGndLRzTDfx')

# =======================Start 3 status card update=====================================================================
caseStatusCount = {}
# case = Case.query.filter(cast(Case.dateTime, DATE) == date.today()).all()
case = Case.query.all()
OP=0
RC=0
FX=0

for i in case:
    eachCase = i.serialize()
    if eachCase['caseStatus'] == 'S01':
        OP += 1
    else:
        OP=OP
    if eachCase['caseStatus'] == "S02":
         RC += 1
    else:
        RC=RC
    if eachCase['caseStatus'] == "S03":
         FX += 1
    else:
         FX=FX

#==End of 3 Status Card update ====================================================================================

#===========Start Case Search Table=================================================================================

# searchtable = session.query(CaseLog,CaseStatus,Case,Building,Location,User).filter(CaseLog.caseID==Case.caseID).filter(CaseLog.caseStatus==CaseStatus.statusID).filter(Case.building==Building.buildingID).filter(Case.location==Location.locationID).filter(Case.userID==User.id).all()

# searchlist=[]
def caseLogRetrieve(searchtable):
    searchlist=[]
    for log,status,case,building,location,user in searchtable:
        searchdict={}   
        searchdict["CaseID"]=log.caseID
        searchdict["Building"]=building.buildingDesc
        searchdict["Location"]=location.locationDesc
        searchdict["Logged By"]=user.username
        searchdict["Reported Date"]=(case.dateTime).strftime("%d-%m-%y %H:%M")
        searchdict["Case Status"]=status.statusDesc
        searchdict["Last Update"]=(log.logDateTime).strftime("%d-%m-%y %H:%M")
        searchdict["Remarks"]=case.adminComments

        searchlist.append(searchdict)
    return searchlist

#===========End Case Search Table=================================================================================

#===========Start Duplicate Check=======================================================================================

def check_duplicate():
    open_cases = Case.query.filter_by(check=0).filter(Case.caseStatus.in_(['S01','S02','S03'])).all()
    all_cases= Case.query.filter(Case.caseStatus.in_(['S01','S02','S03'])).all()

    # print(open_cases)    
    # print(all_cases)
    #initial key case====================================================
    open_cases_dict = {}
    all_cases_dict = {}
    for i in all_cases:
        new_i = i.serializeadmin()
        all_cases_dict[new_i['caseID']] = {"roomNum":new_i['roomNum'],"building":new_i['building'],"level":new_i['level'],"typeOfFacility":new_i['typeOfFacility'],"location":new_i['location'],"caseStatus":new_i['caseStatus'], "check":new_i["check"]} # key value pair
    
    for i in open_cases:
        new_i = i.serializeadmin()
        open_cases_dict[new_i['caseID']] = {"roomNum":new_i['roomNum'],"building":new_i['building'],"level":new_i['level'],"typeOfFacility":new_i['typeOfFacility'],"location":new_i['location'],"caseStatus":new_i['caseStatus'], "check":new_i["check"]} # key value pair
    # print(all_cases_dict)
    # print(open_cases_dict)
    duplicate_dict = {}
    for k,v in open_cases_dict.items():
        compare_case = v
        temp_content=[]
        temp_id = []
        print(k)
        Current_content = compare_case['roomNum']
        if Current_content is not None:
            for key,value in all_cases_dict.items():
                if compare_case['building']==value['building'] and\
                    compare_case['level']==value['level']and\
                    compare_case['location']==value['location']and\
                    compare_case['typeOfFacility']==value['typeOfFacility']:
                    if value['roomNum'] is not None:
                        temp_content.append(value['roomNum'])
                        temp_id.append(key)
        # print("temp content",temp_content)
        # print("temp id",temp_id)
            if len(temp_content) > 0:
                print("duplicate_dict",duplicate_content(Current_content,temp_content,temp_id,k))
                duplicate_dict[k]= duplicate_content(Current_content,temp_content,temp_id,k)
        print("duplicate bigdict",duplicate_dict)
        checkid=Case.query.filter_by(caseID=k).first()
        checkid.check=1
        db.session.commit()
    return duplicate_dict
    # print("==================================================")
    
def duplicate_content(Current_content,text_content,temp_id,k):

    location_type = ['sr','cr','gsr','toliet','lift', 'escalator','common areas']
    id = temp_id
    number_content_duplicate = []
    number_temp_array = []
    location = []
    strip_number_temp_array = []

    for i in range(len(text_content)):
        number_temp_array.append(re.findall('\d+',text_content[i]))

    for i in number_temp_array:
        temp = []
        for j in i:
            temp.append(j.lstrip("0"))
        # print("temp_number",temp)
        strip_number_temp_array.append(temp)

    # print("strip number temp array",strip_number_temp_array)

    n1_id = []
    for i in range(len(strip_number_temp_array)):
        if fuzz.partial_ratio(strip_number_temp_array[0],strip_number_temp_array[i]) == 100:
            number_content_duplicate.append(text_content[i])
            n1_id.append(id[i])

    # print("number content duplicate",number_content_duplicate)
            
    #words to number  

    for i in number_content_duplicate:
        temp_location = ""
        for j in location_type:
            if j in i.lower():
                temp_location =j
        location.append(temp_location)
        # new_i = i.split(" ")
        # for j in new_i:
        #     if j.lower() in location_type:
        #         location.append(j)
    # print("location",location)

    potential_duplicate = {}
    
    for i in range(0,len(location)):
        if fuzz.ratio(location[0],location[i]) == 100:
            potential_duplicate[n1_id[i]] = number_content_duplicate[i]
    if k in potential_duplicate.keys():
        del potential_duplicate[k]
    print("potential:",potential_duplicate)

    return potential_duplicate

#===========End Duplicate Check========================================================================================

#===========Chart Creation/Update Functions===========================================================================

######################################### Grouped Bar: cases against day #########################################
def createGroupedBar():
	xdates = [] #will store today's date and past 4 dates; datetime format
	strdates = [] #will store today's date and past 4 dates; format: Mmm dd
	for i in range(0,5): 
		d = datetime.utcnow().date() - timedelta(days=i)
		dstring = datetime.strftime(d,'%b %d')
		xdates.append(d)
		strdates.append(dstring)
	xdates.reverse()
	strdates.reverse()

	minDate = xdates[0]

	# initialise a dictionary of dictionaries. Each date (key) in strdates will have a statusDict as value
	dateCasesDict = {}
	for i2 in strdates:
		dateCasesDict[i2] = {"open":0, "review":0, "fixing":0}

	for eachDate in xdates:
		dateString = datetime.strftime(eachDate,'%b %d')
		casesAdded = [] #stores caseID of cases that are already included into count
		caseLog = CaseLog.query.filter(and_(
											CaseLog.logDateTime < eachDate+timedelta(days=1),
											CaseLog.logDateTime > minDate-timedelta(days=1) #or >=minDate works too
										)).order_by(desc(CaseLog.logDateTime))
		for i3 in caseLog:
			eachLog = i3.serialize()
			if eachLog['caseID'] not in casesAdded:
				print(eachLog)
				if eachLog['caseStatus'] == "S01":
					dateCasesDict[dateString]['open'] += 1
				elif eachLog['caseStatus'] == "S02":
					dateCasesDict[dateString]['review'] += 1
				elif eachLog['caseStatus'] == "S03":
					dateCasesDict[dateString]['fixing'] += 1
				casesAdded.append(eachLog['caseID'])

	# prepare data for charting
	ytraceOpen = []
	ytraceReview = []
	ytraceFixing = []
	for eachDate in dateCasesDict:
		ytraceOpen.append(dateCasesDict[eachDate]["open"])
		ytraceReview.append(dateCasesDict[eachDate]["review"])
		ytraceFixing.append(dateCasesDict[eachDate]["fixing"])

	# charting
	trace1 = go.Bar(
		x=strdates,
		y=ytraceOpen,
		name='Open',
		marker=dict(
			color='rgb(203,152,183)')
	)
	trace2 = go.Bar(
		x=strdates,
		y=ytraceReview,
		name='Under Review',
		marker=dict(
			color='rgb(188,174,187)')
	)
	trace3 = go.Bar(
		x=strdates,
		y=ytraceFixing,
		name='Fix In-Progress',
		marker=dict(
			color='rgb(173,94,151)')
	)

	tracedata = [trace1, trace2, trace3]
	layout = go.Layout(
		barmode='group'
	)

	fig = go.Figure(data=tracedata, layout=layout)
	return py.plot(fig, filename='cases')

######################### Bar Chart: Average time taken (in days) between each status for that MONTH #########################

def createBar():
	timeDict = {"Pending Review": 0, "Reviewing": 0, "Fixing": 0}
	#Pending Review: time taken for admin to look into case logged -- "Open" to "Under Review"
	#Under Review: time taken for admin to investigate issue -- "Under Review" to " Fix in Progress"
	#Fix in Progress: time taken for contractor to fix issue -- "Fix in Progress" to "Fixed"

	monthDate = datetime.utcnow().date().replace(day=1) #gets first day of the month in date format
	print(monthDate)

	def checkValidCase(caseID): 
		if caseID == "S05" or caseID == "S06":
			skipCases.append(caseID)
		return

	skipCases = []
	logDict = {} #for each case, stores date updated for each status

	caseLog = session.query(CaseLog, CaseStatus).join(CaseStatus).all()
	for log, status in caseLog:
		caseID = log.caseID
		statusID = log.caseStatus
		statusDesc = status.statusDesc
		if caseID not in logDict:
			logDict[caseID] = {"Open": "NA",
								"Under Review": "NA",
								"Fix in Progress": "NA",
								"Fixed": "NA",
								"Invalid": "NA",
								"Duplicate": "NA",
								}
		logDict[caseID][statusDesc] = log.logDateTime

	underReviewCounter = 0
	reviewingCounter = 0
	fixingCounter = 0

	caseLog2 = session.query(CaseLog, CaseStatus).join(CaseStatus).filter(CaseLog.logDateTime >= monthDate).order_by(desc(CaseLog.logDateTime)).all()
	for log2, status2 in caseLog2:
		caseID = log2.caseID
		statusID = log2.caseStatus
		statusDesc = status2.statusDesc
		checkValidCase(caseID)
		if caseID not in skipCases:
			if statusID == "S04": #if = fixed
				fixingTime = (logDict[caseID]["Fixed"] - logDict[caseID]["Fix in Progress"]).days
				timeDict["Fixing"] += fixingTime
				fixingCounter += 1
			elif statusID == "S03": #if = fix in progress
				reviewingTime = (logDict[caseID]["Fix in Progress"] - logDict[caseID]["Under Review"]).days
				timeDict["Reviewing"] += reviewingTime
				reviewingCounter += 1
			elif statusID == "S02": #if = under review
				openTime = (logDict[caseID]["Under Review"] - logDict[caseID]["Open"]).days
				timeDict["Pending Review"] += openTime
				underReviewCounter += 1

	try:
		timeDict["Pending Review"] = int(round(timeDict["Pending Review"]/underReviewCounter, 0)) #gets average time
	except: #if counter=0, which means no cases under that status
		timeDict["Pending Review"] = 0

	try:
		timeDict["Reviewing"] = int(round(timeDict["Reviewing"]/reviewingCounter, 0))
	except:
		timeDict["Reviewing"] = 0

	try:
		timeDict["Fixing"] = int(round(timeDict["Fixing"]/fixingCounter, 0))
	except:
		timeDict["Fixing"] = 0

	print(timeDict)

	# preparing data for charting
	timeList = []
	for k,v in timeDict.items():
		timeList.append(v)

	# charting
	data = [go.Bar(
				x=timeList,
				y=['Pending Review', 'Reviewing', 'Fixing'],
				orientation = 'h',
				marker=dict(
					color='rgb(203,152,183)',
					line=dict(
						color='rgb(8,48,107)',
						width=0.5)
					),
				opacity = 0.6
				)]

	layout = go.Layout(
		xaxis=dict(
			title='number of days',
			titlefont=dict(
				family='Arial, monospace',
				size=13,
				color='#7f7f7f'
				),
			dtick=1
			)
		)

	fig = go.Figure(data=data, layout=layout)
	return py.plot(fig, filename='timetaken')


################# Pie Chart: Backlog (cases opened 1 week, 2 weeks, 3 weeks, >4 weeks ago that are still not fixed) #################

def backlogPie():
	backlog = {"1 week":0, "2 weeks":0, "3 weeks":0, ">4 weeks":0}
	currentDate = datetime.utcnow().date()
	caseLog3 = session.query(CaseLog).all()
	cases = session.query(Case).all()

	unfixedCases = []
	for case in cases:
		if case.caseStatus not in ["S04", "S05", "S06"]: #if not fixed
			unfixedCases.append(case.caseID)

	for log3 in caseLog3:
		if log3.caseID in unfixedCases:
			openDate = log3.logDateTime.date()
			timeDiff = (currentDate - openDate).days #timediff in days
			unfixedCases.remove(log3.caseID) #ensures only the first log for that particular unfixed caseID is retrieved -- since we only want to retrieve the date the case is opened
			if timeDiff <= 7:
				backlog["1 week"] += 1
			elif timeDiff <= 14:
				backlog["2 weeks"] += 1
			elif timeDiff <= 21:
				backlog["3 weeks"] += 1
			else:
				backlog[">4 weeks"] += 1

	print(backlog)
	# preparing data for charting
	backlogList = []
	for k1,v1 in backlog.items():
		backlogList.append(v1)
	print(backlogList)

	#charting
	labels = ['1 week','2 weeks','3 weeks','4 weeks & above']
	values = backlogList
	colors = ['#e8cfd5','#cdc6d6', '#aeaeca', '#8d9ac6']

	trace = go.Pie(labels=labels, values=values, marker=dict(colors=colors))
	return py.plot([trace], filename='backlog_pie')


################################################### Building Pie ###################################################

def buildingPie():
	monthDate = datetime.utcnow().date().replace(day=1) #gets first day of the month in date format
	cases2 = session.query(Case, Building).join(Building).filter(Case.dateTime >= monthDate).all()
	buildingReported = {'Admin Building': 0, 'Campus Green': 0, 'Concourse': 0, 'SIS': 0, 'SOA': 0, 'SOB': 0, 'SOE/SOSS': 0, 'SOL': 0, 'LKS Library': 0, 'SMU Labs' : 0}
	casesList = []
	for case2, building in cases2:
		if case2.caseID not in casesList:
			place = building.buildingDesc
			buildingReported[place] += 1
			casesList.append(case2.caseID)

	#preparing data for charting
	buildingList = []
	valueList = []
	for k2, v2 in buildingReported.items():
		buildingList.append(k2)
		valueList.append(v2)

	#charting
	labels = buildingList
	values = valueList
	# colors = ['#CB98B7','#BCAEBB', '#AD5E97', '#614C6B']

	trace = go.Pie(labels=labels, values=values)
	return py.plot([trace], filename='building_pie')

#===========End of Chart Creation/Update Functions===========================================================================






