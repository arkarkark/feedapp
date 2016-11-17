

import logging
import pickle
import re
import json

import auth
import sanitizeblogger

import bloggerclient

from google.appengine.api import users
from google.appengine.ext import db
from wtwf import wtwfhandler
from wtwf.WtwfModel import WtwfModel

RE_VALID_NAME = re.compile(r'^[a-zA-Z0-9_-]+$')

class AuthedFeed(WtwfModel):
  """Stores Info about feeds that we're serving."""

  blog_id = db.IntegerProperty()
  name = db.StringProperty()
  oauth_token = db.TextProperty()
  tombstone_days_older = db.IntegerProperty()
  keep_first = db.IntegerProperty()
  # optional fields
  last_updated = db.DateTimeProperty(auto_now=True)
  last_updated_by = db.EmailProperty()
  redirect_url = db.StringProperty()
  # automatic fields
  created = db.DateTimeProperty(auto_now_add=True)

class BloggerHandler(wtwfhandler.WtwfHandler):
  """Used to make sure we have an oauth token."""

  @auth.decorator.oauth_required
  def get(self):
    self.redirect('/blogger/')

class BloggerDataHandler(wtwfhandler.GetGenericDataHandler(AuthedFeed)):
  """Main handler. If user is not logged in via OAuth it will display welcome
  page. In other case user's blogs on Blogger will be displayed."""

  def get(self):
    self.AssertAllowed()

    blogger = bloggerclient.BloggerClient(auth.decorator)

    authed_feeds = AuthedFeed.all()
    authed_feeds = dict(zip([x.blog_id for x in authed_feeds], authed_feeds))

    blogList = blogger.blogsListByUser()
    blogs = []
    for entry in blogList.items:
      blog = {
        'blog_id': entry.id,
        'title': entry.name,
        'link': entry.url,
        'published': entry.published,
        'updated': entry.updated,
        'feed_button': 'Create',
      }
      authed_feed = authed_feeds.get(int(entry.id))

      if authed_feed:
        blog.update({
          'name': authed_feed.name,
          'redirect_url': authed_feed.redirect_url,
          'tombstone_days_older': authed_feed.tombstone_days_older,
          'keep_first': authed_feed.keep_first,
          'feed_button': 'Edit'})
      blogs.append(blog)
    self.response.out.write(json.dumps(blogs, default=wtwfhandler.JsonPrinter))


  def post(self):
    self.AssertAllowed()

    blog_id = int(self.request.get('blog_id'))

    json_obj = json.loads(self.request.body)
    ex = AuthedFeed.all().filter('blog_id =', blog_id).get()
    if not ex:
      logging.info('Making New AuthedFeed for %r', blog_id)
      self.initOauth()
      ex = AuthedFeed(blog_id=blog_id,
                      oauth_token=pickle.dumps(self.oauth_token))

    ex.UpdateFromJsonObject(json_obj)
    ex.last_updated_by = users.get_current_user().email()
    key = ex.put()
    self.response.out.write(json.dumps(ex.AsJsonObject(id=key.id()),
                                       default=wtwfhandler.JsonPrinter))


class GetFeedHandler(wtwfhandler.WtwfHandler):
  """Main handler. If user is not logged in via OAuth it will display welcome
  page. In other case user's blogs on Blogger will be displayed."""

  def get(self, name):  # pylint: disable=W0221
    afeed = AuthedFeed.all().filter('name = ', name).get()

    oauth_token = pickle.loads(str(afeed.oauth_token))
    self.client.blogger.override_token = oauth_token
    feed = self.client.blogger.Get('/feeds/%d/posts/default' % afeed.blog_id)
    feed = sanitizeblogger.SanitizeBloggerFeed(feed,
                                               afeed.keep_first,
                                               afeed.tombstone_days_older)
    self.response.headers['Content-Type'] = 'text/xml'
    self.response.out.write(str(feed))
