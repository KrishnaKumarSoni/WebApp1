from flask import Flask, render_template, request, flash, redirect, url_for, session, g
import pymysql
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'my_key_is_my_key_none_of_your_key'


@app.route('/')
def landing():
	return redirect(url_for('login'))

@app.route('/login')
def loginuser():
	return render_template('login.html')

@app.route('/login',methods=['GET', 'POST'])
def login():
	connection = pymysql.connect(host="localhost", user="root", password="", db='abcd',
								   charset='utf8mb4',
								   cursorclass=pymysql.cursors.DictCursor)
	cursor = connection.cursor()
	if request.method == 'POST':
		
		session.pop('user', None)

		user = request.form
		g.username = user['username']
		username = user['username']
		enteredPassword = user['password']

		query = "SELECT password FROM userinfo WHERE username=%s"
		cur = cursor.execute(query, (username))

		if cur:
			try:
				password = cursor.fetchone()
				connection.commit()
			finally:
				connection.close()
		
			if enteredPassword == password['password']:
				session['user'] = username
				return redirect(url_for('homepage'))
			else:
				flash('you entered in the secret zone!')
				return redirect(url_for('login'))		

		else:
			flash('you entered wrong username/password')
			return redirect(url_for('login'))

@app.before_request
def before_request():
	g.user = None
	if 'user' in session:
		g.user = session['user']

@app.route('/logout')
def logout():
	return redirect(url_for('login'))

@app.route('/signup')
def signup():
	return render_template('signup.html')

@app.route('/signup', methods=['GET', 'POST'])
def registerUser():
	connection = pymysql.connect(host="localhost", user="root", password="", db='abcd',
								   charset='utf8mb4',
								   cursorclass=pymysql.cursors.DictCursor)
	cursor = connection.cursor()

	if request.method == 'POST':
		user = request.form
		name = user['name']
		username = user['username']
		password = user['password']
		email = user['emailid']
		phonenumber = user['phonenumber']
		confirmPassword = user['confirmPassword']

		if username:
			query = "SELECT password FROM userinfo WHERE username=%s"
			cur = cursor.execute(query, (username))
			
			if cur:
				flash('username already exists')
				return redirect(url_for('registerUser'))
			else:

				if confirmPassword == password:	
					try:
						query = "INSERT INTO userinfo (name, username, email, phonenumber, password) VALUES (%s, %s, %s, %s, %s)"
						cursor.execute(query, (name, username, email, phonenumber, password))
						connection.commit()
					finally:
						connection.close()
					return redirect(url_for('login'))
				else:
					flash("Passwords do not match!")
					return redirect(url_for('registerUser'))
	else:
		return "error"


@app.route('/index')
def index():
	if g.user:
		return render_template('index.html')
	return redirect(url_for('loginuser'))

@app.route('/myaccount')
def myaccount():
	if g.user:
		username=g.user
		connection = pymysql.connect(host="localhost", user="root", password="", db='abcd',
									   charset='utf8mb4',
									   cursorclass=pymysql.cursors.DictCursor)
		cursor = connection.cursor()

		query = 'SELECT * FROM userinfo WHERE username=%s'
		cursor.execute(query, (username))
		useraccount=cursor.fetchmany(6)

		emailid = useraccount[0]['email']
		phonenumber = useraccount[0]['phonenumber']
		name = useraccount[0]['name']
		connection.commit()

		return render_template('myAccount.html', username = username, phonenumber = phonenumber, emailid = emailid, name = name)


	else:
		return redirect(url_for('login'))	


@app.route('/editaccounts', methods=['GET', 'POST'])
def editaccounts():
	if g.user:
		username = g.user
		connection = pymysql.connect(host="localhost", user="root", password="", db='abcd',
									   charset='utf8mb4',
									   cursorclass=pymysql.cursors.DictCursor)
		cursor = connection.cursor()

		query = 'SELECT * FROM userinfo WHERE username=%s'
		cursor.execute(query, (username))
		useraccount=cursor.fetchmany(6)
		connection.commit()

		name = useraccount[0]['name']
		userid = useraccount[0]['userid']

		if request.method == 'POST':

			newemail = request.form['emailid']
			newphonenumber = request.form['phonenumber']
			query = 'UPDATE userinfo SET email=%s, phonenumber=%s WHERE username=%s'
			cursor.execute(query, (newemail, newphonenumber, username))
			connection.commit()
			return redirect(url_for('myaccount'))
		return render_template('editaccounts.html', username=username, name=name)

