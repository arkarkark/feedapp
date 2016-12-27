import os

import oauth2client.contrib.appengine
import google.appengine.api

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
