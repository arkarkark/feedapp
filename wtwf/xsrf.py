# Copyright 2009 Alex K (wtwf.com) All rights reserved.

__author__ = 'wtwf.com (Alex K)'

import base64
import hmac
import time

SEP = '^'
# Only valid for 1 day
DEFAULT_TIMEOUT = 24 * 60 * 60


class Error(Exception):
  """Something is wrong with the token."""

def GenerateXsrfToken(site_key, action, user, token_time=None):
  token_time = long(token_time or time.time())
  h = hmac.new(site_key)
  h.update(action)
  h.update(SEP)
  h.update(user)
  h.update(SEP)
  h.update(str(token_time))

  return base64.urlsafe_b64encode('%s%s%d' % (h.digest(), SEP, token_time))

def ValidateXsrfToken(token, site_key, action, user):
  # find the time of the token
  decoded_token = base64.urlsafe_b64decode(token)
  t = long(decoded_token[decoded_token.rfind(SEP) + 1:])
  now = long(time.time())

  # work out what the token should be
  expected = GenerateXsrfToken(site_key, action, user, token_time=t)

  # compare them, but compare everything to avoid timing attacks
  good = len(expected) == len(token)
  for x in range(min(len(expected), len(token))):
    if expected[x] != token[x]:
      good = False

  if not good:
    raise Error('invalid token')

  # Is this within the permitted time range
  if now - t > DEFAULT_TIMEOUT:
    raise Error('token is too old')

  return True
