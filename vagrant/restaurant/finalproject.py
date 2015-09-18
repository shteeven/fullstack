from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

import locale

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route("/")
@app.route("/restaurants/")
def showRestaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)


@app.route("/restaurants/new/", methods=['POST', 'GET'])
def newRestaurant():
    if request.method == "POST":
        restaurant = Restaurant(name=request.form['name'])
        session.add(restaurant)
        session.commit()
        flash('%s successfully created.' % restaurant.name)
    else:
        return render_template('newrestaurant.html')
    return redirect(url_for('showRestaurants'))


@app.route("/restaurants/<int:restaurant_id>/edit/", methods=['POST', 'GET'])
def editRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == "POST":
        if restaurant:
            session.query(Restaurant).filter_by(id=restaurant_id).update({
                'name': request.form['name']
            })
            session.commit()
            flash('%s successfully edited.' % restaurant.name)
    else:
        return render_template('editrestaurant.html', restaurant=restaurant)
    return redirect(url_for('showRestaurants'))


@app.route("/restaurants/<int:restaurant_id>/delete/", methods=['POST', 'GET'])
def deleteRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == "POST":
        if restaurant:
            session.query(Restaurant).filter_by(id=restaurant_id).delete()
            session.commit()
            flash('%s successfully deleted.' % restaurant.name)

    else:
        return render_template('deleterestaurant.html', restaurant=restaurant)
    return redirect(url_for('showRestaurants'))


@app.route("/restaurants/<int:restaurant_id>/")
@app.route("/restaurants/<int:restaurant_id>/menu")
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    return render_template('menu.html', items=items, restaurant=restaurant)


@app.route("/restaurants/<int:restaurant_id>/menu/new/",
           methods=['POST', 'GET'])
def newMenuItem(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if restaurant:
            item = MenuItem(
                name=request.form['name'],
                price=request.form['price'],
                description=request.form['description'],
                course=request.form['course'],
                restaurant_id=restaurant_id
            )
            session.add(item)
            session.commit()
            flash('%s successfully created.' % item.name)
    else:
        return render_template('newmenuitem.html', restaurant=restaurant)
    return redirect(url_for('showMenu', restaurant_id=restaurant.id))


@app.route("/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit",
           methods=['POST', 'GET'])
def editMenuItem(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(restaurant_id=restaurant_id,
                                             id=menu_id).one()
    if request.method == 'POST':
        if item:
            session.query(MenuItem).filter_by(
                restaurant_id=restaurant_id,
                id=menu_id).update({'name': request.form['name'],
                                    'price': request.form['price'],
                                    'description': request.form['description'],
                                    'course': request.form['course']})
            session.commit()
            flash('%s successfully edited.' % item.name)
    else:
        return render_template('editmenuitem.html', item=item)
    return redirect(url_for('showMenu', restaurant_id=restaurant_id))


@app.route("/restaurants/<int:restaurant_id>/menu/<int:menu_id>/delete",
           methods=['POST', 'GET'])
def deleteMenuItem(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(restaurant_id=restaurant_id,
                                             id=menu_id).one()
    if request.method == 'POST':
        if item:
            session.query(MenuItem).filter_by(restaurant_id=restaurant_id,
                                              id=menu_id).delete()
            session.commit()
            flash('%s successfully deleted.' % item.name)
    else:
        return render_template('deletemenuitem.html', item=item)
    return redirect(url_for('showMenu', restaurant_id=restaurant_id))


# API Endpoints ###########
@app.route("/restaurants/JSON")
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants=[i.serialize for i in restaurants])


@app.route("/restaurants/<int:restaurant_id>/menu/JSON")
def restaurantMenuJSON(restaurant_id):
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route("/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON")
def menuItemJSON(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItem=item.serialize)


def convertPrice(text):  # force prices to be formatted correctly
    price = float(text.replace("$", ""))
    locale.setlocale(locale.LC_ALL, '')
    return locale.currency(price)


if __name__ == "__main__":
    app.secret_key = 'hey'
    app.debug = True
    app.run('0.0.0.0', port=5000)