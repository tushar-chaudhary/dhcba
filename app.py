from flask import Flask, request, jsonify, send_file,url_for, send_from_directory
from flask_caching import Cache
from flask_compress import Compress
import atexit
from apscheduler.scheduler import Scheduler
#from flask_script import Manager
#from flask_migrate import Migrate, MigrateCommand
from history import getHistory
from quick_form import qforms
from dictionary_word import getDictWord
from returndict import ret_dict
from all_ebooks import all_books
from ebooklinks import booklinks
from ebooksOnlylinks import bookslinkslist
from members_directory import get_member_directory_ByStartingWord, get_member_directory_ByID, get_member_directory_ByNameSuggestion, get_member_directory_ByNameSuggestionPagination, get_member_directory_ByEno
from DelhiPolice.index import getDelhiPolicestationBefore2015, getDelhiPolicestationAfter2015, getPoliceDistrictBefore2015, getPoliceDistrictAfter2015, delhiPoliceFirAfter2015, delhiPoliceFirBefore2015, getMvtheftdistrict, getMvtheftpolicestation, getMvtheftFir, Mvtheft, getPropertyFir, Propertytheft
from concurrent import futures
from send_mail import send_email
from library import read_library
from privacy_policy import get_priv_pol
from firebase import notify
from scrapers import Scrapers
from jsoncompare import compare


# from casehistory import *
# from werkzeug.contrib.cache import MemcachedCache
from termsandconditions import terms_conditions

import platform
import json
# from s3 import s3_upload,s3_delete
# from uuid import uuid4
# from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='')
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'mysql://DhuperInfotech:tushar1997@memberdirectory.ckmg7ngdlvgc.ap-south-1.rds.amazonaws.com/auth_dhcba'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

#Caching Starts here


cache = Cache()
cache.init_app(app, config={'CACHE_TYPE': 'filesystem','CACHE_DIR' : '/tmp'})

'''Failed Memcache experiment'''
# cache.init_app(app, config={'CACHE_TYPE': 'memcached','CACHE_MEMCACHED_SERVERS' : ['127.0.0.1:11211']})
'''Memcache experiment ends here'''

#Caching ends here

global scrp
scrp = Scrapers()


Compress(app)

from models import User, db, Compare_data, Notifications
#
# migrate = Migrate(app, db)
# manager = Manager(app)
#
# manager.add_command('db', MigrateCommand)

cron = Scheduler(daemon=True)
# Explicitly kick off the background thread
cron.start()
db.init_app(app)


@app.route("/")
def home():
    return jsonify({"version_code": 13, "maintainence_status": 0, "popup": [{ "image": "https://s3.ap-south-1.amazonaws.com/dhcba/WhatsApp+Image+2019-05-15+at+1.44.45+AM.jpeg", "title": "", "description": "", "status": 0  }]})


@app.route('/delhipolice/Mvtheftdistrict')
def DelhiPolice_Mvtheftdistrict():
    return jsonify(getMvtheftdistrict())

@app.route("/DisplayBoard")
def DisplayBoard():
    return jsonify(srp.DisplayBoard())

@app.route('/delhipolice/Mvtheftpolicestation')
def DelhiPolice_Mvtheftpolicestation():
    districtcode = request.args.get('districtcode')
    return jsonify(getMvtheftpolicestation(districtcode))

@app.route('/delhipolice/getMvtheft')
def DelhiPoliceFir_Mvtheft():
    district = request.args.get('district')
    policestation = request.args.get('policestation')
    caseyear = request.args.get('caseyear')
    firno = request.args.get('firno')
    return jsonify(Mvtheft(textfirno=firno, textfiryear=caseyear, textdistrict=district, textpolicestation=policestation))

@app.route('/delhipolice/getPropertyTheft')
def DelhiPoliceFir_PropertyTheft():
    district = request.args.get('district')
    policestation = request.args.get('policestation')
    caseyear = request.args.get('caseyear')
    firno = request.args.get('firno')
    return jsonify(Propertytheft(textfirno=firno, textfiryear=caseyear, textdistrict=district, textpolicestation=policestation))


@app.route('/delhipolice/getFir')
def DelhiPoliceFir_MvtheftFir():
    firno_name = request.args.get('firno_name')
    district = request.args.get('district')
    policestation = request.args.get('policestation')
    caseyear = request.args.get('caseyear')
    firno = request.args.get('firno')
    return jsonify(getMvtheftFir(FIRNO=firno_name, textfirno=firno, textfiryear=caseyear, textdistrict=district, textpolicestation=policestation))


@app.route('/delhipolice/getPropertyTheftFir')
def DelhiPoliceFir_PropertyTheftFir():
    firno_name = request.args.get('firno_name')
    district = request.args.get('district')
    policestation = request.args.get('policestation')
    caseyear = request.args.get('caseyear')
    firno = request.args.get('firno')
    return jsonify(getPropertyFir(FIRNO=firno_name, textfirno=firno, textfiryear=caseyear, textdistrict=district, textpolicestation=policestation))


@app.route('/login', methods=['POST'])
def login():
    userid = str(request.form.get('email'))
    password = request.form.get('password')
    device_id = str(request.form.get('device_id'))
    formdata = request.form
    users = [row.device_id for row in Notifications.query.filter_by(device_id=device_id)]
    data = {}
    if device_id in users:
        pass
    else:
        notification = Notifications(device_id=device_id,userid=userid)
        db.session.add(notification)
        db.session.commit()

    try:
        if userid.isdigit():
            q = User.query.filter_by(phone=userid, password=password).all()
        else:
            q = User.query.filter_by(email=userid, password=password).all()
        for i in q:
            data = {"status": "successful", "firstname": i.firstname, "lastname": i.lastname, "phone": i.phone, "enrollment": i.enrollment,
                    "dhcba_member": i.dhcba_member, "bar_no": i.bar_no, "verified": i.verified, "email": i.email}
        return jsonify(data)
    except Exception as e:
        print(e)
        return jsonify({"error": str(e),"formData": formdata})


@app.route('/signup', methods=['POST'])
def signup():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    verified = request.form.get('verified')
    enrollment = request.form.get('enrollment')
    dhcba_member = request.form.get('dhcba_member')
    bar_no = request.form.get('bar_no')
    device_id = str(request.form.get('device_id'))
    userByPhone = len(User.query.filter_by(phone=phone).all())
    userByEmail = len(User.query.filter_by(email=email).all())


    try:
        if(userByPhone > 0):
            data = {"status": "unsuccessfull", "error": "Phone number already exists"}
            return jsonify(data)
        elif (userByEmail > 0):
            data = {"status": "unsuccessfull", "error": "Email already exists"}
            return jsonify(data)
        else:
            record = User(firstname=firstname, lastname=lastname, email=email, phone=phone, password=password,
                          enrollment=enrollment, dhcba_member=dhcba_member, bar_no=bar_no, verified=verified,device_id=device_id)
            db.session.add(record)
            db.session.commit()
            data = {"status": "successfull"}
            return jsonify(data)
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})



@app.route('/delhipolice/getdistrictcode_before2015')
def DelhiPolice_DistrictcodeBefore2015():
    return jsonify(getPoliceDistrictBefore2015())


@app.route('/delhipolice/getpolicestationcode_before2015')
def DelhiPoliceStationcodeBefore2015():
    districtcode = request.args.get('districtcode')
    return jsonify(getDelhiPolicestationBefore2015(districtcode))


@app.route('/delhipolice/getpolicefir_before2015')
def DelhiPoliceFircodeBefore2015():
    district = request.args.get('district')
    policestation = request.args.get('policestation')
    caseyear = request.args.get('caseyear')
    firno = request.args.get('firno')
    return jsonify(delhiPoliceFirBefore2015(district,policestation,caseyear,firno))



@app.route('/delhipolice/getdistrictcode_after2015')
def DelhiPolice_DistrictcodeAfter2015():
    return jsonify(getPoliceDistrictAfter2015())


@app.route('/delhipolice/getpolicestationcode_after2015')
def DelhiPoliceStationcodeAfter2015():
    districtcode = request.args.get('districtcode')
    return jsonify(getDelhiPolicestationAfter2015(districtcode))


@app.route('/delhipolice/getpolicefir_after2015')
def DelhiPoliceFircodeAfter2015():
    district = request.args.get('district')
    policestation = request.args.get('policestation')
    caseyear = request.args.get('caseyear')
    firno = request.args.get('firno')
    return jsonify(delhiPoliceFirAfter2015(district,policestation,caseyear,firno))


@app.route('/homescreenimages')
def HomescreenImages():
    images = ['https://dhcba.s3.ap-south-1.amazonaws.com/WhatsApp+Image+2019-07-18+at+3.41.33+PM.jpeg','https://dhcba.s3.ap-south-1.amazonaws.com/Homescreen+Images/Delhi-High-Court2.jpg','https://dhcba.s3.ap-south-1.amazonaws.com/Homescreen+Images/Webp.net-resizeimage+(1).jpg','https://dhcba.s3.ap-south-1.amazonaws.com/Homescreen+Images/Webp.net-resizeimage.jpg', 'https://dhcba.s3.ap-south-1.amazonaws.com/Homescreen+Images/Webp.net-resizeimage+(2).jpg','https://dhcba.s3.ap-south-1.amazonaws.com/Homescreen+Images/featured-Image2-1366x768.jpg']
    return jsonify(images)


