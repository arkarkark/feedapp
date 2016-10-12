# Copyright 2011 Alex K (wtwf.com)

__author__ = 'wtwf.com (Alex K)'

import os
import logging
import datetime
import urllib

import PyRSS2Gen as rss

from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.api.mail import InboundEmailMessage

from wtwf import wtwfhandler
from wtwf.WtwfModel import WtwfNdbModel
import sanitizeblogger

from crud import crud_model
from crud import crud_handler

# wget -O - 'http://localhost:8080/mailfeed/test' | xmllint -format -

class MailFeed(crud_model.CrudNdbModel):
  """Info and options about a feed. None yet."""

  name = ndb.StringProperty()
  # automatic fields
  created = ndb.DateTimeProperty(auto_now_add=True)

class MailFeedItem(crud_model.CrudNdbModel):
  """Stores Info about a post to a feed."""

  parent_model_name = 'MailFeed'

  subject = ndb.StringProperty()
  body = ndb.TextProperty()
  guid = ndb.StringProperty()
  # automatic fields
  created = ndb.DateTimeProperty(auto_now_add=True)

class EmailToFeed(InboundMailHandler):

  def post(self, name):
    """Transforms body to email request."""
    self.receive(mail.InboundEmailMessage(self.request.body),
                 urllib.unquote(name))

  def receive(self, mail_message, name):

    try:
      name = name.split('@')[0]
    except:
      pass

    # get the feed object
    feed = MailFeed.query(MailFeed.name == name).get()

    body = mail_message.bodies().next()[1].decode()
    logging.info("Body is : %r", body)

    item = MailFeedItem(parent=feed,
                        subject=mail_message.subject,
                        body=body)
    item.put()

    logging.info("Added a message for: " + name)

class FeedFromEmail(webapp.RequestHandler):
  """output a feed for a given name."""

  def get(self, name):
    feed = MailFeed.query(MailFeed.name == name).get()

    if not feed:
      # no feed we need to make one
      feed = MailFeed(name=name)
      feed.put()

    items = MailFeedItem.query(ancestor=feed.key).order(
        -MailFeedItem.created).fetch(5)

    f = rss.RSS2(title = "Generated Feed",
                 link = "http://example.com/",
                 description = "Generated Feed ",
                 lastBuildDate = datetime.datetime.now(),
                 )

    for x in items:
      guid = x.guid
      if not guid:
        x.guid = 'feedapp-%s-%s' % (name, x.created)
        try:
          x.save()
        except:
          pass

      f.items.append(
        rss.RSSItem(
          title = x.subject,
          link = None,
          description = x.body,
          guid = rss.Guid(x.guid, False),
          pubDate = x.created))

    self.response.headers['Content-Type'] = 'text/xml'
    f.write_xml(self.response.out)


class SetupDemo(webapp.RequestHandler):
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
      etf.receive(msg, name)
    self.response.out.write('<p><button onClick="history.back()">' +
                            'DONE</button></p>')


class MailItemDataHandler(crud_handler.GetCrudHandler(MailFeedItem)):
  def postObject(self, item, js):
    if self.request.get('action') == 'tombstone':
      item.body = sanitizeblogger.DELETED
      item.subject = sanitizeblogger.DELETED
      item.put()
      # no need to updated id from key because item will never be new
      js = item.AsJsonObject(js=js)
    return js
