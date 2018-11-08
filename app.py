from flask import Flask, render_template, request, flash, redirect, url_for, session, g
import pymysql
from datetime import datetime
from datetime import timedelta
from flask_uploads import UploadSet, configure_uploads, IMAGES

app = Flask(__name__)
app.secret_key = 'my_key_is_my_key_none_of_your_key'

photos=UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'static/uploadedimages'
configure_uploads(app, photos)

@app.route('/')
def landing():
	return redirect(url_for('login'))

#----------------------------login---------------------------------------------
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
				flash('you entered wrong username/password')
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
	session.pop('user', None)
	return redirect(url_for('login'))

#----------------------------signup---------------------------------------------
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

#----------------------------index-----------------------------------
@app.route('/index')
def index():
	if g.user:
		return render_template('index.html')
	return redirect(url_for('loginuser'))

#-------------------------------myaccount----------------------------------
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

#-------------------------------myads---------------------------------------------------
@app.route('/myads', methods=['GET', 'POST'])
def myads():
	if g.user:
		connection = pymysql.connect(host="localhost", user="root", password="", db='abcd',
								   charset='utf8mb4',
								   cursorclass=pymysql.cursors.DictCursor)
		cursor = connection.cursor()
		query="SELECT * FROM solditems WHERE username='" + g.user + "'"
		cursor.execute(query)
		connection.commit()
		result=cursor.fetchall()

		if request.method=='POST':
			primarykey=request.form['primarykey']
			query1='DELETE FROM solditems WHERE primarykey=' + str(primarykey)
			cursor.execute(query1)
			connection.commit()

			return redirect(url_for('myads'))

		return render_template('myads.html', result=result)

	else:
		flash('please login first')
		return redirect(url_for('login'))

#------------------------------my cab shares----------------------------------------------
@app.route('/mycabshares', methods=['GET', 'POST'])
def mycabshares():
	if g.user:
		connection = pymysql.connect(host="localhost", user="root", password="", db='abcd',
								   charset='utf8mb4',
								   cursorclass=pymysql.cursors.DictCursor)
		cursor = connection.cursor()

		query="SELECT * FROM cabsharing WHERE username='" + g.user + "'"
		cursor.execute(query)
		result=cursor.fetchall()
		connection.commit()

		if request.method=='POST':
			if request.form['seats'].find('add') != -1:
				print(request.form['seats'].find('add'))
				cabnumber = request.form['seats'].split("_")
				query2="UPDATE cabsharing SET numberofseats = numberofseats + 1 WHERE cabnumber='" + cabnumber[0] + "'"
				cursor.execute(query2)
				connection.commit()

			elif request.form['seats'].find('subtract') != -1:
				cabnumber = request.form['seats'].split("_")
				query2="UPDATE cabsharing SET numberofseats = numberofseats - 1 WHERE cabnumber='" + cabnumber[0] + "'"
				cursor.execute(query2)
				connection.commit()
			return redirect(url_for('mycabshares'))

		return render_template('mycabshares.html', result=result)

	else:
		flash('login first')
		return redirect(url_for('login'))

#-----------------------------------edit account-----------------------------------------
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

@app.route('/homepage', methods=['GET', 'POST'])
def homepage():
	if g.user:
		if request.method=='POST':
			catagory=request.form['catagoryselection']
			if catagory != 'Category':
				return redirect(url_for('feed', catagory=catagory))
			else:
				return redirect(url_for('homepage'))
		return render_template('homepage.html')
	else:
		flash("please login")
		return redirect(url_for('login'))

#--------------------------------selling an item------------------------

@app.route('/sellitem', methods=['GET', 'POST'])
def sellitem():
	if g.user:
		connection = pymysql.connect(host="localhost", user="root", password="", db='abcd',
								   charset='utf8mb4',
								   cursorclass=pymysql.cursors.DictCursor)
		cursor = connection.cursor()
		query = 'SELECT cities FROM city_dropdown'
		cursor.execute(query)
		cities = cursor.fetchall()
		connection.commit()
		
		if request.method=='POST' and 'photo' in request.files:
			username = g.user			
			query = 'SELECT * FROM userinfo WHERE username=%s'
			cursor.execute(query, (username))
			useraccount=cursor.fetchmany(6)
			connection.commit()

			phonenumber = useraccount[0]['phonenumber'] 
			name=useraccount[0]['name']
			item=request.form
			itemname=item['itemname']
			itemdetails=item['itemdetails']
			price=item['price']
			city=item['city']
			state=item['state']
			catagory=item['catagory']
				
			filename=photos.save(request.files['photo'])
			imagepath="uploadedimages/" + filename

			query1='INSERT INTO solditems(username, name, phonenumber, itemname, itemdetails, city, state, price, catagory, imagepath) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
			cursor.execute(query1, (username, name, phonenumber, itemname, itemdetails, city, state, price, catagory, imagepath))
			connection.commit()
			connection.close()
			return redirect(url_for('homepage'))

		return render_template('sellitem.html', cities=cities)


	else:
		return redirect(url_for('login'))