@app.route('/executiveCommittee')
def getExecutiveCommittee():
    executive_eno = [{'info': 'President', 'eno':'D/513/1991', 'name': 'Mohit Mathur Chand, Sr. Adv.'}, {'info': 'Hony. Secretary','eno':'D/1065/1995', 'name': 'Abhijat' },{'info': 'Vice President','eno' :'D/238/1988', 'name': 'Jatan Singh'},{'info': 'Joint Secretary', 'eno':'D/2398/1999', 'name': 'Amit Saxena'},{'info': 'Treasurer','eno':'D/671/1998 (R)', 'name': 'Mohit Gupta' },{'info':'Designated Senior Member Executive','eno':'D/86/1975', 'name': 'Ramesh Gupta, Sr. Adv.'},{'info':'Designated Senior Member Executive','eno':'D/319/1986', 'name': 'Sudhanshu Batra, Sr. Adv.'},{'info': '25 year standing standing member executive','eno':'D/271/1983', 'name': 'Baljit Dhir Singh'},{'info': '25 year standing standing member executive','eno':'D/1/1989', 'name': 'Kajal Chandra'},{'info': 'Lady member executive','eno':'D/858/2011', 'name': 'Rupali Kapoor'}, {'info':'Member executive','eno': 'D/983/2009', 'name': 'Kanika Singh'},{'info': 'Member executive','eno':'D/1625/2009', 'name': 'Nagender Bir Singh Benipal'},{'info':'Member executive','eno':'D/855/2010', 'name': 'Nikhil Mehta'},{'info': 'Member executive', 'eno': 'D/1087/2011', 'name': 'Harshit Jain'},{'info':'Member executive','eno':'D/972/2005', 'name': 'Dhan Mohan'}]
    executive_committee = []
    for eno in executive_eno:
        with futures.ThreadPoolExecutor(max_workers=5) as ex:
            member_data = ex.submit(get_member_directory_ByEno, eno['eno']).result()
            member_data['data']['info'] = eno['info']
            member_data['data']['image'] = 'https://dhcba.s3.ap-south-1.amazonaws.com/' + eno['eno'].replace(' ', '').replace('/','x').lower() + '.jpg'
            member_data['data']['Name'] = eno['name']
            member_data['data']['status'] = 'successfull'
            executive_committee.append(
                member_data['data']
        )


    return jsonify({'banner': 'https://dhcba.s3.ap-south-1.amazonaws.com/WhatsApp+Image+2019-07-18+at+3.41.33+PM.jpeg', 'details': executive_committee})



@app.route("/forgot_password", methods=['POST'])
def forgot_password():
    email = request.form.get('email')
    try:
        q = User.query.filter_by(email=email).all()
        for i in q:
            password = i.password
        # print password
        data = send_email(str(email), "Forgot Password DHCBA",
                          "Your password for " + str(email) + " is '" + password + "'.")
        return jsonify(data)
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})


@app.route("/<cnum>/<ctype>/<cyear>")  # helper.py casestatus
def index(cnum, ctype, cyear):
    try:
        return scrp.get_data(cnum, ctype, cyear)
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})

@app.route("/caseHistory_casewise/<casetype>/<caseyear>/<caseno>")  
def getCaseHistory_casewise(casetype, caseyear, caseno):
    try:
        return scrp.getCaseHistory_casewise(casetype, caseyear, caseno)
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})   
    
@app.route("/caseStatus_petvsres/<name>/<year>/<page>") 
def getCaseStatus_petvsres(name, year, page):
    try:
        return scrp.getCaseStatus_petvsres(name, year, page)
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"}) 
    
@app.route("/caseJudgment_petvsres") 
def getJudgmnet_petvsres():
    try:
        return scrp.getJudgmnet_petvsres(request.args.get('typeselected'), request.args.get('p_name'), request.args.get('frdate'), request.args.get('todate'))
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})   
    
@app.route("/certifiedCopies_appliedBy") 
def getCertifiedAppliedby():
    try:        
        return scrp.getCertifiedCopiesAppliedby(request.args.get('appliedby'), request.args.get('frdate'), request.args.get('todate'), request.args.get('side'), request.args.get('diaryno') if request.args.get('diaryno') != 'NULL' else '', request.args.get('diaryyear'), request.args.get('casetype'), request.args.get('caseno') if request.args.get('caseno') != 'NULL' else '', request.args.get('caseyear'))
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})    
    
@app.route("/caseHistory_petvsres/<partyname>/<match>/<petvsres>/<fryear>/<toyear>") 
def getCaseHistory_petVSres(partyname, match, petvsres, fryear, toyear):
    try:
        return scrp.getCaseHistory_petVSres(partyname, match, petvsres, fryear, toyear)
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})    
    
@app.route("/caseHistory_advocatename/<advocatename>/<match>/<fryear>/<toyear>") 
def getCaseHistory_advocatename(advocatename, match, fryear, toyear):
    try:
        return scrp.getCaseHistory_advocatename(advocatename, match, fryear, toyear)
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})  
    
@app.route("/caseStatus_dairyno") 
def getCaseStatus_dairyno():
    try:
        return scrp.getCaseStatus_dairyno(request.args.get('diaryname'), request.args.get('diaryyear'), request.args.get('page'))
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"}) 
    
@app.route("/caseStatus_advocate/<advocatename>/<advocateyear>/<page>") 
def CaseStatus_Advocate(advocatename, advocateyear, page):
    try:
        return scrp.CaseStatus_Advocate(advocatename, advocateyear, page)
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})     

@app.route("/caseJudgment_judge") 
def getJudgmnet_judge():
    try:
        return scrp.getJudgmnet_judge(request.args.get('judgename'), request.args.get('fryear'), request.args.get('toyear'))
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})     
    

@app.route("/caseJudgment_judgementdate") 
def getJudgement_judgementdate():
    try:
        return scrp.getJudgement_judgementdate(request.args.get('judgementdate'))
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})   
    
@app.route("/caseHistory_firno/<policestation>/<number>/<year>") 
def getCaseHistory_firno(policestation, number, year):
    try:
        return scrp.getCaseHistory_firno(policestation, number, year)
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})

