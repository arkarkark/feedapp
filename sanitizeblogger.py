#!/usr/bin/python
# Copyright 2010 Alex K (wtwf.com) All rights reserved.
# $Id: feedMaker,v 1.6 2008-05-07 21:24:50 ark Exp $

__author__ = 'wtwf.com (Alex K)'

import datetime

DELETED = 'This post has been deleted.'

def SanitizeBloggerFeed(feed, keep_first, tombstone_days_older, now=None):
  # now filter the feed
  count = 0
  for entry in feed.entry[:]:
    if (entry.control and
        entry.control.draft and
        entry.control.draft.text != "no"):
      feed.entry.remove(entry)
      continue
    count += 1
    # TODO(ark): yes I know this ignores timezones and other stuff
    if now is None:
      now = datetime.datetime.now()
    age = (now - datetime.datetime.strptime(entry.updated.text[0:19], '%Y-%m-%dT%H:%M:%S')).days

    if ((keep_first and
         keep_first < count) or
        (tombstone_days_older and
         tombstone_days_older < age)):
      entry.title.text = DELETED
      entry.content.text = DELETED
  return feed
