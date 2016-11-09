# FeedApp
App Engine RSS Feed maker

1. Makes rss feeds from private blogger blogs (using your oauth credentials)
1. Makes rss feeds from incoming email

# setup

1. install the cloud sdk if you don't have it.
   1. [https://cloud.google.com/sdk/docs/](https://cloud.google.com/sdk/docs/)
   1. gcloud components install app-engine-python
1. `./setup.sh`
1. `npm test`
1. `npm run dev` to see if it works
1. `npm run install` to push to production
