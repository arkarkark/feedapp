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

import gae_memcache_decorator

def find(haystack, *needles):
  result = None
  for needle in needles:
    try:
      result = haystack.get(needle)
    except AttributeError as ae:
      raise ValueError("error: %r no %r in payload %r" %(ae, needle, haystack))

    if not result:
      raise ValueError("no %r in payload %r" %(needle, haystack))
    haystack = result
  return result

class RssFeed(webapp.RequestHandler):
  """Make RSS Feed for a (public) instagram user."""

  def __repr__(self):
    return "instagram.RssFeed"

  def getInstaGraphQl(self, igid, page_type):
    url = "https://www.instagram.com/%s" % igid
    # this is from: https://stackoverflow.com/a/49815744
    result = urlfetch.fetch(url)
    if result.status_code != 200:
      logging.info("Error %r", result.status_code)
      return self.error(result.status_code)

    payload = None

    insta_html = result.content
    insta_html_split = insta_html.split('<script type="text/javascript">window._sharedData = ')
    if len(insta_html_split) > 1:
      insta_html_split_2 = insta_html_split[1].split(';</script>')
      if len(insta_html_split_2) > 1:
        payload = json.loads(insta_html_split_2[0])

    logging.info("DONE!\n%s", json.dumps(payload, sort_keys=True, indent=2, separators=(',', ': ')))

    profile_page = find(payload, "entry_data", page_type)
    graphql = find(profile_page[0], "graphql")
    return graphql

  @gae_memcache_decorator.cached(time=60*60*12)
  def get(self, user):
    """hello"""
    self.response.out.write("<plaintext>%s\n" % str(self.get))
    return

    graphql = self.getInstaGraphQl(user, "ProfilePage")
    user = find(graphql, "user")
    if not user: return
    edges = find(user, "edge_owner_to_timeline_media", "edges")
    if not edges: return


    f = None

    for item in edges:
      item = find(item, "node")
      if not item:
        continue
      if f is None:
        # init the feed.
        title = "%s (@%s)" % (user["full_name"], user["username"])
        f = rss.RSS2(
          title=title,
          link="https://instagram.com/%s" % user["username"],
          description="",
          lastBuildDate=datetime.datetime.now(),
        )

      link = GetLink(item)

      if item["__typename"] == "GraphSidecar":
        logging.info("getting sidecar for %r", item["shortcode"])
        body = self.GetSidecarBody(self.getInstaGraphQl("p/%s" % item["shortcode"], "PostPage"))
      else:
        body = self.GetBody(item)

      try:
        caption = find(find(item, "edge_media_to_caption", "edges")[0], "node", "text")
      except ValueError:
        caption = ""

      body = """%s\n<br>\n%s""" % (body, cgi.escape(caption))

      rss_item = {
        "title": title,
        "link": link,
        "description": body,
        "guid": rss.Guid(item["id"], False),
        "pubDate": datetime.datetime.fromtimestamp(int(item["taken_at_timestamp"])),
      }
      #  if item.get("is_video"):
      #  rss_item["enclosure"] = rss.Enclosure(item["videos"]["standard_resolution"]["url"], 10, "video/mp4")

      f.items.append(rss.RSSItem(**rss_item))

    self.response.headers['Content-Type'] = 'text/xml'
    f.write_xml(self.response.out)

  def GetVideoUrl(self, item):
    ans = item.get("video_url")
    if ans:
      return ans
    shortcode = item["shortcode"]
    # return "VIDEO URL p/%s" % shortcode
    key = "GetVideoUrl:" + shortcode
    ans = memcache.get(key)
    if ans is not None:
      return ans

    graphql = self.getInstaGraphQl("p/%s" % shortcode, "PostPage")

    ans = graphql.get("shortcode_media", {}).get("video_url")
    memcache.set(key, ans)
    return ans

  def GetBody(self, item):
    #  img_src = re.sub(
    #  r'c[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/',
    #  '',
    #  item["thumbnail_resources"][-1]["src"]
    #  )
    link = GetLink(item)
    img_src = item["display_url"]

    width_and_height = """width="%(width)s" height="%(height)s" """ % item["dimensions"]

    media = """<a href="%s"><img %s src="%s"></a>""" % (link, width_and_height, img_src)
    logging.info("is_video %r %r", item.get("is_video"), bool(item.get("is_video")))
    if item.get("is_video"):
      media = """<video %s controls="controls">
                  <source src="%s" type="video/mp4" poster="%s" />
                </video><br>%s<br>""" % (
                  width_and_height,
                  self.GetVideoUrl(item),
                  img_src,
                  media
                )

    return media

  def GetSidecarBody(self, graphql):
    body = []
    edges = find(graphql, "shortcode_media", "edge_sidecar_to_children", "edges")

    for edge in edges:
      body.append(self.GetBody(find(edge, "node")))

    return "\n\n".join(body)


def GetLink(item):
  return "https://www.instagram.com/p/%s" % item["shortcode"]