@app.route('/homepage')
def homepage():
	return render_template('homepage.html')

@app.route('/sellitem', methods=['GET', 'POST'])
def sellitem():
	if g.user:

		if request.method=='POST':
			username = g.user			
			#getting user details
			connection = pymysql.connect(host="localhost", user="root", password="", db='abcd',
									   charset='utf8mb4',
									   cursorclass=pymysql.cursors.DictCursor)
			cursor = connection.cursor()
			query = 'SELECT * FROM userinfo WHERE username=%s'
			cursor.execute(query, (username))
			useraccount=cursor.fetchmany(6)
			connection.commit()

			phonenumber = useraccount[0]['phonenumber'] 

			item=request.form
			itemname=item['itemname']
			itemdetails=item['itemdetails']
			price=item['price']
			city=item['city']
			state=item['state']
			catagory=item['catagory']
			query1='INSERT INTO ' + str(catagory) + '(username, phonenumber, itemname, itemdetails, city, state, price) VALUES(%s, %s, %s, %s, %s, %s, %s)'
			print(query1)
			cursor.execute(query1, (username, phonenumber, itemname, itemdetails, city, state, price))
			connection.commit()
			connection.close()
			return redirect(url_for('homepage'))

		return render_template('sellitem.html')


	else:
		return redirect(url_for('login'))


@app.route('/createcabshare', methods=['GET', 'POST'])
def createcabshare():
	if g.user:
		connection = pymysql.connect(host="localhost", user="root", password="", db='abcd',
								   charset='utf8mb4',
								   cursorclass=pymysql.cursors.DictCursor)
		cursor = connection.cursor()
		query = 'SELECT cities FROM city_dropdown'
		cursor.execute(query)
		cities = cursor.fetchall()
		connection.commit()

		if request.method=='POST':
			journeydate=request.form['date']
			time=request.form['time']
			leavingfrom=request.form['leavingfrom']
			goingto=request.form['goingto']
			emptyseats=request.form['numberofseats']
			
			journeydatestring=datetime.strptime(journeydate, "%Y-%m-%d")

			query1='INSERT INTO cabsharing(journeydate, goingto, numberofseats) VALUES ('+ +'"%s", %s, %s)'
			cursor.execute(query1, (journeydatestring, goingto, emptyseats))
			connection.commit()	
			return redirect('homepage')
		
		return render_template('createcabshare.html', cities=cities)

@app.route('/cabsharesearch', methods=['GET', 'POST'])
def cabsharesearch():
	if g.user:
		connection = pymysql.connect(host="localhost", user="root", password="", db='abcd',
								   charset='utf8mb4',
								   cursorclass=pymysql.cursors.DictCursor)
		cursor = connection.cursor()
		query = 'SELECT cities FROM city_dropdown'
		cursor.execute(query)
		cities = cursor.fetchall()
		connection.commit()

		if request.method=='POST':
			journeydate=request.form['date']
			time=request.form['time']
			leavingfrom=request.form['leavingfrom']
			goingto=request.form['goingto']

			query1='SELECT * FROM cabsharing WHERE journeydate=' + journeydate
			cursor.execute(query1)
			connection.commit()
			result = cursor.fetchall()
			print(result)

		return render_template('cabsharing.html', cities=cities)

	else:
		return redirect(url_for('login'))

@app.route('/vehicles')
def vehicles():
	if g.user:
		connection = pymysql.connect(host="localhost", user="root", password="", db='abcd',
								   charset='utf8mb4',
								   cursorclass=pymysql.cursors.DictCursor)
		cursor = connection.cursor()
		
		query='SELECT COUNT(*) FROM vehicles'
		cursor.execute("SELECT COUNT(*) FROM vehicles")
		connection.commit()
		result=cursor.fetchone()
		print(result[0])
		return "1"


	else:
		return redirect('login')	
if __name__ == "__main__":
	app.run(debug=True)			 
