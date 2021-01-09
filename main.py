import webapp2
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
import os

from myuser import MyUser
from directory import Directory


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        url = ''
        url_string = ''
        welcome = 'Welcome back'
        user = users.get_current_user()
        if user:
            url = users.create_logout_url('/')
            url_string = 'logout'
            myuser_key = ndb.Key('MyUser', user.user_id())
            myuser = myuser_key.get()

            #First Time Login
            if myuser == None:
                welcome = 'Welcome to the application'
                myuser = MyUser(id=user.user_id())

                #Create Root Directory of the user
                directory_id = myuser.key.id() + '/'
                directory = Directory(id=directory_id)

                directory.parent_directory = None
                directory.name = 'root'
                directory.path = '/'
                directory.put()

                myuser.root_directory = directory.key
                myuser.put()

                # set current path on first login to root directory
                myuser.current_directory = ndb.Key(Directory, myuser.key.id() + '/')

                myuser.put()


        else:
            url = users.create_login_url('/')
            url_string = 'login'

        template_values = {
            'url' : url,
            'url_string' : url_string,
            'user' : user,
            'welcome' : welcome
        }
        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(template_values))

# starts the web application we specify the full routing table here as well
app = webapp2.WSGIApplication([
('/', MainPage),
], debug=True)
