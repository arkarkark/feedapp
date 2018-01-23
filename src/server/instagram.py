# Copyright 2017 Alex K (wtwf.com)

__author__ = 'wtwf.com (Alex K)'

import cgi
import datetime
import json
import logging
import re

import PyRSS2Gen as rss

from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.ext import webapp

class RssFeed(webapp.RequestHandler):
  """Make RSS Feed for a (public) instagram user."""

  def get(self, user):
    #  url = "https://websta.me/rss/n/%s" % user
    #  self.redirect(url)
    #  return

    url = "https://www.instagram.com/%s/?__a=1" % user
    logging.info("fetching: %r", url)
    result = urlfetch.fetch(url)
    if result.status_code != 200:
      return self.error(result.status_code)

    payload = json.loads(result.content)

    user = payload.get("user")
    if not user:
      logging.info("no user in payload")
      return self.error(404)

    media = user.get("media")
    if not media:
      logging.info("no media in user")
      return self.error(404)

    nodes = media.get("nodes")

    if not nodes:
      logging.info("no nodes in media in user")
      return self.error(404)

    f = None

    for item in nodes:
      if f is None:
        title = "%s (@%s)" % (user["full_name"], user["username"])
        f = rss.RSS2(
          title=title,
          link="https://instagram.com/%s" % user["username"],
          description="",
          lastBuildDate=datetime.datetime.now(),
        )

      #  img_src = re.sub(
      #  r'c[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/',
      #  '',
      #  item["thumbnail_resources"][-1]["src"]
      #  )
      img_src = item["display_src"]

      link = "https://instagram.com/p/%s" % item["code"]

      width_and_height = """width="%(width)s" height="%(height)s" """ % item["dimensions"]

      media = """<a href="%s"><img %s src="%s"></a>""" % (link, width_and_height, img_src)
      if item.get("is_video"):
        media = """<video %s controls="controls">
                    <source src="%s" type="video/mp4" poster="%s" />
                  </video><br>%s<br>""" % (
                    width_and_height,
                    GetVideoUrl(link),
                    img_src,
                    media
                  )

      body = """%s<br>%s""" % (media, cgi.escape(item.get("caption")))

      rss_item = {
        "title": title,
        "link": link,
        "description": body,
        "guid": rss.Guid(item["id"], False),
        "pubDate": datetime.datetime.fromtimestamp(int(item["date"])),
      }
      #  if item.get("is_video"):
      #  rss_item["enclosure"] = rss.Enclosure(item["videos"]["standard_resolution"]["url"], 10, "video/mp4")

      f.items.append(rss.RSSItem(**rss_item))

    self.response.headers['Content-Type'] = 'text/xml'
    f.write_xml(self.response.out)

def GetVideoUrl(link):
  key = "GetVideoUrl:" + link
  ans = memcache.get(key)
  if ans is not None:
    return ans

  url = "%s/?__a=1" % link
  logging.info("fetching: %r", url)
  result = urlfetch.fetch(url)
  payload = json.loads(result.content)

  ans = payload.get("graphql", {}).get("shortcode_media", {}).get("video_url")
  memcache.set(key, ans)
  return ans
