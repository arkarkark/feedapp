# Copyright 2011 Alex K (wtwf.com)

__author__ = 'wtwf.com (Alex K)'

import httplib
import json
import logging
import os
import re
import urllib
import urlparse
import xml.etree.ElementTree as ElementTree

from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from google.appengine.ext import webapp
from wtwf import wtwfhandler
from wtwf.WtwfModel import WtwfNdbModel

import config
import searchandreplace

class AllEntities:
  def __getitem__(self, key):
    return key

SRC_RE = re.compile(r"""(?P<pre>\ssrc=["']?)(?P<src>[^ "'>]+)(?P<post>[ "'>])""", re.IGNORECASE)

class ExpandFeed(WtwfNdbModel):
  """Stores Info about feeds that we're serving."""

  TYPE_RSS = 0  # Expand an rss feed
  TYPE_HTML_PAGE = 1  # Take a page and turn it into a rss item
  TYPE_HTML_LIST = 2  # Take a page that contains links to turn into rss items

  name = ndb.StringProperty()
  url = ndb.StringProperty()

  feed_type = ndb.IntegerProperty(default=TYPE_RSS)

  # for HTML_PAGE and HTML_LIST types we need to know where the content starts
  html_begin_str = ndb.StringProperty()
  html_end_str =  ndb.StringProperty()
  html_include_begin = ndb.BooleanProperty(default=False)
  html_include_end = ndb.BooleanProperty(default=False)

  # for HTML_PAGE we need to know what to use as the unique guid from the page
  html_page_guid_re = ndb.StringProperty()

  # The following are for all types
  begin_str = ndb.StringProperty()
  end_str =  ndb.StringProperty()
  include_begin = ndb.BooleanProperty(default=False)
  include_end = ndb.BooleanProperty(default=False)
  title_deduping = ndb.BooleanProperty(default=False)
  replace = ndb.TextProperty()
  absolute_urls = ndb.BooleanProperty(default=False)
  proxy_images = ndb.BooleanProperty(default=False)
  xml_string = ndb.TextProperty()
  last_updated = ndb.DateTimeProperty(auto_now=True)
  last_updated_by = ndb.StringProperty()
  owner = ndb.StringProperty()
  # Automatic Fields
  created = ndb.DateTimeProperty(auto_now_add=True)

  patterns = None

  def GetPatterns(self):
    """Decode the replace TextProperty to a list of searh, replace pairs."""
    if self.patterns:
      return self.patterns

    self.patterns = []
    if self.replace:
      lines = [x.strip() for x in self.replace.split('\n')]
      for line in lines:
        parts = searchandreplace.SplitEscapable(line, '!')
        if len(parts) == 4:
          self.patterns.append((parts[1], parts[2]))
    return self.patterns


