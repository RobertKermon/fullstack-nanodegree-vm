import cgi
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class webserverHandler(BaseHTTPRequestHandler):
    def getHello(self):
        output = ""
        output += "<html><body>"
        if self.path.endswith("/hello"):
            output += "Hello!<br /><a href=\"/hola\">Espanol</a>"
        if self.path.endswith("/hola"):
            output += "&#161Hola!<br /><a href=\"/hello\">English</a>"
        output += "<form method='POST' enctype='multipart/form-data' action='/hello'>"
        output += "<h2>What would you like me to say?</h2><input name='message' type='text' />"
        output += "<input type='submit' value='Submit' />"
        output += "</form>"
        output += "</body></html>"
        self.send_response(200)
        self.send_header('Content-Type','text/html')
        self.end_headers()
        self.wfile.write(output)
        print("sending {0}".format(output))
        return
    
    def postHello(self):
        ctype,pdict = cgi.parse_header(self.headers.getheader('Content-Type'))
        if ctype == 'multipart/form-data':
            fields = cgi.parse_multipart(self.rfile, pdict)
            messageContent = fields.get('message')
        output = ""
        output += "<html><body>"
        output += "<h2> message received: </h2>"
        output += "<h1>{0}</h1>".format(cgi.escape(messageContent[0]))
        output += "<form method='POST' enctype='multipart/form-data' action='/hello'>"
        output += "<h2>What would you like me to say?</h2><input name='message' type='text' />"
        output += "<input type='submit' value='Submit' />"
        output += "</form>"
        output += "</body></html>"
        self.send_response(200)  # the course said to use 301 "moved permanently" for post requests. 200 is appropriate for success. 301 would be appropriate if the result was required to perform a get from another URL
        self.end_headers()
        self.wfile.write(output)
        print("sending {0}".format(output))
        return

    def openDB(self):
        engine = create_engine('sqlite:///restaurantMenu.db')
        Base.metadata.bind=engine
        DBSession = sessionmaker(bind = engine)
        session = DBSession()
        return session

    def handleEditRestaurantForm(self):
        output = "<html><body>"
        restuarantId = self.path.split('/')[2]
        output += "<h1>Editing restaurant ID '{0}'</h1>".format(restuarantId)
        session = self.openDB()
        restaurant = session.query(Restaurant).filter_by(id = restuarantId).one()
        output += "<h1>Editing '{0}' which has an ID of {1}</h1>".format(cgi.escape(restaurant.name),restaurant.id)
        if self.command.upper() == 'POST':
            ctype,pdict = cgi.parse_header(self.headers.getheader('Content-Type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                restaurantName = fields.get('name')[0].strip()
            else:
                raise Exception('content type is not form data')
            if len(restaurantName) == 0:
                raise Exception('restaurant name is 0 length string')
            restaurant.name = restaurantName
            session.add(restaurant)
            session.commit()
            output += "<br /><h2>The new restaurant name is {0}</h2>".format(cgi.escape(restaurant.name))
        session.close()
        output += "<br /><br /><br />"
        output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/{0}/edit'>".format(restuarantId)
        output += "<h2>Rename the restaurant to </h2><input name='name' type='text' />"
        output += "<input type='submit' value='Submit' />"
        output += "</form>"
        output += "<a href='/restaurants'>Main restaurant listing</a>"
        output += "</body></html>"
        self.send_response(200)
        self.send_header('Content-Type','text/html')
        self.end_headers()
        self.wfile.write(output)
        print("sending {0}".format(output))

    def handleDeleteRestaurantForm(self):
        output = "<html><body>"
        restuarantId = self.path.split('/')[2]
        output += "<h1>Deleting restaurant ID '{0}'</h1>".format(restuarantId)
        session = self.openDB()
        restaurant = session.query(Restaurant).filter_by(id = restuarantId).one()
        output += "<h1>Deleting '{0}' which has an ID of {1}</h1>".format(cgi.escape(restaurant.name),restaurant.id)
        if self.command.upper() == 'POST':
            ctype,pdict = cgi.parse_header(self.headers.getheader('Content-Type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                confirmed = fields.get('confirm') is not None
            else:
                raise Exception('content type is not form data')
            output += "confirmed = {0}".format(confirmed)
            if confirmed:
                session.delete(restaurant)
                session.commit()
                session.close()
                self.send_response(301)
                self.send_header('Location','/restaurants')
                self.end_headers()
                return
            else:
                output += "<br /><h2>The restaurant {0} named '{1}' has NOT been deleted, because the deletion was not confirmed</h2>".format(restaurant.id,cgi.escape(restaurant.name))
        session.close()
        output += "<br /><br /><br />"
        output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/{0}/delete'>".format(restuarantId)
        output += "<input name='confirm' type='checkbox'>I really want to delete this restaurant.</input>"
        output += "<input type='submit' value='Submit' />"
        output += "</form>"
        output += "<a href='/restaurants'>Main restaurant listing</a>"
        output += "</body></html>"
        self.send_response(200)
        self.send_header('Content-Type','text/html')
        self.end_headers()
        self.wfile.write(output)
        print("sending {0}".format(output))
        
    def handleNewRestaurantForm(self):
        try:
            output = "<html><body>"
            if self.command.upper() == 'POST':
                ctype,pdict = cgi.parse_header(self.headers.getheader('Content-Type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurantName = fields.get('name')[0].strip()
                else:
                    raise Exception('content type is not form data')
                if len(restaurantName) == 0:
                    raise Exception('restaurant name is 0 length string')
                session = self.openDB()
                theNewRestaurant = Restaurant(name = restaurantName)
                session.add(theNewRestaurant)
                session.commit()
                output += "<h3>Added restaurant '{0}'</h3>".format(cgi.escape(restaurantName))
                session.close()
            output += "<br /><br /><br />"
            output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
            output += "<h2>Add a new restaurant</h2><input name='name' type='text' />"
            output += "<input type='submit' value='Submit' />"
            output += "</form>"
            output += "<a href='/restaurants'>Main restaurant listing</a>"
            output += "</body></html>"
            self.send_response(200)
            self.send_header('Content-Type','text/html')
            self.end_headers()
            self.wfile.write(output)
            print("sending {0}".format(output))
        except Exception as error:
            self.send_error(500,"Internal Server Error '{0}'".format(error))

    def getRestaurants(self):
        try:
            output = "<html><body>"
            session = self.openDB()
            restaurants = session.query(Restaurant).all()
            output = "<h1>Restaurants</h1><br />"
            for restaurant in restaurants:
                output += "<h3>{0} <a href='/restaurants/{1}/edit'>edit</a> <a href='/restaurants/{1}/delete'>delete</a><br /></h3>".format(cgi.escape(restaurant.name),restaurant.id)
            output += "<br /><br /><br />"
            output += "<a href='/restaurants/new'>Add a new restaurant</a>"
            output += "</body></html>"
            session.close()
            self.send_response(200)
            self.send_header('Content-Type','text/html')
            self.end_headers()
            self.wfile.write(output)
            print("sending {0}".format(output))
        except Exception as error:
            self.send_error(500,"Internal Server Error '{0}'".format(error))

    def do_GET(self):
        print ("GET received {0}".format(self.path))
        try:
            if self.path.startswith("/restaurants"):
                if self.path.endswith("/new"):
                    self.handleNewRestaurantForm()
                    return
                elif self.path.endswith("/edit"):
                    self.handleEditRestaurantForm()
                    return
                elif self.path.endswith("/delete"):
                    self.handleDeleteRestaurantForm()
                    return
                elif self.path.endswith("/restaurants"):
                    self.getRestaurants()
                    return
            elif self.path.endswith("/hello"):
                self.getHello()
                return
            elif self.path.endswith("/hola"):
                self.getHello()
                return
            else:
                self.send_error(404,"Resource Not Found '{0}'".format(self.path))
        except IOError:
            self.send_error(404,"File Not Found '{0}'".format(self.path))

    def do_POST(self):
        print ("POST received {0}".format(self.path))
        try:
            if self.path.startswith("/restaurants"):
                if self.path.endswith("/new"):
                    self.handleNewRestaurantForm()
                    return
                if self.path.endswith("/edit"):
                    self.handleEditRestaurantForm()
                    return
                if self.path.endswith("/delete"):
                    self.handleDeleteRestaurantForm()
                    return
            elif self.path.endswith("/hello"):
                self.postHello()
                return
        except Exception as error:
            self.send_error(500,"Internal Server Error '{0}'".format(error))

#define a main function that starts a basic web server
def main():
    try:
        port = 8080
        server = HTTPServer(('', port),webserverHandler)
        try:
            print ("Web server running on port {0}".format(port))
            server.serve_forever()
        except KeyboardInterrupt:
            print ("Keyboard interupt (^C) received, stopping web server")
            server.server_close()
            print ("Web server stopped")
    except Exception as error:
        print ("Unable to start web server port {0} - error message {1}".format(port,error))


#run the "main" function if this module is the entry point 
if __name__ == "__main__":
    main()