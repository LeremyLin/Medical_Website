
import web
import hashlib
from web import form
import pymysql
import json
import types 
import datetime
import time
import cgi, cgitb
pymysql.install_as_MySQLdb()

db = web.database(dbn='mysql',host='mysql.uiccst.com', user='l630003034', pw='123456', db='l630003034')
# router
urls = (
    '/login','login',
    '/login2','login2',
    '/login3','login3',
    '/logout','logout',
    '/register', 'register',
    '/add','add',
    '/add2','add2',
    '/MyRecord','MyRecord',
    '/patientHome','patientHome',
    '/doctorHome','doctorHome',
    '/adminHome','adminHome',
    '/drugAdmin','drugAdmin',
    '/NewAppoint','NewAppoint',
    '/BuyDrug','BuyDrug',
     '/deal/(.*)','deal',
    '/dealDoctor','dealDoctor',
    '/mainPage','mainPage',
    '/doctorRecord','doctorRecord',
    '/addRecord','addRecord',
    '/doctorAppoint','doctorAppoint',
    '/window1','window1',
    '/window2','window2',
    '/window3','window3',
    '/window4','window4',
    '/dealDepart','dealDepart'
   
)
#mysql.uiccst.com
# use session to set debug to False
web.config.debug = False 
app = web.application(urls, globals())

session = web.session.Session(app, web.session.DiskStore('sessions'))

# templates
render = web.template.render('templates/',globals={'context': session})


#user choose role
class mainPage:
    def GET(self):
        if session.get('logged_in'):
            session.kill()
            return render.index()
        else:
            return render.index()

# patient login
class login:
    def GET(self):
        if session.get('logged_in'):
            session.kill()
            return render.login()
        else:
            return render.login()
        
    def POST(self):
        i = web.input()
        ID = i.get('id')
        password = i.get('pass')
        #password = md5(i.get('password'))
        myvar = dict(pid=ID,Password=password) 
        results = list(db.select('patient',myvar, where="pid=$pid and Password=$Password"))
        if results:
            session.logged_in = True
            session.pid= results[0].pid
            session.pname = results[0].Name
            session.pgender = results[0].Gender
            session.ppassword = results[0].Password
            return web.seeother('/patientHome')

        else:
            return render.window4()


# doctor login
class login2:
    def GET(self):
        if session.get('logged_in'):
            session.kill()
            return render.login2()
        else:
            return render.login2()
        
    def POST(self):
        i = web.input()
        did = i.get('id')
        dPass = i.get('pass')
        #password = md5(i.get('password'))
        myvar = dict(did=did,dPass=dPass) 
        results = list(db.select('doctor',myvar, where="did=$did and dPass=$dPass"))
        if results:
            session.logged_in = True
            session.did= results[0].did
            session.dname = results[0].dName
            session.department = results[0].department
            session.dpassword = results[0].dPass
            return web.seeother('/doctorHome')

        else:
            return render.window4()


# doctor login
class login3:
    def GET(self):
        if session.get('logged_in'):
            session.kill()
            return render.login3()
        else:
            return render.login3()
        
    def POST(self):
        i = web.input()
        aid = i.get('id')
        aPass = i.get('pass')
        #password = md5(i.get('password'))
        myvar = dict(aid=aid,aPass=aPass) 
        results = list(db.select('administrator',myvar, where="aid=$aid and aPass=$aPass"))
        if results:
            session.logged_in = True
            session.aid= results[0].aid
            session.aName = results[0].aName
            session.aPass = results[0].aPass
            return web.seeother('/adminHome')

        else:
            return render.window4()



# user logout
class logout:
    def GET(self):
        session.kill()
        return render.logout()


#patient home
class patientHome:
    def GET(self):
        if session.get('logged_in'):
            return render.patientHome()
        else:
            return render.login()

#doctor home
class doctorHome:
    def GET(self):
        if session.get('logged_in'):
            return render.doctorHome()
        else:
            return render.login2()
# drugAdmin Home
class adminHome:
    def GET(self):
        if session.get('logged_in'):
            return render.adminHome()
        else:
            return render.login3()

# register
class register:
    def GET(self):
    	todos = db.select('patient')
    	return render.register(todos)
        # return "Hello, world!"

# add method to patient
class add:
    def POST(self):
        i = web.input()
        m = db.insert('patient',name=i.name,gender=i.sex,Password=i.password)
        raise web.seeother('/window2')



# addRecord
class addRecord:
    def GET(self):
    	todos = db.select('medical_record')
    	return render.addRecord(todos)
        # return "Hello, world!"


# doctor add to patient record
class add2:
    def POST(self):
        i = web.input()
        did=str(session.get('did'))
        today=datetime.date.today()
        m = db.insert('medical_record',pid=i.pid,did=did, diagnose=i.diagnose,prescription=i.prescription,time=today)
        raise web.seeother('/addRecord')



#patient record
class MyRecord:
    def GET(self):
        if session.get('logged_in'):
            #pid = str(session.get('pid'))
            pid=str(session.get('pid'))
            sql='select * from medical_record where pid='+pid+''
            #sql = 'select *,roomorder.id as rid from roomorder join timetable on roomorder.timetable_id = timetable.id where user_id='+uid+' order by apply_date DESC'
            resultList = list(db.query(sql) )           
            return render.MyRecord(resultList)
    
        return render.login()

    