@app.route("/case_types")
@cache.cached(timeout=60000)
def case_types():
    list_of_cases = ["ALL", "ARB. A. (COMM.) - [ARB]", "ARB.A. - [AAP]", "ARB.P. - [AA]", "AW - [AW]",
                     "BAIL APPLN. - [BAILA]", "C.O. - [XOBJ]", "C.O. - [CO]", "C.R.P. - [CR]", "C.REF.(O) - [CRO]",
                     "C.RULE - [CRULE]", "CA - [CAV]", "CA - [CAA]", "CA - [CAA]", "CAVEAT(CO.) - [CAVE]", "CC - [CC]",
                     "CC(ARB.) - [CCR]", "CCP(CO.) - [CCPCO]", "CCP(O) - [CCPO]", "CCP(REF) - [CCPRF]", "CEAC - [CEAC]",
                     "CEAR - [CEAR]", "CF - [CF]", "CHAT.A.C. - [CHAC]", "CHAT.A.REF - [CHAR]", "CM APPL. - [CM2]",
                     "CM APPL. - [CM1]", "CM(M) - [CMM]", "CMI - [CMI]", "CMI - [CMI]", "CO.A(SB) - [COASB]",
                     "CO.A(SB) - [CO.A]", "CO.APP. - [COA]", "CO.APPL. - [CA]", "CO.APPL.(C) - [CA(C)]",
                     "CO.APPL.(M) - [CA(M)]", "CO.EX. - [CO.EX]", "CO.PET. - [CP]", "CONT.APP.(C) - [CCA]",
                     "CONT.CAS(C) - [CCP]", "CONT.CAS.(CRL) - [CRLCP]", "CRL.A. - [CRLA]", "CRL.C.REF. - [CRLCR]",
                     "CRL.L.P. - [CRLMP]", "CRL.L.P. - [CRLMA]", "CRL.M.(BAIL) - [CRLMB]", "CRL.M.(CO.) - [CRLMC]",
                     "CRL.M.A. - [CRLM]", "CRL.M.C. - [CRLMM]", "CRL.M.I. - [CRLMI]", "CRL.O. - [CRLO]",
                     "CRL.O.(CO.) - [CRLOC]", "CRL.REF. - [CRLRF]", "CRL.REV.P. - [CRLR]", "CS(COMM) - [SC]",
                     "CS(OS) - [S]", "CS(OS) GP - [SG]", "CUS.A.C. - [CUSAC]", "CUS.A.R. - [CUSAR]", "CUSAA - [CUSAA]",
                     "CUSTOM A. - [CUSA]", "DEATH SENTENCE REF. - [MREF]", "DEATH SENTENCE REF. - [DSRF]",
                     "EDA - [EDA]", "EDC - [EDC]", "EDR - [EDR]", "EFA(OS) - [EFAOS]", "EL.PET. - [EP]", "ETR - [ETR]",
                     "EX.APPL.(OS) - [EA]", "EX.F.A. - [EFA]", "EX.P. - [EX]", "EX.S.A. - [ESA]", "FAO - [FAO]",
                     "FAO(OS) - [FAOOS]", "FAO(OS) (COMM) - [FAC]", "GCAC - [GCAC]", "GCAR - [GCAR]", "GTA - [GTA]",
                     "GTC - [GTC]", "GTR - [GTR]", "I.A. - [IA]", "I.P.A. - [IPA]", "ITA - [ITA]", "ITC - [ITC]",
                     "ITR - [ITR]", "ITSA - [ITSA]", "LA.APP. - [LAA]", "LPA - [LPA]", "MAC.APP. - [MACA]",
                     "MAT. - [MAT]", "MAT.APP. - [MATA]", "MAT.APP.(F.C.) - [MATFC]", "MAT.CASE - [MATC]",
                     "MAT.REF. - [MATR]", "NA - [NA]", "O.A. - [OAA]", "O.A. - [OA]", "O.M.P. - [OMP]",
                     "O.M.P. (COMM) - [OMC]", "O.M.P. (E) (COMM.) - [OME]", "O.M.P. (J) (COMM.) - [OMJ]",
                     "O.M.P. (MISC.) - [OMM]", "O.M.P. (T) (COMM.) - [OMT]", "O.M.P.(E) - [OE]",
                     "O.M.P.(EFA)(COMM.) - [OMA]", "O.M.P.(I) - [OI]", "O.M.P.(I) (COMM.) - [OMI]",
                     "O.M.P.(MISC.)(COMM.) - [OMMC]", "O.M.P.(T) - [OMPT]", "O.REF. - [OREF]", "O.REF. - [CRF]",
                     "OBJ. IN SUIT - [OBJ]", "OCJA - [OCJA]", "OD - [OD]", "OLR - [OLR]", "OMP (ENF.) (COMM.) - [OMF]",
                     "R.A. - [RA]", "RC.REV. - [RCR]", "RC.S.A. - [SAO]", "RC.S.A. - [RCSA]", "REVIEW PET. - [RP]",
                     "RFA - [RFA]", "RFA(OS) - [RFAOS]", "RFA(OS)(COMM) - [RFC]", "RSA - [RSA]", "SCA - [SCA]",
                     "SDR - [SDR]", "SERTA - [SERTA]", "ST.APPL. - [STA]", "ST.APPL. - [STC]", "ST.REF. - [STR]",
                     "STC - [STC]", "SUR.T.REF. - [SRTR]", "TEST.CAS. - [PR]", "TR.P.(C) - [TRP]", "TR.P.(C.) - [TPC]",
                     "TR.P.(CRL.) - [TPCRL]", "VAT APPEAL - [VATA]", "W.P.(C) - [CW]", "W.P.(CRL) - [CRLW]",
                     "WTA - [WTA]", "WTC - [WTC]", "WTR - [WTR]"]
    return json.dumps(list_of_cases)


@app.route("/case_years")
@cache.cached(timeout=60000)
def case_years():
    list_of_years = [{"year": "2019", "value": "2019"}, {"year": "2018", "value": "2018"}, {"year": "2017", "value": "2017"}, {"year": "2016", "value": "2016"}, {"year": "2015", "value": "2015"}, {"year": "2014", "value": "2014"}, {"year": "2013", "value": "2013"}, {"year": "2012", "value": "2012"}, {"year": "2011", "value": "2011"}, {"year": "2010", "value": "2010"}, {"year": "2009", "value": "2009"}, {"year": "2008", "value": "2008"}, {"year": "2007", "value": "2007"}, {"year": "2006", "value": "2006"}, {"year": "2005", "value": "2005"}, {"year": "2004", "value": "2004"}, {"year": "2003", "value": "2003"}, {"year": "2002", "value": "2002"}, {"year": "2001", "value": "2001"}, {"year": "2000", "value": "2000"}, {"year": "1999", "value": "1999"}, {"year": "1998", "value": "1998"}, {"year": "1997", "value": "1997"}, {"year": "1996", "value": "1996"}, {"year": "1995", "value": "1995"}, {"year": "1994", "value": "1994"}, {"year": "1993", "value": "1993"}, {"year": "1992", "value": "1992"}, {"year": "1991", "value": "1991"}, {"year": "1990", "value": "1990"}, {"year": "1989", "value": "1989"}, {"year": "1988", "value": "1988"}, {"year": "1987", "value": "1987"}, {"year": "1986", "value": "1986"}, {"year": "1985", "value": "1985"}, {"year": "1984", "value": "1984"}, {"year": "1983", "value": "1983"}, {"year": "1982", "value": "1982"}, {"year": "1981", "value": "1981"}, {"year": "1980", "value": "1980"}, {"year": "1979", "value": "1979"}, {"year": "1978", "value": "1978"}, {"year": "1977", "value": "1977"}, {"year": "1976", "value": "1976"}, {"year": "1975", "value": "1975"}, {"year": "1974", "value": "1974"}, {"year": "1973", "value": "1973"}, {"year": "1972", "value": "1972"}, {"year": "1971", "value": "1971"}, {"year": "1970", "value": "1970"}, {"year": "1969", "value": "1969"}, {"year": "1968", "value": "1968"}, {"year": "1967", "value": "1967"}, {"year": "1966", "value": "1966"}, {"year": "1965", "value": "1965"}, {"year": "1964", "value": "1964"}, {"year": "1963", "value": "1963"}, {"year": "1962", "value": "1962"}, {"year": "1961", "value": "1961"}, {"year": "1960", "value": "1960"}, {"year": "1959", "value": "1959"}, {"year": "1958", "value": "1958"}, {"year": "1957", "value": "1957"}, {"year": "1956", "value": "1956"}, {"year": "1955", "value": "1955"}, {"year": "1954", "value": "1954"}, {"year": "1953", "value": "1953"}, {"year": "1952", "value": "1952"}, {"year": "1951", "value": "1951"}, {"year": "1950", "value": "1950"}, {"year": "All Years", "value": "0"}]
    return json.dumps(list_of_years)

@app.route("/case_history_match")
@cache.cached(timeout=60000)
def case_history_match():
    list_of_match = [{"value": "E", "match": "Exact"}, {"value": "S", "match": "Part of Name"}, {"value": "I", "match": "Starting With"}]
    return json.dumps(list_of_match)

