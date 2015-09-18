__author__ = 'Shtav'
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine, update
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

class webserverHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurant") or self.path.endswith("/"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                restaurants = session.query(Restaurant.name, Restaurant.id)

                output = ''
                output += '<html><body>'
                output += '<a href="/restaurant/new">Enter new restaurant.</a>'
                for i in restaurants:
                    output += '<p> %s </p>' \
                              '<p><a href="/restaurant/%s/edit">Edit </a></p>' \
                              '<p><a href="/restaurant/%s/delete">Delete</a></p>' \
                              % (i[0], i[1], i[1])
                output += '</body></html>'
                self.wfile.write(output)
                return

            if self.path.endswith("/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ''
                output += '<html><body>'
                output += '<a href="/restaurant">Return to list.</a>'
                output += '<form method="POST" enctype="multipart/form-data" ' \
                      'action="/restaurant/new">' \
                      '<h2>Enter the new Restaurant\'s ' \
                          'name and hit submit:</h2> ' \
                      '<input name="name" type="text"> ' \
                      '<input type="submit" value="Submit"> </form> '
                output += '</body></html>'
                self.wfile.write(output)
                return

            if self.path.endswith("/edit"):
                restaurant_id = self.path.split('/')[2]
                restaurant_exists = session.query(Restaurant)\
                    .filter_by(id=restaurant_id).one()
                if restaurant_exists:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    output = ''
                    output += '<html><body>'
                    output += '<form method="POST" enctype="multipart/form-data" ' \
                          'action="/restaurant/%s/edit">' \
                          '<h2>Edit ' \
                          '<em> %s </em>\'s name and hit submit:</h2> ' \
                          '<input name="name" type="text"> ' \
                          '<input type="submit" value="Submit"> </form> ' \
                              % (restaurant_exists.id, restaurant_exists.name)
                    output += '</body></html>'
                    self.wfile.write(output)
                return

            if self.path.endswith("/delete"):
                restaurant_id = self.path.split('/')[2]
                restaurant_exists = session.query(Restaurant)\
                    .filter_by(id=restaurant_id).one()
                if restaurant_exists:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    output = ''
                    output += '<html><body>'
                    output += '<form method="POST" enctype="multipart/form-data" ' \
                          'action="/restaurant/%s/delete">' \
                          '<h2>Do you want to remove <em>%s</em>?</h2> ' \
                          '<input type="submit" value="Delete"> </form> ' \
                              % (restaurant_exists.id, restaurant_exists.name)
                    output += '</body></html>'
                    self.wfile.write(output)
                return

        except IOError:
            self.send_error(404, 'File not found %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/new"): # NEW POST REQUEST
                ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    namecontent = fields.get('name')
                new_restaurant = Restaurant(name=namecontent[0])
                session.add(new_restaurant)
                session.commit()
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurant')
                self.end_headers()

            if self.path.endswith("/edit"):  # EDIT POST REQUEST
                ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    namecontent = fields.get('name')
                restaurant_id = self.path.split('/')[2]
                restaurant_exists = session.query(Restaurant)\
                    .filter_by(id=restaurant_id).one()
                if restaurant_exists != []:
                    restaurant_exists.name = namecontent[0]
                    session.add(restaurant_exists)
                    session.commit()
                session.query(Restaurant).filter(Restaurant.id == restaurant_id).\
                    update({'name': namecontent[0]})
                session.commit()
                output = '<html><body>'
                output += '<h2> Okay, how about this? </h2>'
                output += '<h1> %s </h1>' %namecontent[0]
                output += '<form method="POST" enctype="multipart/form-data" ' \
                          'action="/restaurant/%s/edit">' \
                          '<h2>Edit restaurant name and hit submit:</h2> ' \
                          '<input name="name" type="text"> ' \
                          '<input type="submit" value="Submit"> </form> ' \
                          '<a href="/restaurant">Restaurant List</a>' \
                          %restaurant_id
                output += '</body></html>'
                self.wfile.write(output)

            if self.path.endswith("/delete"):  # DELETE POST REQUEST
                restaurant_id = self.path.split('/')[2]
                print("here")
                restaurant_exists = session.query(Restaurant)\
                    .filter_by(id=restaurant_id).one()
                if restaurant_exists:
                    print(restaurant_exists.id)
                    session.delete(restaurant_exists)
                    session.commit()
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurant')
                self.end_headers()

        except:
            pass



def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print('Webserver started at port %s' % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print('^c entered, server terminated.')
        session.close()
        server.socket.close()

if __name__ == "__main__":
    main()
