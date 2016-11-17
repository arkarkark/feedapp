import os

from oauth2client.contrib.appengine import oauth2decorator_from_clientsecrets
from google.appengine.api import memcache

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
SCOPES = [
  'email',
  'https://www.googleapis.com/auth/blogger'
]

decorator = oauth2decorator_from_clientsecrets(
  filename=CLIENT_SECRETS,
  scope=SCOPES,
  cache=memcache
)
