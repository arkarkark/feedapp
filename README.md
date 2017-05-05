# FeedApp
App Engine RSS Feed maker

1. Makes rss feeds from private blogger blogs (using your oauth credentials)
1. Makes rss feeds from incoming email
1. Makes rss feeds from public instagram accounts
1. **(WIP)** Handles incoming image emails and annotates them with location information

# setup

1. install the cloud sdk if you don't have it.
   1. [https://cloud.google.com/sdk/docs/](https://cloud.google.com/sdk/docs/)
   1. `gcloud components install app-engine-python`
1. install pillow for PIL support `sudo pip install pillow`
1. Get `client_secrets.json` (OAuth 2.0 client ID) from [Cloud  Console](https://console.cloud.google.com/apis/credentials). Put it in the same directory as this README.md
1. make `api_keys.json` it should contain this:

 `{"googlemaps": "KEY_FROM_CLOUD_CONSOLE"}`

 get the (API Key) value from [Cloud Console](https://console.cloud.google.com/apis/credentials). Put it in the same directory as this README.md
1. `./setup.sh`
1. `npm test`
1. `npm run dev` to see if it works
1. `npm run deploy` to push to production
