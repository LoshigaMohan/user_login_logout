
from google.appengine.ext import ndb


class Errorhandler(ndb.Model):
    # error
    error = ndb.StringProperty()
