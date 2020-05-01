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
		sql="SELECT p.origin, p.no, p.title, p.address FROM PROBLEM p, PROBLEM_DATE pd WHERE p.origin = pd.origin AND p.no = pd.no ORDER BY pd.date ASC"
		cursor.execute(sql)
		problem=[]
		for result in cursor.fetchall():
			problem.append({
				"origin":result['origin'],
				"no":result['no'],
				"title":result['title'],
				"address":result['address']
			})
		print(problem)
		return render_template('list.html', problem = problem)
	else:
		search = request.form['search']
		search = '%'+search+'%'
		if request.form['searchtype']=='name': 
			sql="SELECT u.class, p.origin, p.no, p.title, u.name FROM USER u, SOLVE s, PROBLEM p WHERE u.name LIKE '%s' AND u.id = s.id AND s.origin = p.origin AND s.no = p.no"%(search)
			cursor.execute(sql)
			list=[]
			for result in cursor.fetchall():
				list.append({
					"class":result['class'],
					"origin":result['origin'],
					"no":result['no'],
					"title":result['title'],
					"name":result['name']
				})
			return render_template('whoSolved.html',list=list)
		else:
			sql="SELECT u.class, p.origin, p.no, p.title, u.name FROM USER u, SOLVE s, PROBLEM p WHERE p.title LIKE '%s' AND s.origin = p.origin AND s.no = p.no AND s.id = u.id"%(search)
			cursor.execute(sql)
			list=[]
			for result in cursor.fetchall():
				list.append({
					"class":result['class'],
					"origin":result['origin'],
					"no":result['no'],
					"title":result['title'],
					"name":result['name']
				})
			return render_template('whoSolved.html', list=list)

@app.route('/whosolved', methods=['GET','POST'])
def whosolved():
	if request.form == 'GET':
		#origin = request.form['origin']
		#no = request.form['no']
		my = request.form['my']
		print("my : " + my)
		sql = "SELECT u.class, p.origin, p.no, p.title, u.name FROM USER u, SOLVE s, PROBLEM p WHERE s.origin = '%s' AND s.no = '%s' AND s.id = u.id AND s.origin = p.origin AND s.no = p.no"%(origin, no)
		cursor.execute(sql)
		list=[]
		for result in cursor.fetchall():
			list.append({
					"class":result['class'],
					"origin":result['origin'],
					"no":result['no'],
					"title":result['title'],
					"name":result['name']
				})
			return render_template('whoSolved.html', list=list)

@app.route('/write', methods=['GET','POST'])
def write():
	"""write code"""
	if request.method == 'GET':
		return render_template('write.html')
	else:
		title = request.form['title']
		code = request.form['code']

@app.route('/add_prob', methods=['GET', 'POST'])
def add_prob():
	"""add problem"""
	if request.method == 'GET':
		return render_template('table_2.html')
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
			print(i)
			sql = "INSERT INTO GIVE(class,origin,no) VALUES (%s,%s,%s)"
			value = (clas, origin[i], no[i])
			cursor.execute(sql,value)

		 
			sql2 = "INSERT INTO PROBLEM(origin,no,title,address) VALUES (%s,%s,%s,%s)"
			value = (origin[i], no[i],title[i],address[i])
			cursor.execute(sql2,value)
	
			date = datetime.today()
		
			sql = "INSERT INTO PROBLEM_DATE(origin,no,date) VALUES (%s,%s,%s)"
			value = (origin[i], no[i],date)
			cursor.execute(sql,value)
			
			conn.commit()
		
		return redirect(url_for('solve'))	

@app.route('/add_code', methods=['GET','POST'])
def add_code():
	if request.method == 'GET':
		return render_template('write.html')

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0',port=1024,debug=True)
