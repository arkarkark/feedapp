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

    try:
      name = urllib.unquote(name).split('@')[0]
    except:
      pass

    # get the feed object
    feed = MailFeed.query(MailFeed.name == name).get()
    if feed is not None:
      self.receive(mail.InboundEmailMessage(self.request.body), feed)
    else:
      # 404 ?
      pass

  def receive(self, mail_message, feed):

    sender = None
    if 'list-id' in mail_message.original:
      sender = mail_message.original['list-id'].strip("""<>"'`""").split(".")[0]
    else:
      sender = mail_message.sender

      if sender:
        # strip it just to the domain name
        try:
          short_sender = sender.split("@")[1].split(".")[-2]
          if short_sender in ['gmail', 'google', 'yahoo', 'aol', 'ca']:
            # o.k. try the bit before the @ sign for gmail users
            sender = sender.split("@")[0]
          else:
            sender = short_sender
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

    f = rss.RSS2(
      title="Generated Feed",
      link="http://example.com/",
      description="Generated Feed ",
      lastBuildDate=datetime.datetime.now(),
    )

    for x in items:
      guid = x.guid
      if not guid:
        x.guid = 'feedapp-%s-%s' % (name, x.created)
        try:
          x.save()
        except:
          pass

      f.items.append(rss.RSSItem(
        title=x.subject,
        link=None,
        description=x.body,
        guid=rss.Guid(x.guid, False),
        pubDate=x.created,
      ))

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
      etf.receive(msg, feed)
    self.response.out.write('<p><button onClick="history.back()">' +
                            'DONE</button></p>')

class BulkDeleteMailItems(webapp.RequestHandler):
  """Blow away old feed items."""

  def get(self):
    logging.info('BulkDeleteMailItems')
    if not users.is_current_user_admin():
      self.error(401)
      return

    logging.info('Passed Auth')

    # olderthan = datetime.datetime(2018,1,1)
    olderthan = datetime.datetime.now() - datetime.timedelta(days=180)

    q = MailFeedItem.query().filter(MailFeedItem.created < olderthan)
    items = q.fetch(5000, keys_only=True)

    self.response.out.write('<p>%d items</p>' % len(items))

    ndb.delete_multi(items)

    self.response.out.write('<p><button onClick="history.back()">' +
                            'DONE</button></p>')


class MailItemDataHandler(crud_handler.GetCrudHandler(MailFeedItem)):
  def postEntity(self, item, js):
    if self.request.get('action') == 'tombstone':
      item.body = item.subject = "This post is no longer available."
      item.put()
      # no need to updated id from key because item will never be new
      js = item.AsJsonObject(js=js)
    return js
