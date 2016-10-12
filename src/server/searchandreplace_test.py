#!/usr/bin/python
# Copyright 2010 Alex K (wtwf.com) All rights reserved.

import unittest

import searchandreplace

class TestExpand(unittest.TestCase):

  def testSplitEscapable(self):
    tests = [('lulu', ['lulu']),
             ('lulu!', ['lulu', '']),
             ('lulu\\!', ['lulu!']),
             ('!hello!world!', ['', 'hello', 'world', '']),
             ('!hello\\!!world!', ['', 'hello!', 'world', ''])]

    for src, out in tests:
      self.assertEqual(out, searchandreplace.SplitEscapable(src, '!'))

if __name__ == '__main__':
  unittest.main()
