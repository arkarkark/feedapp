#!/usr/bin/python
# Copyright 2010 Alex K (wtwf.com) All rights reserved.

import datetime
import unittest

import sanitizeblogger
import atom

class TestSanitizeBloggerFeed(unittest.TestCase):

  def testFixRelativeUrls(self):
    # TODO(ark): add a bunch of tests for different values for
    #     keep_first and tombstone_days_older
    feed = atom.FeedFromString(open('testdata/samplefeed.xml').read())

    keep_first = 5
    tombstone_days_older = 60

    now = datetime.datetime(2016, 10, 10)
    ans = sanitizeblogger.SanitizeBloggerFeed(feed, keep_first, tombstone_days_older, now=now)

    num_entries = len(ans.entry)
    num_kept    = len([x for x in ans.entry if x.title.text != sanitizeblogger.DELETED])
    num_deleted = len([x for x in ans.entry if x.title.text == sanitizeblogger.DELETED])

    self.assertEqual(num_entries, 24)
    self.assertEqual(num_kept, 1)
    self.assertEqual(num_deleted, 23)

if __name__ == '__main__':
  unittest.main()
