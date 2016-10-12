import gdata.auth
import gdata.blogger.service

# You can get the consumer key and secret from
# https://www.google.com/accounts/ManageDomains

SETTINGS = {
  'APP_NAME': '',
  'CONSUMER_KEY': '',
  'CONSUMER_SECRET': '',
  'SIG_METHOD': gdata.auth.OAuthSignatureMethod.HMAC_SHA1,
  'SCOPES': gdata.service.CLIENT_LOGIN_SCOPES['blogger'],
  'FINAL_URL': '/blogger',
}
