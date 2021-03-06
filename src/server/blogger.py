import collections
import datetime
import json
import logging
import pytz
import random
import re
import string

import auth
import oauth2client
import httplib2

import PyRSS2Gen as rss

import dateutil.parser
import googleapiclient.discovery
import wtwf.wtwfhandler
import google.appengine.ext

RE_VALID_NAME = re.compile(r'^[a-zA-Z0-9_-]+$')

def getBlogger(credentials=None):
  if credentials:
    http = credentials.authorize(httplib2.Http())
  else:
    http = auth.decorator.http()
  return googleapiclient.discovery.build('blogger', 'v3', http=http)

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
    if hasattr(d, '__dict__'):
      d = d.__dict__
    self.__dict__.update(d)
    return self
  def dict(self):
    return self.__dict__

class AuthedFeed(google.appengine.ext.ndb.Model):
  """Stores Info about feeds that we're serving."""

  blog_id = google.appengine.ext.ndb.IntegerProperty()
  name = google.appengine.ext.ndb.StringProperty()
  title = google.appengine.ext.ndb.StringProperty()
  url = google.appengine.ext.ndb.StringProperty()
  credentials = oauth2client.contrib.appengine.CredentialsNDBProperty()
  tombstone_days_older = google.appengine.ext.ndb.IntegerProperty()
  keep_first = google.appengine.ext.ndb.IntegerProperty()
  # optional fields
  last_updated = google.appengine.ext.ndb.DateTimeProperty(auto_now=True)
  last_updated_by = google.appengine.ext.ndb.StringProperty()
  redirect_url = google.appengine.ext.ndb.StringProperty()
  # automatic fields
  created = google.appengine.ext.ndb.DateTimeProperty(auto_now_add=True)

  def to_json_object(self):
    return {
      'blog_id': self.blog_id,
      'name': self.name,
      'title': self.title,
      'url': self.url,
      'tombstone_days_older': self.tombstone_days_older,
      'keep_first': self.keep_first,
      'redirect_url': self.redirect_url,
    }


class BloggerHandler(wtwf.wtwfhandler.WtwfHandler):
  """Used to make sure we have an oauth token."""

  @auth.decorator.oauth_required
  def get(self):
    credentials = auth.decorator.credentials
    if credentials.refresh_token is None:
      logging.error('Got credentials with no refresh_token. '
                    'Flush memcache and remove all CredentialsModel from the datastore and try again.')
      return self.error(500)
    else:
      logging.info('credentials look good')

    self.redirect('/blogger/')


class BloggerDataHandler(wtwf.wtwfhandler.GetGenericDataHandler(AuthedFeed)):
  """Main handler. If user is not logged in via OAuth it will display welcome
  page. In other case user's blogs on Blogger will be displayed."""

  @auth.decorator.oauth_required
  def get(self):
    self.AssertAllowed()

    blog_id = self.request.params.get("blog_id")
    if blog_id:
      afeed = AuthedFeed.query(AuthedFeed.blog_id == long(blog_id)).get()
      if afeed:
        self.response.headers['Content-Type'] = 'text/json'
        self.response.out.write(json.dumps(afeed.to_json_object()))
      else:
        self.error(404)
      return

    blogs = []

    authed_feeds = AuthedFeed.query()
    authed_feeds = dict(zip([long(x.blog_id) for x in authed_feeds], authed_feeds))

    logging.info('authed feeds %r', len(authed_feeds))

    blogger = getBlogger()
    items = dict(blogger.blogs().listByUser(userId='self').execute().items())['items']

    for entry in items:
      blog = JsonStruct.fromDict({
        'blog_id': long(entry['id']),
        'title': entry['name'],
        'url': entry['url']
      })

      authed_feed = authed_feeds.get(blog.blog_id)
      if authed_feed:
        del authed_feeds[blog.blog_id]
        blog.update(authed_feed.to_json_object())
      blogs.append(blog.dict())

    logging.info('leftover authed feeds %r', len(authed_feeds))

    for item in authed_feeds.values():
      item = item.to_json_object()
      blogs.append(item)

    self.response.out.write(json.dumps(blogs, default=wtwf.wtwfhandler.JsonPrinter))

  @auth.decorator.oauth_required
  def post(self):
    self.AssertAllowed()

    req = JsonStruct.fromJsonString(self.request.body)

    authed_feed = None

    if req.blog_id:
      authed_feed = AuthedFeed.query(AuthedFeed.blog_id == long(req.blog_id)).get()
    else:
      # get it from the blogger api
      if req.url is None:
        return self.error(422)
      blogger = getBlogger()
      blog = JsonStruct.fromDict(dict(blogger.blogs().getByUrl(url=req.url).execute()))
      if blog.is_empty():
        return self.error(404)
      req.blog_id = blog.id
      req.title = blog.name
      authed_feed = AuthedFeed.query(AuthedFeed.blog_id == long(req.blog_id)).get()
    if not authed_feed:
      if not req.name:
        req.name = re.sub(r'(http://|blog\.|www\.|\.com|\.blogspot|\W)', '', req.url) + '_'
        req.name += ''.join(random.SystemRandom().choice(string.letters + string.digits) for _ in range(8))

      credentials = auth.decorator.credentials
      if credentials.refresh_token is None:
        logging.error('Trying to store AuthedFeed credentials with no refresh_token. '
                      'Flush memcache and remove all CredentialsModel from the datastore and try again.')
        return self.error(500)

      authed_feed = AuthedFeed(
        blog_id=long(req.blog_id),
        name=req.name,
        title=req.title,
        url=req.url,
        credentials=credentials,
      )

    if authed_feed is None:
      return self.error(404)

    for key, value in req.dict().items():
      setattr(authed_feed, key, value)
    authed_feed.put()
    req.update(authed_feed.to_json_object())

    self.response.out.write(req.to_json())

  def delete(self):
    self.AssertAllowed()

    blog_id = self.request.params.get("blog_id")
    if blog_id:
      afeed = AuthedFeed.query(AuthedFeed.blog_id == long(blog_id)).get()
      if afeed:
        afeed.key.delete()
        return

    self.error(404)


class GetFeedHandler(wtwf.wtwfhandler.WtwfHandler):
  """Get the RSS feed for an AuthedFeed."""

  def get(self, name):  # pylint: disable=W0221
    afeed = AuthedFeed.query(AuthedFeed.name == name).get()

    blogger = getBlogger(afeed.credentials)

    blog = JsonStruct.fromDict(blogger.blogs().get(blogId=afeed.blog_id, maxPosts=0, view='READER').execute())
    posts = blogger.posts().list(blogId=afeed.blog_id, orderBy='published', status='live', view='READER')
    posts = dict(posts.execute().items())['items']

    f = rss.RSS2(
      description=blog.name,
      lastBuildDate = datetime.datetime.now(),
      link=blog.url,
      title=blog.title,
    )

    if afeed.keep_first:
      posts = posts[0:afeed.keep_first]

    for post in posts:
      post = JsonStruct.fromDict(post)

      # TODO sanitize per the keep_fisrt and tombstone_days_older settings
      if afeed.tombstone_days_older:
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        published = dateutil.parser.parse(post.published)
        age = (now - published).days
        if age > afeed.tombstone_days_older:
          logging.info("Feed %r Removing post %d days old:%r", name, age, post.title)
          post.title = post.content = 'This post is no longer available.'

      f.items.append(rss.RSSItem(
        description = post.content,
        guid = post.id,
        link = post.url,
        pubDate = post.published,
        title = post.title,
      ))
    self.response.headers['Content-Type'] = 'text/XML'
    f.write_xml(self.response.out)
