import os
import json
import logging

import oauth2client.contrib.appengine
import google.appengine.api
import googlemaps

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
SCOPES = [
  'email',
  'https://www.googleapis.com/auth/blogger'
]

decorator = oauth2client.contrib.appengine.OAuth2DecoratorFromClientSecrets(
  filename=CLIENT_SECRETS,
  scope=SCOPES,
  cache=google.appengine.api.memcache,
  prompt="consent",
)


API_KEYS_FILE = os.path.join(os.path.dirname(__file__), 'api_keys.json')
api_keys = json.load(open(API_KEYS_FILE))

googlemaps = googlemaps.Client(key=api_keys["googlemaps"])

logging.info("API KEY IS %r", api_keys["googlemaps"])
