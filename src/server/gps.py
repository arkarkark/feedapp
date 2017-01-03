# Copyright 2017 Alex K (wtwf.com)

__author__ = 'wtwf.com (Alex K)'

import os
import logging
import datetime
import urllib

from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.api.mail import InboundEmailMessage

from wtwf import wtwfhandler
from wtwf.WtwfModel import WtwfNdbModel

from crud import crud_model
from crud import crud_handler

class PictureMail(crud_model.CrudNdbModel):
  """Info and options about a picture mail email address"""

  name = ndb.StringProperty()
  # automatic fields
  created = ndb.DateTimeProperty(auto_now_add=True)

class PictureMailItem(crud_model.CrudNdbModel):
  """Stores Info about a post to a feed."""

  parent_model_name = 'MailFeed'

  subject = ndb.StringProperty()
  body = ndb.TextProperty()
  guid = ndb.StringProperty()
  # automatic fields
  created = ndb.DateTimeProperty(auto_now_add=True)

class EmailToPicture(InboundMailHandler):

  def post(self, name):
    """Transforms body to email request."""

    try:
      name = urllib.unquote(name).split('@')[0]
    except:
      pass

    # get the feed object
    picture_mail = PictureMail.query(PictureMail.name == name).get()
    if picture_mail is not None:
      self.receive(mail.InboundEmailMessage(self.request.body), feed)
    else:
      # 404 ?
      pass

  def receive(self, mail_message, feed):

    sender = mail_message.sender

    if sender:
      # strip it just to the domain name
      try:
        sender = sender.split("@")[1].split(".")[-2]
      except IndexError:
        pass

    subject = mail_message.subject
    if sender:
      subject = ": ".join([sender, subject])
    body = mail_message.bodies().next()[1].decode()

    logging.info("Subject is : %r", subject)
    logging.debug("Body is : %r", body)

    item = MailFeedItem(parent=feed.key, subject=subject, body=body)
    item.put()

    logging.info("Added a message for: " + feed.name)

class Demo(webapp.RequestHandler):
  """Setup a Demo feed."""

  def get(self):
    if not users.is_current_user_admin():
      self.error(401)
      return

    # remove the old test
    name = "test_feed"
    feed = MailFeed.query(MailFeed.name == name).get()
    if feed:
      for item in MailFeedItem.query(ancestor=feed.key):
        item.key.delete()
      feed.key.delete()

    # now make some test stuff
    feed = MailFeed(name=name)
    feed.put()

    logging.info('added new feed: %s', name)

    testdata = os.path.join(os.path.dirname(__file__), 'testdata')
    etf = EmailToFeed()

    for x in range(1, 4):
      filename = os.path.join(testdata, "email-%02d.txt" % x)
      logging.info('adding: %s', filename)
      self.response.out.write(filename + '</br>')
      f = file(filename)
      body = '\r\n'.join(line.rstrip() for line in f)
      f.close()
      # now inject this into the code where we process emails.
      msg = InboundEmailMessage(body)
      etf.receive(msg, feed)
    self.response.out.write('<p><button onClick="history.back()">' +
                            'DONE</button></p>')
