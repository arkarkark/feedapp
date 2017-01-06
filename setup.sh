#!/bin/bash

[ ! -d dist/lib 		] && mkdir -p dist/lib
[ ! -e dist/lib/googleapiclient ] && pip install -t dist/lib google-api-python-client
[ ! -e dist/lib/pytz 		] && pip install -t dist/lib pytz

if [ ! -e dist/lib/googlemaps ]; then
  ZIPFILE=/tmp/google-maps-services-python.zip
  curl https://codeload.github.com/gae123/google-maps-services-python/zip/master -o $ZIPFILE
  unzip -d dist/lib $ZIPFILE
  ln -s dist/lib/google-maps-services-python-master/googlemaps/roads.py
fi


if [ ! -e dist/lib/PyRSS2Gen.py ]; then
  if [ ! -d dist/lib/PyRSS2Gen-1.1 ]; then
    curl http://www.dalkescientific.com/Python/PyRSS2Gen-1.1.tar.gz | tar zxv -C dist/lib -f -
  fi
  (cd dist/lib/PyRSS2Gen-1.1 && python ./setup.py build)
  (cd dist/lib/; ln -s -f PyRSS2Gen-1.1/build/lib/PyRSS2Gen.py)
fi

if [ ! -d  dist/lib/dateutil ]; then
  if [ ! -d  dist/lib/python-dateutil-1.5 ]; then
    curl http://labix.org/download/python-dateutil/python-dateutil-1.5.tar.gz | tar -zxv -C dist/lib -f -
  fi
  (cd dist/lib/; ln -s -f python-dateutil-1.5/dateutil dateutil)
fi

if which yarn; then
  yarn
else
  echo "You really should install yarn see https://yarnpkg.com/en/docs/install"
  npm install
fi

./node_modules/.bin/gulp
