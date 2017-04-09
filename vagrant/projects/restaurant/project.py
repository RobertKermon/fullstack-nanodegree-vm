import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)

def openDB():
    engine = create_engine('sqlite:///restaurantMenu.db')
    Base.metadata.bind=engine
    DBSession = sessionmaker(bind = engine)
    session = DBSession()
    return session

@app.route('/restaurants/<int:restaurant_id>/menu')
def restaurantMenu(restaurant_id):
    session = openDB()
    try:
        restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
        items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
        return render_template('menu.html', restaurant=restaurant, items=items)
    finally:
        session.close()

@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    session = openDB()
    try:
        #restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
        items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
        return jsonify(MenuItems=[item.serialize for item in items])
    finally:
        session.close()

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def restaurantMenuItemJSON(restaurant_id,menu_id):
    session = openDB()
    try:
        #restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
        items = session.query(MenuItem).filter_by(id=menu_id)
        return jsonify(MenuItems=[item.serialize for item in items])
    finally:
        session.close()



@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET','POST'])
def newMenuItem(restaurant_id):
    session = openDB()
    try:
        if request.method == 'POST':
            newItem = MenuItem(name=request.form["name"],restaurant_id=restaurant_id)
            session.add(newItem)
            session.commit()
            flash("Add menu item successful.")
            return redirect(url_for('restaurantMenu',restaurant_id=restaurant_id))
        restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
        return render_template('newMenuItem.html', restaurant=restaurant)
    finally:
        session.close()
        print("db session closed")

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    session = openDB()
    try:
        restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
        item = session.query(MenuItem).filter_by(id = menu_id).one()
        if request.method == 'POST':
            item.name=request.form["name"]
            session.add(item)
            session.commit()
            flash("Edit menu item successful.")
            return redirect(url_for('restaurantMenu',restaurant_id=restaurant_id))
        return render_template('editMenuItem.html', restaurant=restaurant, item=item)
    finally:
        session.close()
        print("db session closed")

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
    session = openDB()
    try:
        restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
        item = session.query(MenuItem).filter_by(id = menu_id).one()
        if request.method == 'POST':
            session.delete(item)
            session.commit()
            flash("Delete menu item successful.")
            return redirect(url_for('restaurantMenu',restaurant_id=restaurant_id))
        return render_template('deleteMenuItem.html', restaurant=restaurant, item=item)
    finally:
        session.close()
        print("db session closed")





@app.route('/')
@app.route('/hello')
def HelloWorld():
    output = "Hello World - v1.3"
    return output

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run (host = '', port = 5000)