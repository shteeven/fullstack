__author__ = 'Shtav'
from flask import Flask, render_template, request, redirect, jsonify, url_for, \
	flash, make_response
from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker, exc
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
	open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

default_img_url = 'http://orig04.deviantart.net/fa85/f/2012/296/8/7/random_funny___2_by_guppy22-d5irouc.jpg'


# Create anti-forgery state token
@app.route('/login')
def showLogin():
	state = generateRandomString()
	login_session['state'] = state
	# return "The current session state is %s" % login_session['state']
	return render_template('login.html', STATE=state, client_id=CLIENT_ID)


@app.route('/gconnect', methods=['POST'])
def gconnect():
	# Validate state token
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Obtain authorization code, now compatible with Python3
	# request.get_data()
	code = request.data.decode('utf-8')

	try:
		# Upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(
			json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Check that the access token is valid.
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
	       % access_token)
	# Submit request, parse response - Python3 compatible
	h = httplib2.Http()
	response = h.request(url, 'GET')[1]
	str_response = response.decode('utf-8')
	result = json.loads(str_response)

	# If there was an error in the access token info, abort.
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'

	# Verify that the access token is used for the intended user.
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(
			json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is valid for this app.
	if result['issued_to'] != CLIENT_ID:
		response = make_response(
			json.dumps("Token's client ID does not match app's."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_access_token = login_session.get('access_token')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_access_token is not None and gplus_id == stored_gplus_id:
		login_session['access_token'] = access_token
		response = make_response(
			json.dumps('Current user is already connected.'),
			200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Store the access token in the session for later use.
	login_session['provider'] = 'google'
	login_session['access_token'] = access_token
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']

	# see if user exists, if it doesn't make a new one
	user_id = getUserID(login_session['email'])
	if not user_id:
		user_id = createUser(login_session)
	login_session['user_id'] = user_id

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
	# Only disconnect a connected user.
	access_token = login_session.get('access_token')
	if access_token is None:
		response = make_response(
			json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	if result['status'] == '200':
		# Reset the user's sesson.
		return result
	else:
		# For whatever reason, the given token was invalid.
		response = make_response(
			json.dumps('Failed to revoke token for given user.', 400))
		response.headers['Content-Type'] = 'application/json'
		return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
	# Validate state token
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	access_token = request.data

	app_object = json.loads(open('facebook_client_secrets.json', 'r').read())[
		'web']
	app_id = app_object['app_id']
	app_secret = app_object['app_secret']

	url = 'https://graph.facebook.com/oauth/access_token?' \
	      'grant_type=fb_exchange_token' \
	      '&client_id=%s' \
	      '&client_secret=%s' \
	      '&fb_exchange_token=%s' % (app_id, app_secret, access_token)
	h = httplib2.Http()
	result = h.request(url, 'GET')[1]

	userinfo_url = 'https://graph.facebook.com/v2.4/me'
	token = result.split("&")[0]

	url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
	h = httplib2.Http()
	result = h.request(url, 'GET')[1]
	data = json.loads(result)  #### ERROR ####
	login_session['provider'] = 'facebook'
	login_session['username'] = data['name']
	login_session['email'] = data['email']
	login_session['facebook_id'] = data['id']

	# get user's picture
	url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
	h = httplib2.Http()
	result = h.request(url, 'GET')[1]
	data = json.loads(result)

	login_session['picture'] = data['data']['url']

	# see if user exists, if it doesn't make a new one
	user_id = getUserID(login_session['email'])
	if not user_id:
		user_id = createUser(login_session)
	login_session['user_id'] = user_id

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	return output


@app.route('/fbdisconnect')
def fbdisconnect():
	facebook_id = login_session['facebook_id']
	url = 'https://graph.facebook.com/%s/permissions' % facebook_id
	h = httplib2.Http()
	result = h.request(url, 'DELETE')[1]
	return result


@app.route('/disconnect')
def disconnect():
	if 'provider' in login_session:
		if login_session['provider'] == 'google':
			gdisconnect()
			del login_session['gplus_id']
			del login_session['access_token']
		if login_session['provider'] == 'facebook':
			fbdisconnect()
			del login_session['facebook_id']

		del login_session['username']
		del login_session['email']
		del login_session['picture']
		del login_session['user_id']
		del login_session['provider']
		flash('Successfully logged out.')
		return redirect(url_for('showCategories'))
	else:
		flash("You were never logged in!")
		return redirect(url_for('showCategories'))


# User Helper Functions
def createUser(login_session):
	newUser = User(name=login_session['username'], email=login_session[
		'email'], picture=login_session['picture'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email=login_session['email']).one()
	return user.id


def getUserInfo(user_id):
	user = session.query(User).filter_by(id=user_id).one()
	return user


def getUserID(email):
	try:
		user = session.query(User).filter_by(email=email).one()
		return user.id
	except:
		flash("Failed to retrieve user ID.")
		return None


# validate image urls
def validateImageUrl(img_url):
	# if user does not include an image url
	if img_url == '':
		return 200, default_img_url
	# if user includes img, check if valid.
	else:
		try:
			r = requests.get(img_url)
			return r.status_code, img_url
		except requests.exceptions.MissingSchema:
			flash('Image url is an invalid schema. Enter an actual url or leave the field blank.')
			return '400', ''
		except requests.exceptions.InvalidSchema:
			flash('Image url is missing schema. Perhaps an preceding "http://" would fix it, or leave the field blank.')
			return '400', ''


# Check name field; if empty, return false
def validateName(name):
	if name == '':
		flash('Name field must be filled.')
	else:
		return True


# Check if user is signed in
def validateSignedIn():
	if 'username' not in login_session:
		flash('You must login to complete this action.')
		return False
	else:
		return True


# Prevent CSRFs with random tokens
# Code courtesy of Dan Jacobs: http://flask.pocoo.org/snippets/3/
@app.before_request
def csrf_protect():
	if request.method == "POST":
		token = login_session.pop('_csrf_token', None)
		if not token or token != request.form.get('_csrf_token'):
			flash('The request has been rejected and believed to be a cross-site request forgery. If this is not the '
			      'case, try to complete your actions without using the back or refresh button when filling forms.')
			return redirect(url_for('showCategories'))


def generateCsrfToken():
	if '_csrf_token' not in login_session:
		login_session['_csrf_token'] = generateRandomString()
	return login_session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generateCsrfToken


def generateRandomString():
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))


# JSON API to view Categories
@app.route('/category/JSON')
def categoryJSON():
	categories = session.query(Category).all()
	return jsonify(Category=[r.serialize for r in categories])


# JSON API to view Category items
@app.route('/category/<int:category_id>/item/JSON')
def categoryItemsJSON(category_id):
	# TODO: find out how this information is return and if the naming of the cat
	# should be included in the file sent back
	category = session.query(Category).filter_by(id=category_id).one()
	items = session.query(Item).filter_by(
		category_id=category_id).all()
	return jsonify(items=[i.serialize for i in items])


# JSON API to view a single Category item
@app.route('/category/<int:category_id>/item/<int:item_id>/JSON')
def itemJSON(category_id, item_id):
	item = session.query(Item).filter_by(id=item_id).one()
	print(item.serialize)
	return jsonify(item=item.serialize)


# RSS API to most recent items added
def make_external(url):
	return urljoin(request.url_root, url)


@app.route('/recent.atom')
def recentFeed():
	feed = AtomFeed('Recent Articles',
	                feed_url=request.url, url=request.url_root)
	try:
		items = session.query(Item).order_by(Item.timestamp).limit(15).all()
	except exc.NoResultFound:
		response = make_response(
			json.dumps('No items found. Please create some. %s' % url_for('/'),
			           400))
		response.headers['Content-Type'] = 'application/json'
		return response
	for item in items:
		creator = session.query(User).filter_by(id=item.user_id).one()
		feed.add(item.name, unicode(item.description),
		         content_type='html',
		         author=creator.name,
		         updated=item.timestamp,
		         url=make_external('category/' + str(item.category_id) +
		                           '/item/' + str(item.id) + '/'))
	return feed.get_response()


# Show all categories; page rendered differently depending on user login
@app.route('/')
@app.route('/category/')
def showCategories():
	categories = session.query(Category).order_by(asc(Category.name)).all()
	if 'username' not in login_session:
		return render_template('categories.html', categories=categories)
	else:
		return render_template('categories.html', categories=categories, logged='true')


# Create a new category; verify auth and redirect/render accordingly
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
	if not validateSignedIn():
		return redirect('/login')
	if request.method == 'POST':
		if validateName(request.form['name']):
			valid, img_url = validateImageUrl(request.form['img_url'])
			# Save new category.
			if valid == 200:
				newCategory = Category(name=request.form['name'], img_url=img_url, user_id=login_session['user_id'])
				session.add(newCategory)
				session.commit()
				flash('New Category %s Successfully Created' % newCategory.name)
				return redirect(url_for('showCategories'))
	return render_template('newCategory.html', logged='true')


# Edit a category; verify auth and redirect/render accordingly;
# Current user must match user_id of category
@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
	if not validateSignedIn():
		return redirect('/login')
	try:
		editedCategory = session.query(
			Category).filter_by(id=category_id).one()
	except exc.NoResultFound:
		flash("No results found for the category you wish to edit.")
		return redirect(url_for('showItems', category_id=category_id))
	if editedCategory.user_id != login_session['user_id']:
		flash('You are not authorized to edit this. Please create your own in order to edit.')
		return redirect(url_for('showItems', category_id=category_id))
	if request.method == 'POST':
		if validateName(request.form['name']):
			valid, img_url = validateImageUrl(request.form['img_url'])
			if valid == 200:
				editedCategory.name = request.form['name']
				editedCategory.img_url = img_url
				session.add(editedCategory)
				session.commit()
				flash('Category Successfully Edited %s' % editedCategory.name)
				return redirect(url_for('showItems', category_id=category_id))
	return render_template('editCategory.html', category=editedCategory, logged='true')


# Delete a category; verify auth and redirect/render accordingly;
# Current user must match user_id of category
@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
	try:
		categoryToDelete = session.query(Category).filter_by(
			id=category_id).one()
	except exc.NoResultFound:
		flash("No results found for the item you wish to delete.")
		return redirect(url_for('showItems', category_id=category_id))
	if 'username' not in login_session:
		return redirect('/login')
	if categoryToDelete.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not authorized to delete this category. Please create your own category in order to delete.');}</script><body onload='myFunction()''>"
	if request.method == 'POST':
		session.delete(categoryToDelete)
		flash('%s Successfully Deleted' % categoryToDelete.name)
		session.commit()
		return redirect(url_for('showCategories'))
	else:
		return render_template('deletecategory.html', category=categoryToDelete,
		                       logged='true')


# Show a category item; pages rendered differently depending on user login
@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/item/')
def showItems(category_id):
	try:
		category = session.query(Category).filter_by(id=category_id).one()
		creator = getUserInfo(category.user_id)
		items = session.query(Item).filter_by(
			category_id=category_id).all()
	except exc.NoResultFound:
		flash("The category you are trying to view does not exist.")
		return redirect(url_for('showCategories'))
	if 'username' not in login_session:
		return render_template('items.html', items=items,
		                       category=category, creator=creator)
	else:
		try:
			creator.is_user = creator.id == login_session['user_id']
			return render_template('items.html', items=items, category=category,
			                       creator=creator, logged='true')
		except AttributeError:
			return render_template('items.html', items=items, category=category,
			                       creator=creator, logged='true')


@app.route('/category/<int:category_id>/item/<int:item_id>/')
def showItem(item_id, category_id):
	try:
		item = session.query(Item).filter_by(
			id=item_id).one()
	except exc.NoResultFound:
		flash("The item you are trying to view does not exist.")
		return redirect(url_for('showItems', category_id=category_id))
	category = session.query(Category).filter_by(id=category_id).one()
	creator = getUserInfo(category.user_id)
	if 'username' not in login_session or creator.id != login_session[
		'user_id']:
		return render_template('item.html', item=item,
		                       category=category, creator=creator)
	else:
		creator.is_user = creator.id == login_session['user_id']
		return render_template('item.html', item=item, category=category,
		                       creator=creator, logged='true')


# Create a new item; verify auth and redirect/render accordingly;
@app.route('/category/<int:category_id>/item/new/', methods=['GET', 'POST'])
def newItem(category_id):
	if not validateSignedIn():
		return redirect('/login')
	category = session.query(Category).filter_by(id=category_id).one()
	if login_session['user_id'] != category.user_id:
		flash('You are not authorized to add items to this category. Please create your own category.')
		return redirect(url_for('showItems', category_id=category_id))
	if request.method == 'POST':
		if validateName(request.form['name']):
			valid, img_url = validateImageUrl(request.form['img_url'])
			# Save new item
			if valid == 200:
				newItem = Item(name=request.form['name'], description=request.form['description'],
				               img_url=request.form['img_url'], category_id=category_id, user_id=category.user_id)
				session.add(newItem)
				session.commit()
				flash('New Item %s Item Successfully Created' % (newItem.name))
				return redirect(url_for('showItems', category_id=category_id))

	return render_template('newitem.html', category_id=category_id, logged='true')


# Edit an item; verify auth and redirect/render accordingly;
# Current user must match user_id of item
@app.route('/category/<int:category_id>/item/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(category_id, item_id):
	if not validateSignedIn():
		return redirect('/login')
	try:
		edited_item = session.query(Item).filter_by(id=item_id).one()
	except exc.NoResultFound:
		flash("No results found for the item you wish to edit.")
		return redirect(url_for('showItems', category_id=category_id))
	if edited_item.user_id != login_session['user_id']:
		flash('You are not authorized to edit this. Please create your own in order to edit.')
		return redirect(url_for('showItems', category_id=category_id))
	if request.method == 'POST':
		if validateName(request.form['name']):
			valid, img_url = validateImageUrl(request.form['img_url'])
			if valid == 200:
				edited_item.name = request.form['name']
				edited_item.img_url = img_url
				edited_item.description = request.form['description']
				session.add(edited_item)
				session.commit()
				flash('Item Successfully Edited')
				return redirect(url_for('showItem', category_id=category_id, item_id=edited_item.id))
	else:
		return render_template('edititem.html', category_id=category_id, item_id=item_id, item=edited_item, logged='true')


# Delete an item; verify auth and redirect/render accordingly;
# Current user must match user_id of item
@app.route('/category/<int:category_id>/item/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(category_id, item_id):

	if 'username' not in login_session:
		return redirect('/login')
	category = session.query(Category).filter_by(id=category_id).one()
	itemToDelete = session.query(Item).filter_by(id=item_id).one()
	if login_session['user_id'] != category.user_id:
		return "<script>function myFunction() {alert('You are not authorized to delete item items to this category. Please create your own category in order to delete items.');}</script><body onload='myFunction()''>"
	if request.method == 'POST':
		session.delete(itemToDelete)
		session.commit()
		flash('Item Successfully Deleted')
		return redirect(url_for('showItems', category_id=category_id))
	else:
		return render_template('deleteitem.html', item=itemToDelete, logged='true')


if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=8000)