class ExpandFeedItem(WtwfNdbModel):
  """Stores Info about a post to a feed.

  Parent is ExpandFeed"""

  parent_model_name = 'ExpandFeed'

  active = ndb.BooleanProperty(default=True)
  title = ndb.StringProperty()
  guid = ndb.StringProperty()
  expanded = ndb.BooleanProperty(default=False)
  link = ndb.StringProperty()
  #  needs_refresh = ndb.BooleanProperty(default=False)
  xml_string = ndb.TextProperty()
  # automatic fields
  last_updated = ndb.DateTimeProperty(auto_now=True)
  created = ndb.DateTimeProperty(auto_now_add=True)

  xml_element = None
  full_html = None

  def ModifyFark(self):
    """Do something special for a fark feed item."""
    el = self.xml_element

    dontdo = re.compile('\[(Photoshop|Caption)\]', re.IGNORECASE)

    link = el.find('link').text
    tit = el.find('title').text
    linkid = link.rsplit('/',1 )[1]
    origlink = 'http://www.fark.com/cgi/go.pl?i=' + linkid
    if not dontdo.search(tit):
      el.find('link').text = origlink
      # now add a link to view comments in the description
      desc = el.find('description').text
      self.SetDescription(desc +
                          ('<p><a href="%s">View Comments</a> ' % link) +
                          ('<a href="%s">View Item</a></p>' % origlink))
    else:
      # add a way to get to the original pic
      desc = el.find('description').text
      # for photoshop contests we want to link to the voting results
      el.find('link').text = ('http://www.fark.com/comments/' +
                              linkid + '?tt=voteresults0')
      self.SetDescription(desc +
                          '<p><a href="%s">View Source</a></p>' % origlink)
    el.find('guid').text = el.find('link').text

  def StartExpandRpc(self):
    rpc = urlfetch.create_rpc()
    rpc.callback = lambda: self.HandleExpandRpcCallback(rpc)
    logging.info('feed: %s loading: %s', self.parent().name, self.link)
    urlfetch.make_fetch_call(rpc, self.link)
    return rpc

  def HandleExpandRpcCallback(self, rpc):
    result = rpc.get_result()
    logging.info('feed: %s loaded(%r): %s',
                 self.parent().name, result.status_code, self.link)
    if result.status_code != 200:
      logging.error('Error status code %r for url %s\n%s]n',
                    result.status_code, self.link, result.content)
      return

    # string out the null char (Oddee had ^@)
    content = result.content.replace(chr(0), '')
    try:
      content = content.decode('utf-8', 'ignore')
    except Exception as e:
      # possibly don't do the ignore above and try 'ISO-8859-1'?
      logging.error('There was a problem utf decoding content from %r %r',
                    self.link, e)
      pass
    self.UpdateDescriptionFromContent(content)
    self.put()

  def UpdateDescriptionFromContent(self, content):
    # parse it
    if self.xml_element is None:
      self.xml_element = ElementTree.fromstring(self.xml_string)
    self.full_html = content
    self.SetDescription(self.Contract(self.full_html))
    self.expanded = True

  def SetDescription(self, description):
    if self.xml_element is None:
      self.xml_element = ElementTree.fromstring(self.xml_string)
    el = EtreeFind(self.xml_element, ('description', 'summary'))
    el.text = description
    self.xml_string = ElementTree.tostring(self.xml_element)

  def GetDescription(self):
    if self.xml_element is None:
      self.xml_element = ElementTree.fromstring(self.xml_string)
    return EtreeFindText(self.xml_element, ('description', 'summary'))

  def Contract(self, content):
    lines = content.split('\n')
    if len(lines) == 1:
      lines = lines[0].split('\r')
    start = 0
    end = -1
    current_line = 0
    ef = self.parent()
    for line in lines:
      if start == 0 and ef.begin_str in line:
        if ef.include_begin:
          start = current_line
        else:
          start = current_line + 1

      if end == -1 and ef.end_str in line:
        if ef.include_end:
          end = current_line + 1
        else:
          end = current_line
      current_line += 1
    content = self.DoReplace(ef, '\n'.join(lines[start:end]))

    if ef.absolute_urls or ef.proxy_images:
      base = self.GetBaseUrl()
      content = self.FixRelativeUrls(base, content)

    if ef.proxy_images:
      content = self.AddProxyToUrls(content)

    logging.info("Contracted down to lines %d to %d\n\n" %
                 (start, end))
    return content

  def GetBaseUrl(self):
    base = self.link
    urlp = urlparse.urlparse(base)
    if urlp.hostname in ('bit.ly', 'www.bit.ly', 'feedproxy.google.com'):
      base = self.ResolveSnippyUrl(base)
    return base

  def ResolveSnippyUrl(self, url):
    try:
      urlp = urlparse.urlparse(url)
      conn = httplib.HTTPConnection(urlp.hostname)
      conn.request('GET', urlp.path)
      r1 = conn.getresponse()
      nurl = r1.getheader('location')
      if nurl:
        return nurl
    except Exception as e:
      logging.error('there was an error resolvig %r: %r', url, e)
      pass
    return url


  def DoReplace(self, ex, content):
    patterns = ex.GetPatterns()
    for (search, replace) in patterns:
      content = re.sub(search, replace, content)
    return content

  def FixRelativeUrls(self, base, txt):
    """Replace all relative urls in txt with absolute urls."""
    return SRC_RE.sub(lambda x: (x.group('pre') +
                                 urlparse.urljoin(base, x.group('src')) +
                                 x.group('post')),
                      txt)


  def AddProxyToUrls(self, txt):
    def FixSingleSrc_(match):
      src = match.group('src')
      ext = os.path.splitext(src)[1]
      if ext.lower() in ('.gif', '.png', '.jpg', '.jpeg'):
        return (match.group('pre') +
                config.image_proxy_url + src +
                match.group('post'))
      else:
        return match.group(0)
    return SRC_RE.sub(FixSingleSrc_, txt)