@app.route("/case_history_policestation")
@cache.cached(timeout=60000)
def case_history_plstation():
    list_of_stations = [{"value": "All", "policeStation": "Select All"}, {"value": "1", "policeStation": "ADARSH NAGAR"}, {"value": "2", "policeStation": "ALIPUR"}, {"value": "3", "policeStation": "AMBEDKAR NAGAR"}, {"value": "4", "policeStation": "ANAND PARBAT"}, {"value": "5", "policeStation": "ANAND VIHAR"}, {"value": "6", "policeStation": "ASHOK VIHAR"}, {"value": "7", "policeStation": "BADARPUR"}, {"value": "8", "policeStation": "BARA HINDU RAO"}, {"value": "9", "policeStation": "BHAJAN PURA"}, {"value": "10", "policeStation": "CHANDNI MAHAL"}, {"value": "11", "policeStation": "CHANKYA PURI"}, {"value": "12", "policeStation": "CHITTRANJAN PARK"}, {"value": "13", "policeStation": "CIVIL LINES"}, {"value": "14", "policeStation": "CONNAUGHT PLACE"}, {"value": "15", "policeStation": "DABRI"}, {"value": "16", "policeStation": "DARYA GANJ"}, {"value": "17", "policeStation": "DEFENCE COLONY"}, {"value": "18", "policeStation": "DELHI CANTT."}, {"value": "19", "policeStation": "DESHBANDHU GUPTA ROAD"}, {"value": "20", "policeStation": "DILSHAD GARDEN"}, {"value": "21", "policeStation": "DWARKA"}, {"value": "22", "policeStation": "FARASH BAZAR"}, {"value": "23", "policeStation": "GANDHI NAGAR"}, {"value": "24", "policeStation": "GEETA COLONY"}, {"value": "25", "policeStation": "GOKULPURI"}, {"value": "26", "policeStation": "GREATER KAILASH"}, {"value": "27", "policeStation": "HARI NAGAR"}, {"value": "28", "policeStation": "HAUZ KHAS"}, {"value": "29", "policeStation": "HAUZ QAZI"}, {"value": "30", "policeStation": "HAZARAT NIZAMMUDDIN"}, {"value": "31", "policeStation": "HAZARAT NIZAMMUDDIN RLY. STATION."}, {"value": "32", "policeStation": "I.P.ESTATE"}, {"value": "33", "policeStation": "INDERPURI"}, {"value": "34", "policeStation": "JAFFARPUR"}, {"value": "35", "policeStation": "JAFFARPUR KALAN"}, {"value": "36", "policeStation": "JAHANGIR PURI"}, {"value": "37", "policeStation": "JAMA MASJID"}, {"value": "38", "policeStation": "JANAKPURI"}, {"value": "39", "policeStation": "KALKAJI"}, {"value": "40", "policeStation": "KALYAN PURI"}, {"value": "41", "policeStation": "KAMLA MARKET"}, {"value": "42", "policeStation": "KANJHAWALA"}, {"value": "43", "policeStation": "KAPASHERA"}, {"value": "44", "policeStation": "KAROL BAGH"}, {"value": "45", "policeStation": "KASHMERE GATE"}, {"value": "46", "policeStation": "KESHAV PURAM"}, {"value": "47", "policeStation": "KHAJOORI KHAS"}, {"value": "48", "policeStation": "KIRTI NAGAR"}, {"value": "49", "policeStation": "KOTLA MUBARAKPUR"}, {"value": "50", "policeStation": "KOTWALI"}, {"value": "51", "policeStation": "KRISHNA NAGAR"}, {"value": "52", "policeStation": "LAHORI GATE"}, {"value": "53", "policeStation": "LAJPAT NAGAR"}, {"value": "54", "policeStation": "LODHI COLONY"}, {"value": "55", "policeStation": "MAHIPALPUR"}, {"value": "56", "policeStation": "MALVIYA NAGAR"}, {"value": "57", "policeStation": "MANDAWALI"}, {"value": "58", "policeStation": "MANDIR MARG"}, {"value": "59", "policeStation": "MANGOLPURI"}, {"value": "60", "policeStation": "MANSAROVER PARK"}, {"value": "61", "policeStation": "MAURIS NAGAR"}, {"value": "62", "policeStation": "MAYAPURI"}, {"value": "63", "policeStation": "MAYUR VIHAR"}, {"value": "64", "policeStation": "MEHRAULI"}, {"value": "65", "policeStation": "MODEL TOWN"}, {"value": "66", "policeStation": "MOTI NAGAR"}, {"value": "67", "policeStation": "MUKHERJEE NAGAR"}, {"value": "68", "policeStation": "NABI KARIM"}, {"value": "69", "policeStation": "NAJAFGARH"}, {"value": "70", "policeStation": "NAND NAGRI"}, {"value": "71", "policeStation": "NANGLOI"}, {"value": "72", "policeStation": "NARAINA"}, {"value": "73", "policeStation": "NARELA"}, {"value": "74", "policeStation": "NARELA INDUSTRIAL AREA"}, {"value": "75", "policeStation": "NEW ASHOK NAGAR"}, {"value": "76", "policeStation": "NEW DELHI"}, {"value": "77", "policeStation": "NEW FRIENDS COLONY"}, {"value": "78", "policeStation": "OKHLA INDUSTRIAL AREA"}, {"value": "79", "policeStation": "OLD DELHI RAILWAY STATION"}, {"value": "80", "policeStation": "PAHARGANJ"}, {"value": "81", "policeStation": "PALAM AIRPORT"}, {"value": "82", "policeStation": "PARLIAMENT STREET"}, {"value": "83", "policeStation": "PASCHIM VIHAR"}, {"value": "84", "policeStation": "PATEL NAGAR"}, {"value": "85", "policeStation": "PRASAD NAGAR"}, {"value": "86", "policeStation": "PRASHANT VIHAR"}, {"value": "87", "policeStation": "PRATAP NAGAR"}, {"value": "88", "policeStation": "PREET VIHAR"}, {"value": "89", "policeStation": "PUNJABI BAGH"}, {"value": "90", "policeStation": "R.K.PURAM"}, {"value": "91", "policeStation": "RAJINDER NAGAR"}, {"value": "92", "policeStation": "RAJOURI GARDEN"}, {"value": "93", "policeStation": "ROHINI"}, {"value": "94", "policeStation": "ROHINI-I"}, {"value": "95", "policeStation": "ROOP NAGAR"}, {"value": "96", "policeStation": "S.P. BADLI"}, {"value": "97", "policeStation": "SADAR BAZAR"}, {"value": "98", "policeStation": "SANGAM VIHAR"}, {"value": "99", "policeStation": "SARAI ROHILLA"}, {"value": "100", "policeStation": "SARAI ROHILLA RLY. STATION"}, {"value": "101", "policeStation": "SARASWATI VIHAR"}, {"value": "102", "policeStation": "SARITA VIHAR"}, {"value": "103", "policeStation": "SEELAMPUR"}, {"value": "104", "policeStation": "SEEMA PURI"}, {"value": "105", "policeStation": "SHAHDARA"}, {"value": "106", "policeStation": "SHAKARPUR"}, {"value": "107", "policeStation": "SHALIMAR BAGH"}, {"value": "108", "policeStation": "SRINIWAS PURI"}, {"value": "109", "policeStation": "SUBZI MANDI"}, {"value": "110", "policeStation": "SULTAN PURI"}, {"value": "111", "policeStation": "TILAK MARG"}, {"value": "112", "policeStation": "TILAK NAGAR"}, {"value": "113", "policeStation": "TIMAR PUR"}, {"value": "114", "policeStation": "TOWN HALL"}, {"value": "115", "policeStation": "TRILOK PURI"}, {"value": "116", "policeStation": "TUGLAQ ROAD"}, {"value": "117", "policeStation": "UTTAM NAGAR"}, {"value": "118", "policeStation": "VASANT KUNJ"}, {"value": "119", "policeStation": "VASANT VIHAR"}, {"value": "120", "policeStation": "VIKAS PURI"}, {"value": "121", "policeStation": "SAROJINI NAGAR"}, {"value": "122", "policeStation": "VIVEK VIHAR"}, {"value": "123", "policeStation": "WELCOME COLONY"}, {"value": "124", "policeStation": "ZAFFAR PUR"}, {"value": "125", "policeStation": "USMANPUR"}, {"value": "126", "policeStation": "I.G.I.AIRPORT"}, {"value": "127", "policeStation": "CHANDNI CHOWK"}, {"value": "128", "policeStation": "BAWANA"}, {"value": "129", "policeStation": "R.M.D."}, {"value": "130", "policeStation": "NEW DELHI RAILWAY STATION"}, {"value": "131", "policeStation": "CBI"}, {"value": "132", "policeStation": "SPECIAL BRANCH LODHI ROAD"}, {"value": "133", "policeStation": "NARCOTIC CELL, KAMLA MARKET"}, {"value": "134", "policeStation": "ANTI-CORRUPTION BRANCH"}, {"value": "135", "policeStation": "PANDAV NAGAR"}, {"value": "136", "policeStation": "AMAN VIHAR"}, {"value": "137", "policeStation": "AMAR COLONY"}, {"value": "138", "policeStation": "BINDAPUR"}, {"value": "139", "policeStation": "SWAROOP NAGAR"}, {"value": "140", "policeStation": "KARAWAL NAGAR"}, {"value": "141", "policeStation": "SHASTRI PARK"}, {"value": "142", "policeStation": "JAMIA NAGAR"}, {"value": "143", "policeStation": "NANAK PURA"}, {"value": "144", "policeStation": "ECONOMIC OFFENCE WING"}, {"value": "145", "policeStation": "BURARI"}, {"value": "146", "policeStation": "JAIT PUR"}, {"value": "147", "policeStation": "RITHALA METRO"}, {"value": "148", "policeStation": "MAURYA ENCLAVE"}, {"value": "149", "policeStation": "VIJAY VIHAR"}, {"value": "150", "policeStation": "CHHAWLA"}, {"value": "151", "policeStation": "NIHAL VIHAR"}, {"value": "152", "policeStation": "NEB SARAI"}, {"value": "153", "policeStation": "SAKET"}, {"value": "154", "policeStation": "KHYALA"}, {"value": "155", "policeStation": "GOVIND PURI"}, {"value": "156", "policeStation": "BARAKHAMBA ROAD"}, {"value": "157", "policeStation": "CRIME AND RAILWAY"}, {"value": "158", "policeStation": "S.B.DAIRY"}, {"value": "159", "policeStation": "HARSH VIHAR"}, {"value": "160", "policeStation": "N.C.B. R.K.PURAM"}, {"value": "161", "policeStation": "CRIME WOMEN CELL"}, {"value": "162", "policeStation": "RAJAGARDEN METRO STATION"}, {"value": "163", "policeStation": "BEGAM PUR"}, {"value": "164", "policeStation": "BHARAT NAGAR"}, {"value": "165", "policeStation": "SUNLIGHT COLONY"}, {"value": "166", "policeStation": "BHALSWA DAIRY"}, {"value": "167", "policeStation": "JAFFARABAD"}, {"value": "168", "policeStation": "PUL PRAHLADPUR"}, {"value": "169", "policeStation": "MAHINDRA PARK"}, {"value": "170", "policeStation": "JAGAT PURI"}, {"value": "171", "policeStation": "MIYAWALI"}, {"value": "172", "policeStation": "SAFDARJUNG ELCLAVE"}, {"value": "173", "policeStation": "FATEHPUR BERI"}, {"value": "174", "policeStation": "MADHU VIHAR"}, {"value": "175", "policeStation": "RANHOLA"}, {"value": "176", "policeStation": "JYOTI NAGAR"}, {"value": "177", "policeStation": "RANI BAGH"}, {"value": "178", "policeStation": "SONIA VIHAR"}, {"value": "179", "policeStation": "RANJEET NAGAR"}, {"value": "180", "policeStation": "DOMESTIC AIRPORT"}, {"value": "181", "policeStation": "K.N.KATJU MARG"}, {"value": "182", "policeStation": "VASANT KUNJ SOUTH"}, {"value": "183", "policeStation": "DHAULA KUAN"}, {"value": "184", "policeStation": "FARIDABAD CENTRAL"}, {"value": "185", "policeStation": "J.P.NAGAR BARODA"}, {"value": "186", "policeStation": "G.T.B. ENCLAVE"}, {"value": "187", "policeStation": "CHEENAI"}, {"value": "188", "policeStation": "SHAKURBASTI"}, {"value": "189", "policeStation": "GAZI PUR"}, {"value": "190", "policeStation": "SAGAR PUR"}, {"value": "191", "policeStation": "LUNAWADA"}, {"value": "192", "policeStation": "BABA HARI DASS NAGAR"}, {"value": "193", "policeStation": "ROHINI NORTH"}, {"value": "194", "policeStation": "UDYOG NAGAR"}, {"value": "195", "policeStation": "."}, {"value": "196", "policeStation": "DWARKA SOUTH"}, {"value": "197", "policeStation": "SURAT CRIME BRANCH"}, {"value": "198", "policeStation": "DIRECTORATE OF REVENUE INTELLIGENCE"}, {"value": "199", "policeStation": "MADIPUR"}, {"value": "200", "policeStation": "QUTAB MINAR MATRO"}, {"value": "201", "policeStation": "MADHUBAN"}, {"value": "202", "policeStation": "CITY KOTWALI"}, {"value": "203", "policeStation": "MUNDKA"}, {"value": "204", "policeStation": "ANAND TOWN GUJRAT"}, {"value": "205", "policeStation": "CITY SANGRUR"}, {"value": "206", "policeStation": "NIA"}, {"value": "207", "policeStation": "YAMUNA DEPOT.METRO EAST"}, {"value": "208", "policeStation": "SOUTH CAMPUS"}, {"value": "209", "policeStation": "KUSHAIGUDA"}, {"value": "210", "policeStation": "NAGINA BIJNOR"}, {"value": "211", "policeStation": "SGM NAGAR FARIDABAD"}, {"value": "212", "policeStation": "KASHMIRI GATE METRO STATION"}, {"value": "213", "policeStation": "KAVI NAGAR GHAZIABAD"}, {"value": "214", "policeStation": "KOTWALI NAGAR ETAH UP"}, {"value": "215", "policeStation": "NORTH PARGANA WEST BENGAL"}, {"value": "216", "policeStation": "BOKARO JHARKHAND"}, {"value": "217", "policeStation": "MAHILA THANA SADAR MURADABAD"}, {"value": "218", "policeStation": "TAWRU GURGAON"}, {"value": "219", "policeStation": "KOTWALI MORADABAD UP"}, {"value": "220", "policeStation": "JAIPUR CITY GANDHI NAGAR"}, {"value": "221", "policeStation": "KORBA CHHATISGARSH"}, {"value": "222", "policeStation": "KALKAJI MANDIR METRO STATION"}, {"value": "223", "policeStation": "LASADI GATE MEERUT"}, {"value": "224", "policeStation": "RPF HAZARAT NIZAMUDDIN"}, {"value": "225", "policeStation": "KANKADBAG PATNA BIHAR"}, {"value": "226", "policeStation": "NARNAUND HARYANA"}, {"value": "227", "policeStation": "MAHILA THANA SIKAR RAJASTHA"}, {"value": "228", "policeStation": "DONA PAULA GOA"}, {"value": "229", "policeStation": "KOTWALI ROORKEE HARIDWAR"}, {"value": "230", "policeStation": "TIRUPPUR TAMILNADU"}, {"value": "231", "policeStation": "JAHANGIRPUR,DISTRICT SURAT,GUJARAT"}, {"value": "232", "policeStation": "BASANT VIHAR DEHRADUN"}, {"value": "233", "policeStation": "N.M.JOSHI MARG MUMBAI"}, {"value": "234", "policeStation": "HUBLI DHARWAD KARNATAKA"}, {"value": "235", "policeStation": "KOREGAON PARK PUNE MAHARASHTRA"}, {"value": "236", "policeStation": "NAMKUM RANCHI JHARKHAND"}, {"value": "237", "policeStation": "BANUR DISTT PATIALA PUNJAB"}, {"value": "238", "policeStation": "ANAND VIHAR RAILWAY STATION"}, {"value": "239", "policeStation": "SIKAR RAJASTHAN"}, {"value": "240", "policeStation": "CITY ROHTAK"}, {"value": "241", "policeStation": "QAISER BAGH LUCKNOW"}, {"value": "242", "policeStation": "DIBRUGARH ASSAM"}, {"value": "243", "policeStation": "MAINPURI KOTWAI UTTAR PRADESH"}, {"value": "244", "policeStation": "NAMUKUM RANCHI JHARKHAND"}, {"value": "245", "policeStation": "JUHU MAHARASHTRA MUMBAI"}, {"value": "246", "policeStation": "NEHRU COLONY DEHRADUN UTTRAKHAND"}, {"value": "247", "policeStation": "PANIPAT CITY"}, {"value": "248", "policeStation": "INDIRAPURAM GHAZIABAD"}, {"value": "249", "policeStation": "JAGADHRI CITY YAMUNA NAGAR JAGADHRI CITY"}, {"value": "250", "policeStation": "MASOORI DISTT. GHAZIABAD"}, {"value": "251", "policeStation": "CIVIL LINES AMRITSAR PUNJAB"}, {"value": "252", "policeStation": "MAHILA THANA PATIALA PUNJAB"}, {"value": "253", "policeStation": "CID BHARARI SHIMLA HIMACHAL PRADESH"}, {"value": "254", "policeStation": "CIVIL LINES GURGAON"}, {"value": "255", "policeStation": "SUSHANT LOK GURGAON"}, {"value": "256", "policeStation": "CHANDIGARH SOUTH SECTOR"}, {"value": "257", "policeStation": "JORABAGAN KOLKATA"}, {"value": "258", "policeStation": "BARAUT DISTT. BAGHPAT UP"}, {"value": "259", "policeStation": "KASNA GAUTAM BUDH NAGAR UP"}, {"value": "260", "policeStation": "JANGDIALA GURU AMRITSAR PUNJAB"}, {"value": "261", "policeStation": "FEROZEPUR JHIRKA MEWAT HARYANA"}, {"value": "262", "policeStation": "DWARKA SECTOR TWENTY THREE"}, {"value": "263", "policeStation": "POWAI MUMBAI"}, {"value": "264", "policeStation": "CRIME BRANCH SRINAGAR JAMMU AND KASHMIR"}, {"value": "265", "policeStation": "DHARAMPUR SOLAN HIMACHAL PRADESH"}, {"value": "266", "policeStation": "VASCO POLICE STATION GOA"}, {"value": "267", "policeStation": "BARADARI BARELLI UP"}, {"value": "268", "policeStation": "DIRECTORATE OF ENFORCEMENT"}, {"value": "269", "policeStation": "MADHOTANDA UTTAR PRADESH"}, {"value": "270", "policeStation": "EOW MUMBAI"}, {"value": "271", "policeStation": "JAMA SADAR JHARKHAND"}, {"value": "272", "policeStation": "BURTOLLA KOLKATA"}, {"value": "273", "policeStation": "BADOT UTTAR PRADESH"}, {"value": "274", "policeStation": "KOTWALI JALPAIGURI WEST BENGAL"}, {"value": "275", "policeStation": "SIRSA HARYANA"}, {"value": "276", "policeStation": "URBAN STATE ROHTAK"}, {"value": "277", "policeStation": "RAJINDER NAGAR RAIPUR CHATTISGARH"}, {"value": "278", "policeStation": "ANANTNAG  JAMMU AND KASHMIR"}, {"value": "279", "policeStation": "SILIGURI DARJEELING"}, {"value": "280", "policeStation": "KOTWALI BHARATPUR RAJASTHAN"}, {"value": "281", "policeStation": "CID JAIPUR"}, {"value": "282", "policeStation": "RAM SHAHER HIMACHAL PRADES"}, {"value": "283", "policeStation": "PILUKHWA DISTRICT HAPUR"}, {"value": "284", "policeStation": "THELUPUR VARANASI"}, {"value": "285", "policeStation": "BAHADURGARH HARYANA"}, {"value": "286", "policeStation": "MURAD NAGAR"}, {"value": "287", "policeStation": "LINK ROAD GHAZIABAD"}, {"value": "288", "policeStation": "LONI GHAZIABAD"}, {"value": "289", "policeStation": "BOKHERA KOTA CITY RAJASTHAN"}, {"value": "290", "policeStation": "PILUKHWA"}, {"value": "291", "policeStation": "KAIRANA DISTRICT MUZZAFARNAGAR UP"}, {"value": "292", "policeStation": "GOMTI NAGAR LUCKNOW"}, {"value": "293", "policeStation": "CITY FEROZEPUR PUNJAB"}, {"value": "294", "policeStation": "CHAMARAJPET BANGALORE CITY KARNATAKA"}, {"value": "295", "policeStation": "UDAIPUR RAJASTHAN"}, {"value": "296", "policeStation": "KHURJA U.P."}, {"value": "297", "policeStation": "CRIME BRANCH ECONOMIC OFFENCE WING CID BHUBANESHYWAR ORDISHA"}, {"value": "298", "policeStation": "KOTWALI DEHAT BULANDSHAHAR UTTAR PRADESH"}, {"value": "299", "policeStation": "PARK STEET KOLKOTTA"}, {"value": "300", "policeStation": "HAILAKANDI ASSAM"}, {"value": "301", "policeStation": "CIVIL LINES ALLAHABAD"}, {"value": "302", "policeStation": "SRIKAKULAM ICHAPURAM ANDHRA PRADESH"}, {"value": "303", "policeStation": "NIT FARIDABAD HARYANA"}, {"value": "304", "policeStation": "CIVIL LINES PATIALA"}, {"value": "305", "policeStation": "VIGILANCE AND ANTI COR. PALAKKAD KERALA"}, {"value": "306", "policeStation": "MAHILA THANA DISTT. JODHPUR EAST"}, {"value": "307", "policeStation": "RAJGARH DISTRICT CHURU RAJASTHAN"}, {"value": "308", "policeStation": "LAXMI SAGAR BHUVNESHWAR ODISHA"}, {"value": "309", "policeStation": "MAHILA THANA BANNI PARK WEST DISST. JAIPUR RAJASTHAN"}, {"value": "310", "policeStation": "MADAN MOHAN GATE AGRA"}, {"value": "311", "policeStation": "GURGAON SECTOR SEVENTEEN/EIGHTEEN"}, {"value": "312", "policeStation": "FARIDABAD OUTSIDE"}, {"value": "313", "policeStation": "CIVIL LINES ROHTAK HARYANA"}, {"value": "314", "policeStation": "WAKAD MAHARASHTRA"}, {"value": "315", "policeStation": "GULBARGA RURAL KARNATAKA"}, {"value": "316", "policeStation": "WAZIR GANJ LUCKNOW UTTAR PRADESH"}, {"value": "317", "policeStation": "NORTH AVENUE"}, {"value": "318", "policeStation": "TUTICORIN TAMIL NADU"}, {"value": "319", "policeStation": "BANIYADHER U.P."}, {"value": "320", "policeStation": "VIGILANCE"}, {"value": "321", "policeStation": "W FOUR AWPS KILPAUK"}, {"value": "322", "policeStation": "GOVIND NAGAR MATHURA UP"}, {"value": "323", "policeStation": "GHAT LODIA AHMEDABAD GUJRAT"}, {"value": "324", "policeStation": "CIVIL LINES HISAR HARYANA"}, {"value": "325", "policeStation": "GAUTAM BUDH NAGAR SECTOR THIRTY NINE U.P."}, {"value": "326", "policeStation": "GAUTAM BUDH NAGAR SECTOR FIFTY EIGHT NOIDA UP"}, {"value": "327", "policeStation": "SOUTH AVENUE"}, {"value": "328", "policeStation": "LINE PAR BAHADURGARH"}, {"value": "329", "policeStation": "MUBBALANIPALEN VISAKHAPATNAM"}, {"value": "330", "policeStation": "MAHILA THANA GAUTAM BUDH NAGAR"}, {"value": "331", "policeStation": "DADRI GAUTAM BUDH NAGAR UTTAR PRADESH"}, {"value": "332", "policeStation": "PALTAN BAZAR ASSAM"}, {"value": "333", "policeStation": "CANTT. KANPUR CITY"}, {"value": "334", "policeStation": "KASHIMIRA DISTT THANE MAHARASHTRA"}, {"value": "335", "policeStation": "TOURISH POLICE STATION TRC SRINAGAR JAMMU AND KASHMIR"}, {"value": "336", "policeStation": "NAUPADA THANE MAHARASHTRA"}, {"value": "337", "policeStation": "BHIMTAL NAINTAL"}, {"value": "338", "policeStation": "JYOTI NAGAR JAIPUR SOUTH"}, {"value": "339", "policeStation": "KAIRANA DISTRICT MUJJAFANAGAR UP"}, {"value": "340", "policeStation": "KOTWALI DISTT. SAGAR MADHYA PRADESH"}, {"value": "341", "policeStation": "PANCHKULA SECTOR V PANCHKULA"}, {"value": "342", "policeStation": "MAGADH MEDICAL DISTT. GAYA BIHAR"}, {"value": "343", "policeStation": "PARK SITE MUMBAI"}, {"value": "344", "policeStation": "BHONDSI DISTRICT GURUGRAM HARYANA"}, {"value": "345", "policeStation": "CUSTOMS"}, {"value": "346", "policeStation": "MAHILA THANA DISTRICT GAZIABAD"}, {"value": "347", "policeStation": "JAHANGIRABAD DISTRICT BULANDSHAHAR UTTAR PRADES"}, {"value": "348", "policeStation": "TARA NAGAR DISTT. CHURU RAJASTHAN"}, {"value": "349", "policeStation": "SARABHA NAGAR LUDHIANA CITY PUNJAB"}, {"value": "350", "policeStation": "SUBZI MANDI RAILWAY STATION"}, {"value": "351", "policeStation": "BARIYATU RANCHI"}, {"value": "352", "policeStation": "KOTWALI MURENA MADHYA PARDESH"}, {"value": "353", "policeStation": "GAUTAM BUDH NAGAR WOMEN POLICE STATION"}, {"value": "354", "policeStation": "CHANDNI BAGH PANIPAT"}, {"value": "355", "policeStation": "CIVIL LINES BILASPUR CHHATTISGARH"}, {"value": "356", "policeStation": "SADAR SHERASA BIHAR"}, {"value": "357", "policeStation": "KOTWALI MANDI UP"}, {"value": "358", "policeStation": "BEHROR RAJASTHAN"}, {"value": "359", "policeStation": "BHAWANIPORE KOLKATA WEST BENGAL"}, {"value": "360", "policeStation": "JEWAR DISTT. GAUTAM BUDH NAGAR UP"}, {"value": "361", "policeStation": "CIVIL LINES MORADABAD UP"}, {"value": "362", "policeStation": "KOTWALI NAGAR DHERADUN"}, {"value": "363", "policeStation": "VISHWAKARMA JAIPUR"}, {"value": "364", "policeStation": "MUCHIPARA KOLKATA WEST BENGAL"}, {"value": "365", "policeStation": "KOTWALI PATNA NAGAR"}, {"value": "366", "policeStation": "NEHRU PLACE METRO"}, {"value": "367", "policeStation": "BELIPAR GORAKPUR UP"}, {"value": "368", "policeStation": "RAJ PARK"}, {"value": "369", "policeStation": "NAJIBABAD UP"}, {"value": "370", "policeStation": "PATASHPUR DISTRIC PURBA MEDINIPUR WEST BENGAL"}, {"value": "371", "policeStation": "KISHAN GARH"}, {"value": "372", "policeStation": "KHAIRTHAL JILA ALWAR RAJASTHAN"}, {"value": "373", "policeStation": "TIGRI"}, {"value": "374", "policeStation": "LAMLAI MANIPUR"}, {"value": "375", "policeStation": "BURRABAZAR"}, {"value": "376", "policeStation": "BUDH VIHAR"}]
    return json.dumps(list_of_stations)

