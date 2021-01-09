from google.appengine.ext import ndb

class MyUser(ndb.Model):
    # email address of this user
    email_address = ndb.StringProperty()