def EtreeFind(el, names):
  return EtreeFindSomething(el, names, 'find')

def EtreeFindall(el, names):
  return EtreeFindSomething(el, names, 'findall')


def EtreeFindSomething(el, names, find_type):

  namespaces = ('',
                '{http://www.w3.org/2005/Atom}',
                '{http://purl.org/rss/1.0/}')
  if isinstance(names, basestring):
    names = [names]
  if type(names) in (list, tuple, set):
    names = tuple(names)
  for name in names:
    for namespace in namespaces:
      if find_type == 'find':
        ans = el.find(namespace + name)
        if ans is not None:
          return ans
      else:
        ans = el.findall(namespace + name)
        if len(ans) > 0:
          return ans

  logging.info('failed to find %r', names)
  if find_type == 'find':
    return None
  else:
    return []


def EtreeFindText(el, names, default=None):
  el = EtreeFind(el, names)
  if el is not None:
    return el.text
  return default


class ExpandHandler(webapp.RequestHandler):
  """Fetch a feed and then fetch all the items for that feed."""

  def isDebug(self):
    return self.request.get('debug')

  def debug(self, fmt, *args):
    if self.isDebug():
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.out.write(fmt % args)
      self.response.out.write('\n')

  def get(self, ex_id):
    ex = None
    try:
      ex = ExpandFeed.get_by_id(long(ex_id))
    except ValueError:
      pass
    if ex is None:
      logging.info('looking for %r as a ExpandFeed.name', ex_id)
      ex_id = urllib.unquote(ex_id)
      if ex_id.endswith('.xml'):
        ex_id = ex_id[0:-4]
      ex = ExpandFeed.query(ExpandFeed.name == ex_id).get()

    if not ex:
      self.error(404)
      return

    rpc = urlfetch.create_rpc()
    urlfetch.make_fetch_call(rpc, ex.url)

    # load all the latest items for this feed...
    items_query = ExpandFeedItem.query(ExpandFeedItem.active > False,
                                       ancestor=ex)

    logging.info('found items')
    items_by_title = {}
    items_by_guid = {}

    for item in items_query:
      items_by_guid[item.guid] = item
      if item.title in items_by_title:
        # use the newest one
        old = items_by_title[item.title]
        if item.last_updated > old.last_updated:
          items_by_title[item.title] = item
      else:
        items_by_title[item.title] = item

    logging.info('found %d previous items by guid and %d by title',
                 len(items_by_guid), len(items_by_title))

    # now get the text from the async loaded url and parse it and deal with it
    result = rpc.get_result()
    if result.status_code != 200:
      logging.error('Got unexpected status code: %r', result.status_code)
      self.error(501)
      return

    # parse it
    logging.info('Got feed body from:%r', ex.url)

    parser = ElementTree.XMLParser()
    parser.parser.UseForeignDTD(True)
    parser.entity = AllEntities()

    root = ElementTree.fromstring(result.content, parser=parser)
    logging.info('Parsed')

    rpcs = []
    items = []
    feed_type = None

    for channel in EtreeFindall(root, 'channel'):
      for item in list(EtreeFindall(channel, 'item')):
        feed_type = 'rss'
        self.ProcessItem(item, ex, items, rpcs, items_by_title, items_by_guid)
        channel.remove(item)
        if self.isDebug():
          break

    if not feed_type:
      # maybe it's an atom feed
      for item in EtreeFindall(root, 'entry'):
        feed_type = 'atom'
        self.ProcessItem(item, ex, items, rpcs, items_by_title, items_by_guid)
        root.remove(item)
        if self.isDebug():
          break

    if not feed_type:
      # maybe it's an rdf feed (like the oatmeal)
      for item in EtreeFindall(root, 'item'):
        logging.info('item  = %r', item)
        feed_type = 'rdf'
        self.ProcessItem(item, ex, items, rpcs, items_by_title, items_by_guid)
        root.remove(item)
        if self.isDebug():
          break


    # now save this feed's text to the ExpandFeed
    self.debug('Saving updated xml_string for %r %r', feed_type, ex.name)
    ex.xml_string = ElementTree.tostring(root)
    ex.put()

    # TODO(ark) mark the non-active ExpandFeedItems
    # ***

    self.debug('Waiting for %d RPCs', len(rpcs))
    for rpc in rpcs:
      rpc.wait()

    # TODO(ark) handle multiple channels
    if feed_type == 'rss':
      channel = root.find('channel')
      for fi in items:
        channel.append(fi.xml_element)
    elif feed_type in ('atom', 'rdf'):
      for fi in items:
        root.append(fi.xml_element)
    else:
      logging.error('unknown feed_type: %r',  feed_type)

    if not self.isDebug():
      self.response.headers['Content-Type'] = 'text/xml'
    self.response.out.write(ElementTree.tostring(root))


  def ProcessItem(self, item, ex, items, rpcs, items_by_title, items_by_guid):
    guid = EtreeFindText(item, ('guid', 'id', 'link'))
    title = EtreeFindText(item, 'title')
    linkel = EtreeFind(item, 'link')
    link = None
    if linkel.text:
      link = linkel.text
    if not link:
      link = linkel.get('href')
    self.debug('Expanding: %s', link)
    logging.info('guid is %s for %s', guid, link)

    fi = items_by_guid.get(guid, None)
    if fi is None and ex.title_deduping:
      fi = items_by_title.get(title, None)
      if fi is not None:
        fi.expanded = False
    if fi is None:
      fi = ExpandFeedItem(parent=ex, guid=guid, title=title, link=link)
      fi.xml_element = item
    else:
      fi.xml_element = ElementTree.fromstring(fi.xml_string)
    if not fi.expanded or self.isDebug():
      if ex.name == 'fark':  # super special case (sorry)
        fi.ModifyFark()
      else:
        rpcs.append(fi.StartExpandRpc())
    items.append(fi)


