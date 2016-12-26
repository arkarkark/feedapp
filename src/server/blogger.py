import googleapiclient.discovery
import logging
import pickle
import re
import json
import collections
import datetime

import auth
import sanitizeblogger
import oauth2client
import httplib2

import PyRSS2Gen as rss

from google.appengine.api import users
from google.appengine.ext import ndb
from wtwf import wtwfhandler
from wtwf.WtwfModel import WtwfModel

RE_VALID_NAME = re.compile(r'^[a-zA-Z0-9_-]+$')

def getBlogger(credentials=None):
  if credentials:
    http = credentials.authorize(httplib2.Http())
  else:
    http = auth.decorator.http()
  return googleapiclient.discovery.build("blogger", "v3", http=http)

class JsonStruct:
  @staticmethod
  def fromDict(d):
    if d:
      return JsonStruct(**d)
    else:
      return JsonStruct(**{})

  @staticmethod
  def fromJsonString(s):
    return JsonStruct(**json.loads(s))

  def __init__(self, **entries):
    self.__dict__.update(entries)
  def __getattr__(self, key):
    return self.__dict__.get(key, None)
  def to_json(self):
    return json.dumps(self.__dict__)
  def is_empty(self):
    return len(self.__dict__) == 0
  def update(self, d):
    if hasattr(d, "__dict__"):
      d = d.__dict__
    self.__dict__.update(d)
    return self

class AuthedFeed(ndb.Model):
  """Stores Info about feeds that we're serving."""

  blog_id = ndb.IntegerProperty()
  name = ndb.StringProperty()
  title = ndb.StringProperty()
  url = ndb.StringProperty()
  credentials = oauth2client.contrib.appengine.CredentialsNDBProperty()
  tombstone_days_older = ndb.IntegerProperty()
  keep_first = ndb.IntegerProperty()
  # optional fields
  last_updated = ndb.DateTimeProperty(auto_now=True)
  last_updated_by = ndb.StringProperty()
  redirect_url = ndb.StringProperty()
  # automatic fields
  created = ndb.DateTimeProperty(auto_now_add=True)

  def to_json_object(self):
    return {
      "blog_id": self.blog_id,
      "name": self.name,
      "title": self.title,
      "url": self.url,
      "tombstone_days_older": self.tombstone_days_older,
      "keep_first": self.keep_first,
      "redirect_url": self.redirect_url,
    }


class BloggerHandler(wtwfhandler.WtwfHandler):
  """Used to make sure we have an oauth token."""

  @auth.decorator.oauth_required
  def get(self):
    self.redirect('/blogger/')

def blogObjectFromBlog(entry):
  return {
    'blog_id': entry.id,
    'title': entry.name,
    'url': entry.url,
    'published': entry.published,
    'updated': entry.updated,
    'feed_button': 'Create',
  }

class BloggerDataHandler(wtwfhandler.GetGenericDataHandler(AuthedFeed)):
  """Main handler. If user is not logged in via OAuth it will display welcome
  page. In other case user's blogs on Blogger will be displayed."""

  @auth.decorator.oauth_required
  def get(self):
    self.AssertAllowed()

    blogs = []

    authed_feeds = AuthedFeed.query()
    authed_feeds = dict(zip([x.blog_id for x in authed_feeds], authed_feeds))

    logging.info("authed feeds %r", len(authed_feeds))

    blogger = getBlogger()
    items = dict(blogger.blogs().listByUser(userId="self").execute().items())["items"]

    for entry in items:
      entry = JsonStruct.fromDict(entry)
      # print "entry %r" % entry.to_json()
      blog = blogObjectFromBlog(entry)

      authed_feed = authed_feeds.get(entry.id)

      if authed_feed:
        del authed_feeds[entry.id]
        blog.update(authed_feed.to_json_object())
        blog.feed_button = "Edit"
      blogs.append(blog)

    logging.info("leftover authed feeds %r", len(authed_feeds))

    for item in authed_feeds.values():
      logging.info("leftover item %r", item.to_json_object())
      item = item.to_json_object()
      item["feed_button"] = "Edit"
      blogs.append(item)

    self.response.out.write(json.dumps(blogs, default=wtwfhandler.JsonPrinter))

  @auth.decorator.oauth_required
  def post(self):
    self.AssertAllowed()

    req = JsonStruct.fromJsonString(self.request.body)

    authed_feed = None

    if req.id:
      authed_feed = authed_feeds.get(req.id)
    else:
      if req.blog_id:
        authed_feed = AuthedFeed.query(AuthedFeed.blog_id == long(req.blog_id)).get()
      else:
        # get it from the blogger api
        if req.blog_url is None:
          return self.error(422)
        blogger = getBlogger()
        blog = JsonStruct.fromDict(dict(blogger.blogs().getByUrl(url=req.blog_url).execute()))
        if blog.is_empty():
          return self.error(404)
        req.blog_id = blog.id
        req.title = blog.name
        authed_feed = AuthedFeed.query(AuthedFeed.blog_id == long(req.blog_id)).get()
      if not authed_feed:
        name = req.name or blog.url
        name = re.sub(r'(http://|www\.|\.com|\.blogspot|\W)', '', name)
        authed_feed = AuthedFeed(
          blog_id=long(req.blog_id),
          name=name,
          title=req.title,
          url=blog.url,
          credentials = auth.decorator.credentials,
        )

    if authed_feed is None:
      return self.error(404)
    authed_feed.put()
    req.update(authed_feed.to_json_object())
    req.feed_button = "Edit"
    logging.info("found id %r in %r", id, req.to_json())

    self.response.out.write(req.to_json())

class GetFeedHandler(wtwfhandler.WtwfHandler):
  """Get the RSS feed for an AuthedFeed."""

  def get(self, name):  # pylint: disable=W0221
    afeed = AuthedFeed.query(AuthedFeed.name == name).get()

    blogger = getBlogger(afeed.credentials)

    blog = JsonStruct.fromDict(blogger.blogs().get(blogId=afeed.blog_id, maxPosts=0, view="READER").execute())
    posts = blogger.posts().list(blogId=afeed.blog_id, orderBy="published", status="live", view="READER")
    posts = dict(posts.execute().items())["items"]

    f = rss.RSS2(
      description=blog.name,
      lastBuildDate = datetime.datetime.now(),
      link=blog.url,
      title=blog.title,
    )

    for post in blog.posts["items"]:
      post = JsonStruct.fromDict(post)

      # TODO sanitize per the keep_fisrt and tombstone_days_older settings

      f.items.append(rss.RSSItem(
        description = post.content,
        guid = post.id,
        link = post.url,
        pubDate = post.published,
        title = post.title,
      ))
    self.response.headers['Content-Type'] = 'text/XML'
    f.write_xml(self.response.out)
