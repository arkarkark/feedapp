# Copyright 2009 Alex K (wtwf.com) All rights reserved.

__author__ = 'wtwf.com (Alex K)'

import os
import model
import urlparse

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


def admin_required(handler_method):
  """A decorator to require that a user be logged in to access a handler."""
  def check_login(self, *args):
    if self.request.method != 'GET':
      raise webapp.Error('The admin_required decorator can only be used for '
                         'GET requests')
    if not model.is_admin():
      self.redirect(users.create_login_url(self.request.uri))
      return
    else:
      handler_method(self, *args)
  return check_login
