# Copyright 2011 Alex K (wtwf.com)

# based on code by 'wiktorgworek@google.com (Wiktor Gworek)'
__author__ = 'wtwf.com (Alex K)'

# If you want to check this with pychecker on osx you can do this...

# export PYTHONPATH=$PYTHONPATH:/usr/local/google_appengine/
# export PYTHONPATH=$PYTHONPATH:/usr/local/google_appengine/lib/yaml/lib/

from google.appengine.ext import vendor

vendor.add('lib')

from google.appengine.ext import webapp

from wtwf import wtwfhandler
from crud import crud_handler

import blogger
import expand
import mail
import auth
import gps

app = webapp.WSGIApplication([
  ('/data/gps.*', gps.Demo),
  ('/data/blogger/oauth', blogger.BloggerHandler),
  ('/data/blogger/blog', blogger.BloggerDataHandler),
  (r'/public/data/blogger/feed/(\w+)', blogger.GetFeedHandler),
  (r'/mailfeed/([a-zA-Z0-9_-]+)', mail.FeedFromEmail),
  # ('/expand/([a-zA-Z0-9_.%-]+)', expand.ExpandHandler),
  # ('/data/expand/feed.json', crud_handler.GetCrudHandler(expand.ExpandFeed)),
  # ('/data/expand/item.json', expand.ExpandItemDataHandler),
  ('/data/mail/feed.json', crud_handler.GetCrudHandler(mail.MailFeed)),
  ('/data/mail/item.json', mail.MailItemDataHandler),
  ('/data/user/user.json', wtwfhandler.UserHandler),
  ('/data/setupdemo', mail.SetupDemo),
  (r'/_ah/mail/(.+)', mail.EmailToFeed),
  (auth.decorator.callback_path, auth.decorator.callback_handler())
])
