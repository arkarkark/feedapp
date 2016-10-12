# Copyright 2009 Alex K (wtwf.com) All rights reserved.

__author__ = 'wtwf.com (Alex K)'

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp

__pychecker__ = 'no-override'

class Admins(db.Model):
  admin_email = db.StringProperty(required=True)

def is_admin():
  user = users.get_current_user()
  if user:
    if Admins.all().filter('admin_email = ', user.email()).fetch(1):
      return True
  return False

def no_admins():
  admins = Admins.all().fetch(1)
  if not admins:
    return True
  else:
    return False