@app.route("/certified_copies_side")
@cache.cached(timeout=60000)
def certified_copies_side():
    list_of_sides = [{"value": "ALL", "side": "ALL"}, {"value": "A", "side": "APPLLATE"}, {"value": "O", "side": "ORIGINAL"}, {"value": "W", "side": "WRIT"}]
    return json.dumps(list_of_sides)

@app.route("/judgments_judgename")
@cache.cached(timeout=60000)
def judgments_judgename():
    list_of_judges = [{"judgename": "Select one", "value": ""}, {"judgename": "CHIEF JUSTICE RAJENDRA MENON", "value": "103"}, {"judgename": "JUSTICE A.K. CHAWLA", "value": "94"}, {"judgename": "JUSTICE A. K. PATHAK", "value": "68"}, {"judgename": "JUSTICE ANU MALHOTRA", "value": "97"}, {"judgename": "JUSTICE ANUP JAIRAM BHAMBHANI", "value": "106"}, {"judgename": "JUSTICE CHANDER SHEKHAR", "value": "96"}, {"judgename": "JUSTICE C. HARI SHANKAR", "value": "102"}, {"judgename": "JUSTICE G. S. SISTANI", "value": "12"}, {"judgename": "JUSTICE HIMA KOHLI", "value": "13"}, {"judgename": "JUSTICE I. S. MEHTA", "value": "89"}, {"judgename": "JUSTICE JAYANT NATH", "value": "78"}, {"judgename": "JUSTICE J.R. MIDHA", "value": "57"}, {"judgename": "JUSTICE JYOTI SINGH", "value": "104"}, {"judgename": "JUSTICE MANMOHAN", "value": "53"}, {"judgename": "JUSTICE MANOJ KUMAR OHRI", "value": "108"}, {"judgename": "JUSTICE MUKTA GUPTA", "value": "70"}, {"judgename": "JUSTICE NAJMI WAZIRI ", "value": "83"}, {"judgename": "JUSTICE NAVIN CHAWLA", "value": "101"}, {"judgename": "JUSTICE PRATEEK JALAN", "value": "105"}, {"judgename": "JUSTICE PRATHIBA M. SINGH", "value": "100"}, {"judgename": "JUSTICE RAJIV SAHAI ENDLAW", "value": "61"}, {"judgename": "JUSTICE RAJIV SHAKDHER", "value": "60"}, {"judgename": "JUSTICE REKHA PALLI", "value": "99"}, {"judgename": "JUSTICE R. K. GAUBA", "value": "90"}, {"judgename": "JUSTICE SANGITA DHINGRA SEHGAL", "value": "91"}, {"judgename": "JUSTICE SANJEEV NARULA", "value": "107"}, {"judgename": "JUSTICE SANJEEV SACHDEVA", "value": "79"}, {"judgename": "JUSTICE SIDDHARTH MRIDUL", "value": "52"}, {"judgename": "JUSTICE S. MURALIDHAR", "value": "40"}, {"judgename": "JUSTICE S.RAVINDRA BHAT", "value": "43"}, {"judgename": "JUSTICE SUNIL GAUR", "value": "69"}, {"judgename": "JUSTICE SURESH KUMAR KAIT", "value": "58"}, {"judgename": "JUSTICE VALMIKI J. MEHTA", "value": "64"}, {"judgename": "JUSTICE VIBHU BAKHRU", "value": "80"}, {"judgename": "JUSTICE VINOD GOEL", "value": "95"}, {"judgename": "JUSTICE VIPIN SANGHI", "value": "51"}, {"judgename": "JUSTICE V. KAMESWAR RAO", "value": "81"}, {"judgename": "JUSTICE YOGESH KHANNA", "value": "98"}, {"judgename": "---------------FORMER JUDGES-----------------------", "value": ""}, {"judgename": "JUSTICE AJIT BHARIHOKE", "value": "65"}, {"judgename": "JUSTICE AJIT PRAKASH SHAH", "value": "59"}, {"judgename": "JUSTICE A.K.SIKRI", "value": "2"}, {"judgename": "JUSTICE ANIL KUMAR", "value": "1"}, {"judgename": "JUSTICE ARUNA SURESH", "value": "3"}, {"judgename": "JUSTICE ASHUTOSH KUMAR", "value": "92"}, {"judgename": "JUSTICE BADAR DURREZ AHMED", "value": "6"}, {"judgename": "JUSTICE B.A.KHAN", "value": "4"}, {"judgename": "JUSTICE B.C.PATEL", "value": "5"}, {"judgename": "JUSTICE B.N.CHATURVEDI", "value": "7"}, {"judgename": "JUSTICE C.K.MAHAJAN", "value": "8"}, {"judgename": "JUSTICE DALVEER BHANDARI", "value": "9"}, {"judgename": "JUSTICE DEEPA SHARMA", "value": "82"}, {"judgename": "JUSTICE DIPAK MISRA", "value": "71"}, {"judgename": "JUSTICE D.K.JAIN", "value": "10"}, {"judgename": "JUSTICE D.MURUGESAN", "value": "77"}, {"judgename": "JUSTICE GITA MITTAL", "value": "11"}, {"judgename": "JUSTICE G.P.  MITTAL", "value": "72"}, {"judgename": "JUSTICE G. ROHINI", "value": "87"}, {"judgename": "JUSTICE H. R. MALHOTRA", "value": "14"}, {"judgename": "JUSTICE INDERMEET KAUR", "value": "67"}, {"judgename": "JUSTICE INDIRA BANERJEE", "value": "93"}, {"judgename": "JUSTICE J.D.KAPOOR", "value": "15"}, {"judgename": "JUSTICE J.M. MALIK", "value": "16"}, {"judgename": "JUSTICE J.P. SINGH", "value": "17"}, {"judgename": "JUSTICE KAILASH GAMBHIR", "value": "18"}, {"judgename": "JUSTICE MADAN B. LOKUR", "value": "20"}, {"judgename": "JUSTICE MAHMOOD ALI KHAN", "value": "19"}, {"judgename": "JUSTICE MANJU GOEL", "value": "21"}, {"judgename": "JUSTICE MANMOHAN SARIN", "value": "24"}, {"judgename": "JUSTICE MANMOHAN SINGH", "value": "56"}, {"judgename": "JUSTICE MARKANDEYA KATJU", "value": "22"}, {"judgename": "JUSTICE M. L. MEHTA", "value": "73"}, {"judgename": "JUSTICE MOOL CHAND GARG", "value": "55"}, {"judgename": "JUSTICE MUKUL MUDGAL", "value": "23"}, {"judgename": "JUSTICE MUKUNDAKAM SHARMA", "value": "25"}, {"judgename": "JUSTICE NEETRAJ KISHAN KAUL", "value": "63"}, {"judgename": "JUSTICE N.V. RAMANA", "value": "86"}, {"judgename": "JUSTICE O.P.DWIVEDI", "value": "26"}, {"judgename": "JUSTICE P.K.BHASIN", "value": "27"}, {"judgename": "JUSTICE PRADEEP NANDRAJOG", "value": "28"}, {"judgename": "JUSTICE PRATIBHA RANI", "value": "75"}, {"judgename": "JUSTICE P. S. TEJI ", "value": "88"}, {"judgename": "JUSTICE R.C.CHOPRA", "value": "29"}, {"judgename": "JUSTICE R.C.JAIN", "value": "30"}, {"judgename": "JUSTICE REKHA SHARMA", "value": "32"}, {"judgename": "JUSTICE REVA KHETRAPAL", "value": "31"}, {"judgename": "JUSTICE R.S. SODHI", "value": "33"}, {"judgename": "JUSTICE R.V. EASWAR", "value": "74"}, {"judgename": "JUSTICE SANJAY KISHAN KAUL", "value": "36"}, {"judgename": "JUSTICE SANJIV KHANNA", "value": "38"}, {"judgename": "JUSTICE SHIV NARAYAN DHINGRA", "value": "42"}, {"judgename": "JUSTICE S.K. AGARWAL", "value": "35"}, {"judgename": "JUSTICE S.K.MAHAJAN", "value": "37"}, {"judgename": "JUSTICE S.L.BHAYANA", "value": "39"}, {"judgename": "JUSTICE S.N. AGGARWAL", "value": "41"}, {"judgename": "JUSTICE S. P. GARG", "value": "76"}, {"judgename": "JUSTICE SUDERSHAN KUMAR MISRA", "value": "44"}, {"judgename": "JUSTICE SUNITA GUPTA", "value": "85"}, {"judgename": "JUSTICE SWATANTER KUMAR", "value": "34"}, {"judgename": "JUSTICE TIRATH SINGH THAKUR", "value": "45"}, {"judgename": "JUSTICE USHA MEHRA", "value": "46"}, {"judgename": "JUSTICE V.B.GUPTA", "value": "48"}, {"judgename": "JUSTICE VEENA BIRBAL", "value": "47"}, {"judgename": "JUSTICE VIJENDER JAIN", "value": "49"}, {"judgename": "JUSTICE VIKRAMAJIT SEN", "value": "50"}, {"judgename": "JUSTICE V. K. JAIN", "value": "66"}, {"judgename": "JUSTICE V.K.SHALI", "value": "54"}, {"judgename": "JUSTICE V.P.VAISH", "value": "84"}]
    return json.dumps(list_of_judges)