#patient buy drug
class BuyDrug:
    def GET(self):
        if session.get('logged_in'):
            i = web.input()
            drugName=str(i.get('drugName'))
            drugId=str(i.get('drugId'))
            drugAmount=str(i.get('drugAmount'))
            if drugId!='None' and drugAmount!='None':
                sql='update drug_catalog set amount=amount-'+drugAmount+' where drugID=\''+drugId+'\''
                db.query(sql)
            if drugName!='None':
                sql='select * from drug_catalog where drugName=\''+drugName+'\''
                resultList = list(db.query(sql) )
                return render.BuyDrug(resultList)
            sql='select * from drug_catalog limit 7'
            resultList = list(db.query(sql) )
            return render.BuyDrug(resultList)
        return render.mainPage()



#drug admin
class drugAdmin:
    def GET(self):
        if session.get('logged_in'):
            i = web.input()
            drugId=str(i.get('drugId'))
            drugAmount=str(i.get('drugAmount'))
            drugName=str(i.get('drugName'))
            if drugId!='None' and drugAmount!='None':
                sql='update drug_catalog set amount=amount+'+drugAmount+' where drugID=\''+drugId+'\''
                db.query(sql)
            if drugName!='None':
                sql='select * from drug_catalog where drugName=\''+drugName+'\''
                resultList = list(db.query(sql) )
                return render.drugAdmin(resultList)
            sql='select * from drug_catalog limit 7'
            resultList = list(db.query(sql) )
            return render.drugAdmin(resultList)
        return render.login3()



# doctor record
class doctorRecord:
    def GET(self):
        if session.get('logged_in'):
            i = web.input()
            pid=str(i.get('pid'))
            if pid=='None':
                sql='select * from medical_record where pid=0'
                resultList = list(db.query(sql) )
            else:
                sql='select * from medical_record where pid='+pid+''
                resultList = list(db.query(sql) )
            return render.doctorRecord(resultList)
        return render.login2()

class dealDepart:
    def GET(self):
        if session.get('logged_in'):
            i = web.input()
            department=str(i.get('department'))
            print(department)
            sql='select * from doctor where department=\''+department+'\''
            resultList = list(db.query(sql) )
            return render.NewAppoint(resultList)
        return render.mainPage()
    

#deal appoint
class deal:
    def GET(self,data):
        if session.get('logged_in'):
            pid=str(session.get('pid'))
            today=str(datetime.date.today())
            sql='select * from appoint where pid='+pid+''
            resultList = list(db.query(sql) )
            if resultList:
                raise web.seeother('/NewAppoint')
            else:
                sql='update doctor set status=1 where did=\''+data+'\''
                db.query(sql)
                sql='insert into appoint values('+pid+',\''+data+'\',\''+today+'\')'
                db.query(sql)
                raise web.seeother('/window1')
        return render.mainPage()

# Register success
class window2:
    def GET(self):
        sql='select * from patient order by pid desc limit 1'
        resultList = list(db.query(sql) )
        return render.window2(resultList)
    

#appoint success
class window1:
    def GET(self):
        if session.get('logged_in'):
            pid=str(session.get('pid'))
            sql='select * from appoint natural join doctor where pid='+pid+''
            resultList = list(db.query(sql) )
            return render.window1(resultList)
        return render.mainPage()

class window3:
    def GET(self):
        if session.get('logged_in'):
            pid=str(session.get('pid'))
            sql='select * from doctor natural join appoint where pid='+pid+''
            getResult = list(db.query(sql) )
            return render.window3(getResult)
        return render.mainPage()

class window4:
    def GET(self):
        return render.window4

# doctor record
class doctorRecord:
    def GET(self):
        if session.get('logged_in'):
            i = web.input()
            pid=str(i.get('pid'))
            if pid=='None':
                sql='select * from medical_record where pid=0'
                resultList = list(db.query(sql) )
            else:
                sql='select * from medical_record where pid='+pid+''
                resultList = list(db.query(sql) )
            return render.doctorRecord(resultList)
        return render.login2()




#patient new appointment
class NewAppoint:
    def GET(self):
        if session.get('logged_in'):
            i = web.input()
            d = web.data()
            did=str(i.get('did'))
            pid=str(session.get('pid'))
            sql='select * from appoint where pid='+pid+''
            resultList = list(db.query(sql) )
            if resultList:
                raise web.seeother('/window3')
            elif did!='None':
                sql='select * from doctor where did=\''+did+'\''
                resultList = list(db.query(sql) )
                return render.NewAppoint(resultList)
            
            else:
                sql='select * from doctor limit 7'
                resultList = list(db.query(sql) ) 
                return render.NewAppoint(resultList)

        return render.login()


# doctor appointment
class doctorAppoint:
    def GET(self):
        if session.get('logged_in'):
            did=str(session.get('did'))
            sql='select * from appoint natural join patient where did=\''+did+'\''
            resultList = list(db.query(sql) ) 
            return render.doctorAppoint(resultList)
        return render.mainPage()

    




               
#deal doctor
class dealDoctor:
    def GET(self):
        if session.get('logged_in'):
            did=str(session.get('did'))
            sql='update doctor set status=0 where did=\''+did+'\''
            db.query(sql)
            sql='delete from appoint where did=\''+did+'\''
            db.query(sql)
            raise web.seeother('/doctorAppoint')
        return render.mainPage()


# Hash code
def md5(s):
    if isinstance(s, str):
        m = hashlib.md5()   
        m.update(s.encode('utf-8'))
        return m.hexdigest()
    else:
        return ''
#Run
if __name__ == "__main__":
    app.run()
