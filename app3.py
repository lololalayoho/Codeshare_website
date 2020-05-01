#-*- coding:utf-8 -*-
from flask import Flask, url_for, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import pymysql

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
	if not session.get('logged_in'):
		return render_template('main_2.html')

	else:
		if request.method == 'POST':
			username = getname(request.form['username'])
			return render_template('main_2.html', data=getfollowedby(username))


@app.route('/login', methods=['GET', 'POST'])
def login():
	"""Login Form"""
	if request.method == 'GET':
		return render_template('login.html')

	else:
		id = request.form['id']
		sql="SELECT id FROM USER WHERE id='%s'"%(id)
		cursor.execute(sql)
		result=cursor.fetchall()
		print(result)
		if result:
			session['logged_in'] = True
			return redirect(url_for('home'))
		else:
			return '스터디원이 아닙니다.'

@app.route("/logout")
def logout():
	"""Logout Form"""
	session['logged_in'] = False
	return redirect(url_for('home'))


if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0',port=1024,debug=True)
	