@app.route("/judgments_partyname")
def judgments_partyname():
    list_of_partyname = [{"type": "Petitioner", "value": "P"}, {"type": "Respondent", "value": "R"}, {"type": "Don't Know ", "value": "O"}]
    return json.dumps(list_of_partyname)

# http://localhost:5000/ccopies/9242/2014/CW
# #http://localhost:5000/ccopies/9242/2014/ALL
# @app.route('/ccopies/<caseno>/<cyear>/<ctype>')
# def certified_copy(caseno, cyear, ctype):
#     return getCertifiedCopies(caseno, cyear, ctype)

# http://localhost:5000/ccopies?caseno=9242&cyear=2014&ctype=ALL&deli=ON
@app.route('/ccopies')
def certified_copy():
    try:
        caseno = request.args.get('caseno')
        cyear = request.args.get('cyear')
        ctype = request.args.get('ctype')
        deli = request.args.get('deli')
        return_this = scrp.getCertifiedCopiesSimple(caseno, cyear, ctype, deli)
        return return_this

    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})


@app.route('/ccappliedby/<applied_by>/<diary_yr>/<cyear>')
def cert_copy_app_by(applied_by, diary_yr, cyear):
    try:
        return scrp.getCertifiedApliedby(applied_by, diary_yr, cyear)
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})


