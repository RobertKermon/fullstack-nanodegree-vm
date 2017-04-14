import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session

#variable initialization
app = Flask(__name__)

#module functions
def openDB():
    engine = create_engine('sqlite:///restaurantMenu.db')
    Base.metadata.bind=engine
    DBSession = sessionmaker(bind = engine)
    databaseSession = DBSession()
    return databaseSession


#Restaurant listing functions
@app.route('/')
@app.route('/restaurants/')
def restaurantList():
    databaseSession = openDB()
    try:
        restaurants = databaseSession.query(Restaurant).all()
        if not 'isAdmin' in session:
            session["isAdmin"]=0
        if request.args.get('isAdmin'):
            session["isAdmin"]=(request.args.get('isAdmin')=="1")
        return render_template('restaurantList.html', restaurants=restaurants, isAdmin=session["isAdmin"])
    finally:
        databaseSession.close()

@app.route('/restaurants/JSON/')
def restaurantsJSON():
    databaseSession = openDB()
    try:
        restaurants = databaseSession.query(Restaurant).all()
        return jsonify(Restaurant=[restaurant.serialize for restaurant in restaurants])
    finally:
        databaseSession.close()


#Menu display functions
@app.route('/restaurants/<int:restaurant_id>/menu/')
def restaurantMenu(restaurant_id):
    databaseSession = openDB()
    try:
        restaurant = databaseSession.query(Restaurant).filter_by(id = restaurant_id).one()
        items = databaseSession.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
        return render_template('menu.html', restaurant=restaurant, items=items, isAdmin=session["isAdmin"])
    finally:
        databaseSession.close()

@app.route('/restaurants/<int:restaurant_id>/menu/JSON/')
def restaurantMenuJSON(restaurant_id):
    databaseSession = openDB()
    try:
        items = databaseSession.query(MenuItem).filter_by(restaurant_id=restaurant_id)
        return jsonify(MenuItems=[item.serialize for item in items])
    finally:
        databaseSession.close()

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
def restaurantMenuItemJSON(restaurant_id,menu_id):
    databaseSession = openDB()
    try:
        items = databaseSession.query(MenuItem).filter_by(id=menu_id)
        return jsonify(MenuItems=[item.serialize for item in items])
    finally:
        databaseSession.close()


#Restaurant editing functions
@app.route('/restaurants/new/', methods=['GET','POST'])
def newRestaurant():
    databaseSession = openDB()
    try:
        if request.method == 'POST':
            newRestaurant = Restaurant(name=request.form["name"])
            databaseSession.add(newRestaurant)
            databaseSession.commit()
            flash("New Restaurant Created")
            return redirect(url_for('restaurantList'))
        return render_template('newRestaurant.html')
    finally:
        databaseSession.close()
        print("db databaseSession closed")

@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET','POST'])
def editRestaurant(restaurant_id):
    databaseSession = openDB()
    try:
        restaurant = databaseSession.query(Restaurant).filter_by(id = restaurant_id).one()
        if request.method == 'POST':
            restaurant.name=request.form["name"]
            databaseSession.add(restaurant)
            databaseSession.commit()
            flash("Restaurant Sucessfully Edited")
            return redirect(url_for('restaurantList'))
        return render_template('editRestaurant.html', restaurant=restaurant)
    finally:
        databaseSession.close()
        print("db databaseSession closed")

@app.route('/restaurants/<int:restaurant_id>/delete/', methods=['GET','POST'])
def deleteRestaurant(restaurant_id):
    databaseSession = openDB()
    try:
        restaurant = databaseSession.query(Restaurant).filter_by(id = restaurant_id).one()
        if request.method == 'POST':
            databaseSession.delete(restaurant)
            databaseSession.commit()
            flash("Restaurant Sucessfully Deleted")
            return redirect(url_for('restaurantList'))
        return render_template('deleterestaurant.html', restaurant=restaurant)
    finally:
        databaseSession.close()
        print("db databaseSession closed")


#MenuItem editing functions
@app.route('/restaurants/<int:restaurant_id>/menu/new/', methods=['GET','POST'])
def newMenuItem(restaurant_id):
    databaseSession = openDB()
    try:
        if request.method == 'POST':
            newItem = MenuItem(name=request.form["name"],restaurant_id=restaurant_id,price=request.form["price"],course=request.form["course"],description=request.form["description"])
            databaseSession.add(newItem)
            databaseSession.commit()
            flash("Menu Item Created")
            return redirect(url_for('restaurantMenu',restaurant_id=restaurant_id))
        restaurant = databaseSession.query(Restaurant).filter_by(id = restaurant_id).one()
        return render_template('newMenuItem.html', restaurant=restaurant)
    finally:
        databaseSession.close()
        print("db databaseSession closed")

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    databaseSession = openDB()
    try:
        item = databaseSession.query(MenuItem).filter_by(id = menu_id).join(Restaurant).filter_by(id = restaurant_id).one()
        restaurant = item.restaurant
        if request.method == 'POST':
            item.name=request.form["name"]
            item.price=request.form["price"]
            item.course=request.form["course"]
            item.description=request.form["description"]            
            databaseSession.add(item)
            databaseSession.commit()
            flash("Menu Item Sucessfully Edited")
            return redirect(url_for('restaurantMenu',restaurant_id=restaurant_id))
        return render_template('editMenuItem.html', restaurant=restaurant, item=item)
    finally:
        databaseSession.close()
        print("db databaseSession closed")

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
    databaseSession = openDB()
    try:
        item = databaseSession.query(MenuItem).filter_by(id = menu_id).join(Restaurant).filter_by(id = restaurant_id).one()
        restaurant = item.restaurant
        if request.method == 'POST':
            databaseSession.delete(item)
            databaseSession.commit()
            flash("Menu Item Sucessfully Deleted")
            return redirect(url_for('restaurantMenu',restaurant_id=restaurant_id))
        return render_template('deleteMenuItem.html', restaurant=restaurant, item=item)
    finally:
        databaseSession.close()
        print("db databaseSession closed")


#App runner
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run (host = '', port = 5000)