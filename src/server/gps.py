# Copyright 2017 Alex K (wtwf.com)

__author__ = 'wtwf.com (Alex K)'

import os
import logging
import datetime
import urllib
import json

from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.api.mail import InboundEmailMessage

from google.appengine.api import images

from oauth2client.contrib.appengine import AppAssertionCredentials

import auth

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
    self.response.headers['Content-Type'] = 'text/plain'

    file_name = os.path.join(os.path.dirname(__file__), 'original_msg.txt')
    message = mail.InboundEmailMessage(open(file_name, 'r').read())

    if False:
      for content_type, body in message.bodies():
        self.response.out.write("body %r\n" % [content_type, body.decode()])

    for attachment in message.attachments:
      image_data = attachment.payload.decode()
      img = images.Image(image_data=image_data)
      img.rotate(0)
      img.execute_transforms(parse_source_metadata=True)

      self.response.out.write("done %r\n" % [
        attachment.filename, attachment.content_id,
        # dir(img),
      ],
      )
      self.response.out.write(
        json.dumps(img.get_original_metadata(), sort_keys=True, indent=4, separators=(',', ': '))
      )

    reverse_geocode_result = auth.googlemaps.reverse_geocode((40.714224, -73.961452))
    self.response.out.write("reverse %r" % reverse_geocode_result)
