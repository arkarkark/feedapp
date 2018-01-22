# Copyright 2017 Alex K (wtwf.com)

__author__ = 'wtwf.com (Alex K)'

import cgi
import datetime
import json
import logging
import re

import PyRSS2Gen as rss

from google.appengine.api import urlfetch
from google.appengine.ext import webapp

class RssFeed(webapp.RequestHandler):
  """Make RSS Feed for a (public) instagram user."""

  def get(self, user):
    url = "https://websta.me/rss/n/%s" % user
    self.redirect(url)
    return

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
        title = "%s (@%s)" % (user["full_name"], user["username"])
        f = rss.RSS2(
          title=title,
          link="https://instagram.com/%s" % user["username"],
          description="",
          lastBuildDate=datetime.datetime.now(),
        )

      img_src = re.sub(
        r'c[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/',
        '',
        item["images"]["standard_resolution"]["url"]
      )

      media = """<a href="%s"><img src="%s"></a>""" % (item["link"], img_src)
      if item["type"] == "video":
        media = """<video width="%s" height="%s" controls="controls">
                    <source src="%s" type="video/mp4" poster="%s" />
                  </video><br>%s<br>""" % (
                    item["videos"]["standard_resolution"]["width"],
                    item["videos"]["standard_resolution"]["height"],
                    item["videos"]["standard_resolution"]["url"],
                    img_src,
                    media
                  )

      body = """%s<br>%s""" % (media, cgi.escape((item.get("caption") or {}).get("text", "")))

      rss_item = {
        "title": title,
        "link": item["link"],
        "description": body,
        "guid": rss.Guid(item["id"], False),
        "pubDate": datetime.datetime.fromtimestamp(int(item["created_time"])),
      }
      if item["type"] == "video":
        rss_item["enclosure"] = rss.Enclosure(item["videos"]["standard_resolution"]["url"], 10, "video/mp4")

      f.items.append(rss.RSSItem(**rss_item))

    self.response.headers['Content-Type'] = 'text/xml'
    f.write_xml(self.response.out)
