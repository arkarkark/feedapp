# Copyright 2017 Alex K (wtwf.com)

__author__ = 'wtwf.com (Alex K)'

import datetime
import json
import logging
import os

import PyRSS2Gen as rss

from google.appengine.api import urlfetch
from google.appengine.ext import webapp

class RssFeed(webapp.RequestHandler):
  """Make RSS Feed for a (public) instagram user."""

  def get(self, user):

    url = "https://www.instagram.com/%s/media/" % user
    logging.info("fetching: %r", url)
    result = urlfetch.fetch(url)
    if result.status_code != 200:
      return self.error(result.status_code)

    media = json.loads(result.content)

    if "items" not in media or len(media["items"]) == 0:
      return self.error(404)

    f = None
    for item in media["items"]:
      if f is None:
        user = item["user"]
        f = rss.RSS2(
          title="%s (@%s)" % (user["full_name"], user["username"]),
          link="https://instagram.com/%s" % user["username"],
          description="",
          lastBuildDate=datetime.datetime.now(),
        )

      body = """<a href="%s"><img src="%s"></a>""" % (
        item["link"],
        item["images"]["standard_resolution"]["url"]
      )
      f.items.append(rss.RSSItem(
        title=item["caption"]["text"],
        link=item["link"],
        description=body,
        guid=rss.Guid(item["id"], False),
        pubDate=datetime.datetime.fromtimestamp(int(item["created_time"])),
      ))

    self.response.headers['Content-Type'] = 'text/xml'
    f.write_xml(self.response.out)