class ExpandItemDataHandler(wtwfhandler.GetGenericDataHandler(ExpandFeedItem)):

  def get(self):
    self.AssertAllowed()
    # could be a query or a request for a specific (or new) expand obj

    ei_id = self.request.get('id')
    parent_key = ndb.Key('ExpandFeed', long(self.request.get('parent_id')))

    if ei_id:
      ei_id = long(ei_id)
      item = ExpandFeedItem.get_by_id(ei_id, parent=parent_key)

      ans = item.AsJsonObject()
      # now add a body
      ans['body'] = item.GetDescription()
    else:
      # we want all of them for this feed
      all_items = ExpandFeedItem.query(ExpandFeedItem.active > False,
                                       ancestor=parent_key)
      ans = [exi.AsJsonObject() for exi in all_items]
    self.response.headers['Content-Type'] = 'text/json'
    self.response.out.write(json.dumps(ans, default=wtwfhandler.JsonPrinter))


  def post(self):
    self.AssertAllowed()

    ei_id = long(self.request.get('id'))
    parent_key = ndb.Key('ExpandFeed', long(self.request.get('parent_id')))

    item = ExpandFeedItem.get_by_id(ei_id, parent=parent_key)
    ex = item.parent()
    ans = json.loads(self.request.body)
    item.UpdateFromJsonObject(ans)
    ex.UpdateFromJsonObject(ans['expand'])

    if self.request.get('action') == 'preview':
      # Don't update the object at all, just the json and send it back.
      if 'full_html' not in ans:
        rpc = item.StartExpandRpc()
        rpc.wait()
        ans['full_html'] = item.full_html
      ans['body'] = item.Contract(ans['full_html'])

    self.response.out.write(json.dumps(ans,
                                       default=wtwfhandler.JsonPrinter))
