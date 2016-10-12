# Copyright 2009 Alex K (wtwf.com) All rights reserved.

__author__ = 'wtwf.com (Alex K)'

import datetime
import json
import logging
import os
import rfc822
import time
import urlparse

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db

# To help protect against a json vulnerability if the json being sent back is
# handled by angular's http service we can prefix this string.
# http://docs.angularjs.org/api/ng.$http (see Security Considerations)
JSON_PREFIX = """)]}',\n"""

def JsonPrinter(obj):
  if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
    obj.isoformat()

class WtwfHandler(webapp.RequestHandler):

  def AssertAllowed(self):
    if not users.is_current_user_admin():
      logging.error('user is not authorized!')
      self.abort(401)
    # TODO(ark) check for XSRF CSRF?

  def TemplateFilename(self, name):
    return os.path.join(os.path.dirname(os.path.dirname(__file__)),
                        'html', name)

  def TemplateContents(self, name, values=None):
    if values is None:
      values = {}
    path = self.TemplateFilename(name)
    return template.render(path, values)

  def SendTemplate(self, name, values=None):
    self.response.out.write(self.TemplateContents(name, values))

  def Error(self, msg, *args):
    if args:
      msg = msg % args
    self.response.out.write('Error: ' + msg)
    # raise webapp.Error(msg)

  def GetBaseUrl(self):
    us = urlparse.urlsplit(self.request.url)
    return us.scheme + '://' + us.netloc


  def IsMobile(self):
    # more info at http://www.zytrax.com/tech/web/mobile_ids.html
    ua = self.request.headers['USER_AGENT']
    simple = ('iPhone', 'AvantGo', 'DoCoMo', 'Minimo', 'BlackBerry',
              'Mobile Safari')
    for x in simple:
      if x in ua:
        return True
    else:
      return False

  def GetUrl(self, snippy):
    if self.IsMobile() and snippy.mobile_url:
      return snippy.mobile_url
    else:
      return snippy.url



class SimplePassword(object):
  """A decorator to provide simple password protection to a app engine
  get request."""

  def __init__(self,
               valid_answers,
               login_required=False,
               template_name=None,
               cookie_name='NoSearchEngines',
               session_cookie_name='NoSearchEnginesSESSION',
               cookie_path='/',
               cookie_value='okeydokelydoodley'):
    self.valid_answers = valid_answers
    self.template_name = template_name
    self.cookie_name = cookie_name
    self.session_cookie_name = session_cookie_name
    self.cookie_path = cookie_path
    self.cookie_value = cookie_value
    self.login_required = login_required

  # see http://www.artima.com/weblogs/viewpost.jsp?thread=240845
  def __call__(self, f):
    decorator = self
    def wrapped_f(*args):
      self = args[0]


      if (self.request.cookies.get(decorator.cookie_name, '') ==
          decorator.cookie_value or
          self.request.cookies.get(decorator.session_cookie_name, '') ==
          decorator.cookie_value):
        # renew the cookies
        decorator.SetCookies(self)
        # if we have &cookie_name in the url redirect to where it isn't
        new_url = decorator.CurrentPageUrl(self)
        if self.request.url != new_url:
          self.redirect(new_url)
          return

        if decorator.login_required:
          user = users.get_current_user()
          if user:
            # send the page
            f(*args)
            # all done
            return
          else:
            self.redirect(users.create_login_url(self.request.uri))
            return

      # cookies are not set!

      # see if we tried to set them and it failed?
      if self.request.get(decorator.cookie_name):
        decorator.sendForm(self, 'setting cookies failed')
        return

      # now see if they are answering the form
      new_url = decorator.CurrentPageUrl(self)
      answer = self.request.get('answer', None)
      if answer:
        if answer.lower() in decorator.valid_answers:
          decorator.SetCookies(self)
          # try to set cookies and redirect to a url indicating cookies were set
          if '?' in new_url:
            new_url += '&'
          else:
            new_url += '?'
          new_url += decorator.GetGetParameter()
          self.redirect(new_url)
          return
        else:
          decorator.sendForm(self, 'invalid answer')
          return
      # just display the form
      decorator.sendForm(self, )
    return wrapped_f

  def sendForm(self, handler_self, message=None):
    form_values = {}
    if message:
      form_values['message'] = message
    template_values = {'content':
                       handler_self.TemplateContents('form.html', form_values)}

    handler_self.SendTemplate('default.html', template_values)

  def SetCookies(self, handler_self):
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    expires = rfc822.formatdate(time.mktime(expires.timetuple()))
    # 'Fri, 31-Dec-2020 23:59:59 GMT'
    handler_self.response.headers.add_header('Set-Cookie',
                                     '%s=%s; expires=%s; path=%s' %
                                     (self.cookie_name, self.cookie_value,
                                      expires, self.cookie_path))
    handler_self.response.headers.add_header('Set-Cookie', '%s=%s; path=%s ' %
                                     (self.session_cookie_name,
                                      self.cookie_value, self.cookie_path))

  def GetGetParameter(self):
    return self.cookie_name + '=y'

  def CurrentPageUrl(self, handler_self):
    url = handler_self.request.url
    param = self.GetGetParameter()
    if url.endswith(param):
      url = url[0:-1 * (len(param) + 1)]
    return url


