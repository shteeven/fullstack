__author__ = 'Shtav'
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import locale
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

@app.route("/")
def defaultRestaurantMenu():
    restaurant = session.query(Restaurant).first()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)

    return render_template('menu.html', restaurant=restaurant, items=items)

@app.route("/restaurants/<int:restaurant_id>/")
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)

    return render_template('menu.html', restaurant=restaurant, items=items)

@app.route("/restaurants/<int:restaurant_id>/new/", methods=['POST', 'GET'])
def newMenuItem(restaurant_id):
    if request.method == "POST":
        newItem = MenuItem(name=request.form['name'],
                           price=convertPrice(request.form['price']),
                           description=request.form['description'],
                           restaurant_id=restaurant_id)

        session.add(newItem)
        session.commit()
        flash('%s successfully added to menu.' % newItem.name)
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)

    return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))

@app.route("/restaurants/<int:restaurant_id>/<int:menu_id>/edit/",
           methods=['POST', 'GET'])
def editMenuItem(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(restaurant_id=restaurant_id,
                                             id=menu_id).one()
    if request.method == "POST":
        if item:
            session.query(MenuItem).filter_by(
                restaurant_id=restaurant_id,
                id=menu_id).update({'name': request.form['name'],
                                    'price': request.form['price'],
                                    'description': request.form['description']})
            session.commit()
            flash('%s successfully edited.' % item.name)
    else:
        return render_template('editmenuitem.html', item=item)

    return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))


@app.route("/restaurants/<int:restaurant_id>/<int:menu_id>/delete/",
           methods=['POST', 'GET'])
def deleteMenuItem(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(restaurant_id=restaurant_id,
                                             id=menu_id).one()
    if request.method == "POST":
        if item:
            session.query(MenuItem).filter_by(
                restaurant_id=restaurant_id,
                id=menu_id).delete()
            session.commit()
            flash('%s successfully deleted.' % item.name)

    else:
        return render_template('deletemenuitem.html',
                               item=item)

    return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))


@app.route("/restaurants/<int:restaurant_id>/menu/JSON")
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route("/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON")
def menuItemJSON(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItem=item.serialize)


def convertPrice(text):
    price = float(text.replace("$", ""))
    locale.setlocale(locale.LC_ALL, '')
    return locale.currency(price)


if __name__ == "__main__":
    app.secret_key = 'hey'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
