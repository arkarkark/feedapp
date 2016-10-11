import logging

from google.appengine.ext import db
from google.appengine.ext import ndb

class WtwfModel(db.Model):

  def AsJsonObject(self, id=None, js=None):
    if js is None:
      js = {}
    for key in self.properties().keys():
      js[key] = getattr(self, key)
    try:
      if id is None:
        id = self.key().id()
      js['id'] = str(id)
    except db.NotSavedError:
      js['id'] = 'new'
    if self.parent():
      js['parent_id'] = self.parent().key().id()

    return js

  def UpdateFromJsonObject(self, js):
    for key, value in js.items():
      if key not in ('id', 'created'):
        if hasattr(self, key):
          ty = self.GetType(key)
          if ty == 'IntegerProperty':
            setattr(self, key, int(value))
          else:
            setattr(self, key, value)

  # following code adapted from: http://stackoverflow.com/questions/1440958/
  def GetPropertyTypeInstance(self, pname):
    return self.properties().get(pname, None)

  def GetType(self, pname):
    return self.GetPropertyTypeInstance(pname).__class__.__name__



class WtwfNdbModel(ndb.Model):

  def AsJsonObject(self, id=None, js=None):
    if js is None:
      js = {}
    for key in self.to_dict().keys():
      js[key] = getattr(self, key)
    try:
      if id is None:
        if self.key:
          id = self.key.id()
        else:
          id = 'new'
      js['id'] = str(id)
    except db.NotSavedError:
      js['id'] = 'new'
    if self.key and self.key.parent():
      js['parent_id'] = str(self.key.parent().id())
    return js

  def UpdateFromJsonObject(self, js):
    for key, value in js.items():
      if key not in ('id', 'created'):
        if hasattr(self, key):
          ty = self.GetType(key)
          if ty == 'IntegerProperty':
            setattr(self, key, int(value))
          else:
            setattr(self, key, value)

  # following code adapted from: http://stackoverflow.com/questions/1440958/
  def GetPropertyTypeInstance(self, pname):
    return self._properties.get(pname, None)

  def GetType(self, pname):
    return self._properties.get(pname, None).__class__.__name__