@app.route("/judges_roster")
@cache.cached(timeout=300)
def JudgesRoster():
    try:
        return scrp.getJudgesRoster()
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})


@app.route("/cause_list")
@cache.cached(timeout=300)
def Cause_List():
    try:

        return jsonify(scrp.getCauseList())
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})


@app.route("/nominated_counsel")
@cache.cached(timeout=300)
def Nominated_Counsel():
    try:
        return scrp.getNominatedCounsel()
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})


@app.route("/history")
def History():
    return getHistory()


@app.route('/feedback', methods=['POST'])
def feedback():
    email = "dhcbaofficial1@gmail.com"
    content = request.form.get('content')
    subject = request.form.get('subject')
    if (str(content) or str(subject)) == "None":
        return jsonify({"status": "unsuccessful"})
    return jsonify(send_email(str(email), str(subject), str(content)))


@app.route("/sjudges")
@cache.cached()
def Sjudges():
    try:
        return jsonify(scrp.SittingJudges())
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})


@app.route("/Updateddforms")
@cache.cached()
def Udforms():
    return jsonify(scrp.GetDforms())


@app.route("/qforms")
@cache.cached()
def Qforms():
    return qforms()


@app.route('/ebooks/<filename>')
def return_files_tut(filename):
    try:
        return send_file('static/ebooks/' + filename, attachment_filename='{0}.pdf'.format(filename))
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})