class UsernameHandler(WtwfHandler):
  """Return a username as a jsonp type script."""

  def get(self):
    username = ""
    user = users.get_current_user()
    if user:
      username = user.email()
    self.response.out.write('wtwf_username = "%s";' % username)


class UserHandler(WtwfHandler):
  """Return a json object with a username or login link or logout link.."""

  def get(self):
    ans = {'logoutUrl': users.create_logout_url("/"),
           'loginUrl': users.create_login_url("/"),
           'username': '',
           'isAdmin': users.is_current_user_admin()}
    user = users.get_current_user()
    if user:
      ans['username'] = user.email()

    self.response.out.write(json.dumps(ans))


def GetGenericDataHandler(model):
  the_model = model
  class SpecificHandler(GenericDataHandler):
    model = the_model
  return SpecificHandler


class GenericDataHandler(WtwfHandler):

  model = None

  def get(self):
    self.AssertAllowed()

    # could be a query or a request for a specific (or new) expand obj
    key_id = self.request.get('id')
    parent_id = self.request.get('parent_id')
    if parent_id and hasattr(self.model, 'parent_model_name'):
      if parent_id == 'new':
        return
      parent_key = db.Key.from_path(self.model.parent_model_name,
                                    long(parent_id))
    else:
      parent_key = None

    if key_id == '':
      all_models = self.model.all()
      if parent_key:
        all_models = all_models.ancestor(parent_key)
      if 'active' in self.model.properties():
        all_models = all_models.filter('active >', False)
      if hasattr(self, 'getObject'):
        ans = [self.getObject(ex) for ex in all_models]
      else:
        ans = [ex.AsJsonObject() for ex in all_models]
    else:
      if key_id == 'new':
        # TODO init this from the json (solves required fields problems)
        ex = self.model(parent=parent_key)
      else:
        ex = self.model.get_by_id(long(key_id), parent=parent_key)
      if hasattr(self, 'getObject'):
        ans = self.getObject(ex)
      else:
        ans = ex.AsJsonObject()
    self.response.out.write(JSON_PREFIX + json.dumps(ans, default=JsonPrinter))


  def post(self):
    self.AssertAllowed()

    key_id = self.request.get('id')
    parent_id = self.request.get('parent_id')
    if parent_id and hasattr(self.model, 'parent_model_name'):
      if parent_id == 'new':
        return
      parent_key = db.Key.from_path(self.model.parent_model_name,
                                    long(parent_id))
    else:
      parent_key = None

    if key_id == 'new':
      # TODO provide a way to do this owner=users.get_current_user().email()
      # and perhaps init it from the json
      ex = self.model(parent=parent_key)
    else:
      ex = self.model.get_by_id(long(key_id), parent=parent_key)

    ex.UpdateFromJsonObject(json.loads(self.request.body))
    if hasattr(ex, 'last_updated_by'):
      ex.last_updated_by = users.get_current_user().email()

    if hasattr(self, 'postObject'):
      ans = self.postObject(ex, json.loads(self.request.body))
    else:
      key = ex.put()
      ans = ex.AsJsonObject()
      ans['id'] = key.id()
    self.response.out.write(JSON_PREFIX + json.dumps(ans, default=JsonPrinter))


  def delete(self):
    self.AssertAllowed()

    parent_id = self.request.get('parent_id')
    if parent_id:
      parent_id = long(parent_id)
      parent_key = db.Key.from_path(self.model.parent_model_name, parent_id)
    else:
      parent_key = None
    ex = self.model.get_by_id(long(self.request.get('id')),
                              parent=parent_key)
    ex.delete()


# from: http://webapp-improved.appspot.com/_modules/webapp2_extras/appengine/users.html

def login_required(handler_method):
    """A decorator to require that a user be logged in to access a handler.

    To use it, decorate your get() method like this::

        @login_required
        def get(self):
            user = users.get_current_user(self)
            self.response.out.write('Hello, ' + user.nickname())

    We will redirect to a login page if the user is not logged in. We always
    redirect to the request URI, and Google Accounts only redirects back as
    a GET request, so this should not be used for POSTs.
    """
    def check_login(self, *args, **kwargs):
        if self.request.method != 'GET':
            self.abort(400, detail='The login_required decorator '
                'can only be used for GET requests.')

        user = users.get_current_user()
        if not user:
            return self.redirect(users.create_login_url(self.request.url))
        else:
            handler_method(self, *args, **kwargs)

    return check_login


def admin_required(handler_method):
    """A decorator to require that a user be an admin for this application
    to access a handler.

    To use it, decorate your get() method like this::

        @admin_required
        def get(self):
            user = users.get_current_user(self)
            self.response.out.write('Hello, ' + user.nickname())

    We will redirect to a login page if the user is not logged in. We always
    redirect to the request URI, and Google Accounts only redirects back as
    a GET request, so this should not be used for POSTs.
    """
    def check_admin(self, *args, **kwargs):
        if self.request.method != 'GET':
            self.abort(400, detail='The admin_required decorator '
                'can only be used for GET requests.')

        user = users.get_current_user()
        if not user:
            return self.redirect(users.create_login_url(self.request.url))
        elif not users.is_current_user_admin():
            self.abort(403)
        else:
            handler_method(self, *args, **kwargs)

    return check_admin
