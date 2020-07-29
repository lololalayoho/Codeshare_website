#-*- coding:utf-8 -*-
from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import pymysql
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'app secret key'
conn = pymysql.connect(
	host='localhost',
	user='root',
	password='long',
	db='LONGLONG',
	charset='utf8',
	cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()
'''
class User(db.Model):
	""" Create user table"""
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	password = db.Column(db.String(80))

	def __init__(self, username, password):
		self.username = username
		self.password = password
'''

@app.route('/', methods=['GET', 'POST'])
def home():
	sql="SELECT name FROM USER"
	cursor.execute(sql)
	member=[]
	for result in cursor.fetchall():
		member.append({
			"name":result['name']
		})

	
	return render_template('main_2.html',member=member)

	""" Session control"""
	if not session.get('id'):
		return render_template('main_2.html',member=member)

	else:
		if request.method == 'POST':
			username = getname(request.form['username'])
			return render_template('main_2.html', data=getfollowedby(username),member=member)


@app.route('/login', methods=['GET', 'POST'])
def login():
	"""Login Form"""
	if request.method == 'GET':
		return render_template('login.html')

	else:
		id = request.form['id']
		passwd = request.form['passwd']
		sql="SELECT id FROM USER WHERE id='%s'"%(id)
		cursor.execute(sql)
		result = cursor.fetchall()
		if result:
			sql="SELECT id, class FROM USER WHERE id='%s' AND passwd='%s'"%(id, passwd)
			cursor.execute(sql)
			login = cursor.fetchone()
			if login:
				session['id'] = login['id']
				session['class'] = login['class']
				return redirect(url_for('button'))
			else:
				return '비밀번호가 틀렸습니다.'
		else:
			return '스터디원이 아닙니다.'

@app.route('/button',methods=['GET'])
def button():
	return render_template('button.html')

@app.route('/solve', methods=['GET', 'POST'])
def solve():
	"""solve form"""
	if request.method == 'GET':
		sql="SELECT g.class, p.origin, p.no, p.title, p.address FROM GIVE g, PROBLEM p WHERE g.origin=p.origin AND g.no=p.no AND class = 1"
		cursor.execute(sql)
		week1=[]
		for result in cursor.fetchall():
			week1.append({
				"class":result['class'],
				"origin":result['origin'],
				"no":result['no'],
				"title":result['title'],
				"address":result['address']
			})
		sql="SELECT g.class, p.origin, p.no, p.title, p.address FROM GIVE g, PROBLEM p WHERE g.origin=p.origin AND g.no=p.no AND class = 2"
		cursor.execute(sql)
		week2=[]
		for result in cursor.fetchall():
			week2.append({
				"class":result['class'],
				"origin":result['origin'],
				"no":result['no'],
				"title":result['title'],
				"address":result['address']
			})

		return render_template('week.html',week1 = week1, week2 = week2) 

@app.route('/solved',methods=['GET','POST'])
def solved():
	if request.method == 'GET':
		sql="SELECT p.origin, p.no, p.title, p.address FROM PROBLEM p, PROBLEM_DATE pd WHERE p.origin = pd.origin AND p.no = pd.no ORDER BY pd.date DESC"
		cursor.execute(sql)
		problem=[]
		for result in cursor.fetchall():
			problem.append({
				"origin":result['origin'],
				"no":result['no'],
				"title":result['title'],
				"address":result['address']
			})
		return render_template('list.html', problem = problem)
	else:
		search = request.form['search']
		search = '%'+search+'%'
		if request.form['searchtype']=='name': 
			sql="SELECT s.date, u.id, u.class, p.origin, p.no, p.title, u.name FROM USER u, SOLVE s, PROBLEM p WHERE u.name LIKE '%s' AND u.id = s.id AND s.origin = p.origin AND s.no = p.no ORDER BY date DESC"%(search)
			cursor.execute(sql)
			list=[]
			for result in cursor.fetchall():
				list.append({
					"date":result['date'],
					"class":result['class'],
					"origin":result['origin'],
					"no":result['no'],
					"title":result['title'],
					"name":result['name'],
					"id":result['id']
					
				})
			return render_template('search.html',list=list)
		else:
			sql="SELECT s.date, u.id, u.class, p.origin, p.no, p.title, u.name FROM USER u, SOLVE s, PROBLEM p WHERE p.title LIKE '%s' AND s.origin = p.origin AND s.no = p.no AND s.id = u.id ORDER BY date DESC"%(search)
			cursor.execute(sql)
			list=[]
			for result in cursor.fetchall():
				list.append({
					"date":result['date'],
					"class":result['class'],
					"origin":result['origin'],
					"no":result['no'],
					"title":result['title'],
					"name":result['name'],
					"id":result['id']
				})
			return render_template('search.html', list=list)

@app.route('/read_code',methods=['GET','POST'])
def read_code():
	if request.method == 'POST':
		origin = request.form['origin']
		no = request.form['no']
		id = request.form['id']
		date = request.form['date']
		sql = "select title from PROBLEM WHERE no='%s' AND origin='%s'"%(no,origin)
		cursor.execute(sql)
		title=cursor.fetchone()
		sql = "select code from SOLVE where origin=%s and no=%s and id = %s and date = %s" 
		me = 0
		if int(id) == session['id']:
			me = 1	
		value = (origin,no,id,date)
		cursor.execute(sql,value)
		result = cursor.fetchone()
		data=[]
		data.append({
			"title":title,
			"code":result['code'],
			"date":date,
			"origin":origin,
			"no":no,
		})
		
		return render_template('read.html', data = data, me = me)

@app.route('/whosolved', methods=['GET','POST'])
def whosolved():
	if request.method == 'POST':
		origin = request.form['origin']
		no = request.form['no']
		sql = "SELECT p.no, p.origin, p.title FROM PROBLEM p, SOLVE s WHERE p.no = '%s' AND p.origin = '%s' AND p.no = s.no AND p.origin = s.origin"%(no, origin)
		cursor.execute(sql)
		result = cursor.fetchall()
		if result:
			sql = "SELECT u.id, s.date, p.origin, p.no, p.title, u.name FROM USER u, SOLVE s, PROBLEM p WHERE s.origin = '%s' AND s.no = '%s' AND s.id = u.id AND s.origin = p.origin AND s.no = p.no ORDER BY s.date DESC"%(origin, no)
			cursor.execute(sql)
			list=[]
			for result in cursor.fetchall():
				list.append({
						"date":result['date'],
						"origin":result['origin'],
						"no":result['no'],
						"title":result['title'],
						"name":result['name'],
						"id":result['id']
					})
			return render_template('whoSolved.html', list=list)
		else:
			sql="SELECT title FROM PROBLEM WHERE no = '%s' AND origin = '%s'"%(no, origin)
			cursor.execute(sql)
			result = cursor.fetchall()
			list1=[]
			list1.append({
				"no":no,
				"origin":origin,
				"title":result[0]['title']
			})
			return render_template('whoSolved.html', list1=list1)

@app.route('/write', methods=['GET','POST'])
def write():
	"""write code"""
	if request.method == 'GET':
		return render_template('write.html')
	else:
		origin = request.form['origin']
		no = request.form['no']
		title = request.form['title']
		problem=[]
		problem.append({
			"title":title,
			"no":no,
			"origin":origin
		})
		return render_template('write.html',problem=problem)
		

@app.route('/add_prob', methods=['GET', 'POST'])
def add_prob():
	"""add problem"""
	if request.method == 'GET':
		return render_template('give_table.html')
	else:
		clas = request.form['checkbox1[]']
		sql="DELETE FROM GIVE WHERE class='%s'"%(clas)
		cursor.execute(sql)
		conn.commit()
			
		origin = request.form.getlist('origin[]')
		no = request.form.getlist('no[]')
		title = request.form.getlist('title[]')
		address = request.form.getlist('address[]')
			
		for i, name in enumerate(origin):
			sql = "INSERT INTO GIVE(class,origin,no) VALUES (%s,%s,%s)"
			value = (clas, origin[i], no[i])
			cursor.execute(sql,value)

		 
			sql2 = "INSERT INTO PROBLEM(origin,no,title,address) SELECT %s, %s, %s, %s FROM DUAL WHERE NOT EXISTS (SELECT * FROM PROBLEM WHERE no = %s AND origin = %s)"
			value = (origin[i], no[i], title[i], address[i], no[i], origin[i])
			cursor.execute(sql2,value)
	
			date = datetime.today()
		
			sql = "INSERT INTO PROBLEM_DATE(origin,no,date) SELECT %s, %s, %s FROM DUAL WHERE NOT EXISTS (SELECT * FROM PROBLEM_DATE WHERE origin = %s AND no = %s)"
			value = (origin[i], no[i], date, origin[i], no[i])
			cursor.execute(sql,value)
			
			conn.commit()
		
		return redirect(url_for('solve'))	

@app.route('/add_code', methods=['GET','POST'])
def add_code():
	if request.method == 'GET':
		return render_template('write.html')
	else:
		origin = request.form['origin']
		no = request.form['no']
		id = int(session['id'])
		code = request.form['solve_code']
		date = datetime.today()
		sql="INSERT INTO SOLVE (id, origin, no, code, date) VALUES ('%s', '%s', '%s', '%s', '%s')"%(id, origin, no, code, date)
		cursor.execute(sql)
		conn.commit()	
		return redirect(url_for('solved'))

@app.route('/modify', methods=['POST'])
def modify():
	origin = request.form['origin']
	no = request.form['no']
	date = request.form['date']
	code = request.form['code']
	modi = []
	modi.append({
		"origin":origin,
		"no":no,
		"date":date,
		"code":code
	})
	return render_template('modify.html', modi = modi)

@app.route('/Delete',methods=['POST'])
def Delete_code():
	id = int(session['id'])
	origin = request.form['origin']
	no = request.form['no']
	sql = "DELETE FROM SOLVE WHERE id = '%s' AND origin = '%s' AND no = '%s'"%(id,origin,no)
	cursor.execute(sql)
	conn.commit()
	return redirect(url_for('solved'))
@app.route('/modify_code', methods=['POST'])
def modify_code():
	origin = request.form['origin']
	no = request.form['no']
	id = int(session['id'])
	code = request.form['solve_code']
	date = request.form['date']
	mdate = datetime.today()
	sql = "UPDATE SOLVE SET date = '%s', code = '%s' WHERE id = '%s' AND origin = '%s' AND no = '%s' AND date = '%s'"%(mdate, code, id, origin, no, date)
	cursor.execute(sql)
	conn.commit()
	return redirect(url_for('solved'))

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0',port=1024,debug=True)