@app.route('/dictionary/')
@cache.cached()
def retdict():
    try:
        return ret_dict()
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})


@app.route('/calendar')
@cache.cached()
def calendar():
    return jsonify({"2019": "http://delhihighcourt.nic.in/writereaddata/upload/PreviousCal/PreCalender_2019_1FM8HKVU4M0.PDF",
                    "2018": "https://s3.ap-south-1.amazonaws.com/dhcapi/Calendar/calendar_2018_compressed.pdf"})


@app.route('/judgement')
def judgement():
    ctype = request.args.get('ctype')
    cnum = request.args.get('cnum')
    cyear = request.args.get('cyear')
    cdesc = request.args.get('cdesc')

    return_this = scrp.getJudgement(ctype, cnum, cyear, cdesc)
    return jsonify(return_this)


# http://127.0.0.1:5000/judgement?ctype=CW&cnum=922&cyear=2014&cdesc=Array4

@app.route('/act/')
@cache.cached()
def ret_act():
    try:
        return send_file('static/DELHI_HIGH_COURT_ACT_1966.pdf', attachment_filename='DELHI_HIGH_COURT_ACT.pdf')
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})


@app.route('/notices')
@cache.cached(timeout=300)
def gen_notices():
    try:
        return scrp.getGenNotices()
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})


# @app.route('/lawdict/<alp>')
# def GetLawDict(alp):
#     try:
#         return getLawDictionary(alp)
#     except Exception as e:
#         return str(e)
#
@app.route('/d/<word>')
def dictWord(word):
    try:
        return getDictWord(word)
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})


# @app.route('/allebooks')
# def allebooks():
#     try:
#         return Getebooksonline()
#     except:
#         return 'not available'

@app.route('/bookslink')
@cache.cached()
def bookslinks():
    return booklinks()


@app.route('/eblist')
@cache.cached()
def eblist():
    return bookslinkslist()


@app.route('/book/<book>')
def book(book):
    try:
        return all_books(book)
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})


# /member_directory/name?name=sam&suggestion=true
@app.route('/member_directory/name')
def member_directory_name():
    name = request.args.get('name')
    suggestion = str(request.args.get('suggestion')).lower()
    if suggestion == 'true':
        return jsonify(get_member_directory_ByNameSuggestion(name, True))
    else:
        return jsonify(get_member_directory_ByNameSuggestion(name, False))


@app.route('/member_directory')
def member_directory_name_pagination():
    name = request.args.get('name')
    offset = request.args.get('offset')
    suggestion = str(request.args.get('suggestion')).lower()
    if suggestion == 'true':
        return jsonify(get_member_directory_ByNameSuggestionPagination(name, True, offset))
    else:
        return jsonify(get_member_directory_ByNameSuggestionPagination(name, False, offset))
    

@app.route('/member_directory_startingWord')
def member_directory_starting_word():
    keyword = request.args.get('keyword')
    starting_word = request.args.get('starting_word')
   
    return jsonify(get_member_directory_ByStartingWord(keyword, starting_word))
    


# /member_directory/id?idz=100
@app.route('/member_directory/id')
def member_directory_id():
    idz = request.args.get('idz')
    return jsonify(get_member_directory_ByID(idz))


# send_mail?p=sameer18051998@gmail.com&s=test&b=test
@app.route('/send_mail')
def email():
    emailto = request.args.get('p')
    subject = request.args.get('s')
    body = request.args.get('b')

    return jsonify(send_email(emailto, subject, body))


@app.route('/displayboard')
def dispBoard():
    try:
        return scrp.displayBoardNew()
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})

@app.route('/displaysession')
def dispSession():
    try:
        return scrp.getsession(request.args.get('url'))
    except Exception as e:
        print(e)
        return jsonify({"status": "unsuccessful"})



@app.route('/library')
@cache.cached()
def library_list():
    return read_library()

@app.route('/privacy_policy')
@cache.cached()
def privacy_policy():
    return get_priv_pol()

@app.route('/terms_conditions')
@cache.cached()
def termsandcondition():
    return terms_conditions()


def bool_it(value):
    value = str(value).lower()
    if value == 'true':
        return True
    elif value == 'false':
        return False

@app.route('/notifications_enabled',methods=['POST'])
def notifications_enabled():
    device_id = request.form.get('device_id')
    typez = request.form.get('type')

    if typez == "get":
        q = Notifications.query.filter_by(device_id=device_id).all()
        for i in q:
            notification = {"cause_list":(i.cause_list),"nominated_counsel":(i.nominated_counsel),
                           "judges_roster":(i.judges_roster),"bar_notifications":(i.bar_notifications),
                           "notices": i.notices, "events":(i.events), "obituary":(i.obituary), "electioncommittee":(i.electioncommittee)}

        return jsonify(notification)
    elif typez == "set":
        electioncommittee = bool_it(request.form.get('electioncommittee'))
        cause_list = bool_it(request.form.get('cause_list'))
        nominated_counsel = bool_it(request.form.get('nominated_counsel'))
        judges_roster = bool_it(request.form.get('judges_roster'))
        bar_notifications = bool_it(request.form.get('bar_notifications'))
        notices = bool_it(request.form.get('notices'))
        events = bool_it(request.form.get('events'))
        obituary = bool_it(request.form.get('obituary'))
        record = Notifications.query.filter_by(device_id=device_id).first()
        record.cause_list = cause_list
        record.nominated_counsel = nominated_counsel
        record.judges_roster = judges_roster
        record.bar_notifications = bar_notifications
        record.notices = notices
        record.events = events
        record.obituary = obituary
        db.session.add(record)
        db.session.commit()
        return jsonify({"status" : "successful"})

@cron.interval_schedule(minutes=30.0)
def notification_cause_list():
    with app.app_context():
        current = str(scrp.getCauseList())
        # existing = json.loads(str(Compare_data.query.get(1).cause_list.decode("utf-8")))
        existing = Compare_data.query.get(1).cause_list.decode("utf-8")
        if compare(current) == compare(existing):
            print("same cause_list")
        else:
            print("different cause_list")
            notify("Delhi high court", "Daily Cause list", method="cause_list", signals=5)
            record = Compare_data.query.get(1)
            record.cause_list=str(current)
            db.session.add(record)
            db.session.commit()


@cron.interval_schedule(minutes=5.0)
def notification_judges_roster():
    with app.app_context():
        current = str(scrp.getJudgesRoster())
        existing = Compare_data.query.get(1)
        if current == (existing.judges_roster).decode("utf-8"):
            print("same judges_roster")
        else:
            print("different judges_roster")
            notify("Delhi High Court","Daily Judges Roster",method="judges_roster", signals=6)
            record = Compare_data.query.get(1)
            record.judges_roster=current
            db.session.add(record)
            db.session.commit()


@cron.interval_schedule(minutes=5.5)
def notification_nominated_counsel():
    with app.app_context():
        current = str(scrp.getNominatedCounsel())
        existing = Compare_data.query.get(1)
        if current == (existing.nominated_counsel).decode("utf-8"):
            print("same nominated_counsel")
        else:
            print("different nominated_counsel")
            notify("Delhi High Court","Daily Nominated Counsel",method="nominated_counsel", signals=7)
            record = Compare_data.query.get(1)
            record.nominated_counsel=current
            db.session.add(record)
            db.session.commit()

from flask_docs import Flask_docs

atexit.register(lambda: cron.shutdown(wait=False))

import logging
handler = logging.FileHandler('app.log')  # errors logged to this file
app.logger.addHandler(handler)  # attach the handler to the app's logger

if __name__ == '__main__':
    #   docs = Flask_docs()
    #   docs.from_app(app,all_method=False)
    app.run(threaded=True, host="0.0.0.0", debug=True)
    #    manager.run()