#-------------------------------------item feed-------------------------------------------
@app.route('/feed', methods=['GET', 'POST'])
def feed():
	if g.user:
		connection = pymysql.connect(host="localhost", user="root", password="", db='abcd',
								   charset='utf8mb4',
								   cursorclass=pymysql.cursors.DictCursor)
		cursor = connection.cursor()

		catagory=request.args.get('catagory')	
		title=catagory
		query="SELECT * FROM solditems WHERE catagory = '" + catagory.lower() +  "'"
		cursor.execute(query)
		connection.commit()
		result = cursor.fetchall()

		if request.method=='POST':
			key=request.form['key']
			return redirect(url_for('item', key=key))
		return render_template('catagoryfeed.html', title=title, result=result)
	else:
		flash('please Login first')
		return redirect(url_for('login'))

#----------------------------------------item---------------------------------------------
@app.route('/item')
def item():
	if g.user:
		primarykey=request.args.get('key')
		connection = pymysql.connect(host="localhost", user="root", password="", db='abcd',
								   charset='utf8mb4',
								   cursorclass=pymysql.cursors.DictCursor)
		cursor = connection.cursor()
		query="SELECT * FROM solditems WHERE primarykey=" + str(primarykey)
		cursor.execute(query)
		connection.commit()
		result=cursor.fetchall()

		return render_template('item.html', result=result)
		
	else:
		flash('please Login first')
		return redirect(url_for('login'))

#--------------------------create cabshare-----------------------------------------
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

		query2 = "SELECT name, phonenumber FROM userinfo WHERE username='" + username + "'"
		cursor.execute(query2)
		userdetails=cursor.fetchall()
		connection.commit()

		if request.method=='POST':
			journeydate=request.form['date']
			journeytime=request.form['time']
			leavingfrom=request.form['leavingfrom']
			goingto=request.form['goingto']
			emptyseats=request.form['numberofseats']
			name=userdetails[0]['name']
			phonenumber=userdetails[0]['phonenumber']

			if leavingfrom != goingto: 
				query='INSERT INTO cabsharing(username, phonenumber, name, journeydate, journeytime, goingto, leavingfrom, numberofseats) VALUES(%s, %s, %s, %s, %s, %s)'
				cursor.execute(query, (g.user, name, phonenumber, journeydate, journeytime, goingto, leavingfrom, emptyseats))
				connection.commit()	
				return redirect('homepage')
			else:
				flash("source and destination can't be same")
				return redirect(url_for('createcabshare'))
		return render_template('createcabshare.html', cities=cities)

#-------------------------------------search a cab----------------------------------------
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
			
			if leavingfrom != goingto:
				flash("source and destination can't be same")

				query1="SELECT * FROM cabsharing WHERE journeydate='" + journeydate + "'"
				cursor.execute(query1)
				connection.commit()
				result = cursor.fetchall()

				print(result)
				result_final=[]
				for i in result:
					journeytime = i['journeytime']
					journeytime = str(journeytime)
					journeytime_time = datetime.strptime(journeydate+ ' ' +journeytime, '%Y-%m-%d %H:%M:%S')
					time_time = datetime.strptime(journeydate+ ' ' + time , '%Y-%m-%d %H:%M')
					timediff = abs(journeytime_time - time_time)
				
					if timediff.seconds <= 3600:
						result_final.append(i)

				if result:
					return render_template('searchresult.html', result=result_final)
				else: 
					flash('No cabs available. Make a share yourself!')
					return redirect(url_for('createcabshare'))
			else: 
				flash("source and destination can't be same")
				return redirect(url_for('cabsharesearch'))
		return render_template('cabsharing.html', cities=cities)

	else:
		return redirect(url_for('login'))

 
if __name__ == "__main__":
	app.run(debug=True)			 
