#!/bin/bash

if [ ! -d dist/lib ]; then
    mkdir -p dist/lib
fi

if [ ! -e dist/lib/googleapiclient ]; then
    pip install -t dist/lib google-api-python-client
fi

if [ ! -e dist/lib/pytz ]; then
    pip install -t dist/lib pytz
fi

if [ ! -e dist/lib/PyRSS2Gen.py ]; then
  if [ ! -d dist/lib/PyRSS2Gen-1.1 ]; then
    curl http://www.dalkescientific.com/Python/PyRSS2Gen-1.1.tar.gz | tar zxv -C dist/lib -f -
  fi
  (cd dist/lib/PyRSS2Gen-1.1 && python ./setup.py build)
  (cd dist/lib/; ln -s -f PyRSS2Gen-1.1/build/lib/PyRSS2Gen.py)
fi

if [ ! -d  dist/lib/python-dateutil-1.5 ]; then
  curl http://labix.org/download/python-dateutil/python-dateutil-1.5.tar.gz | tar -zxv -C dist/lib -f -
fi
(cd dist/lib/; ln -s -f python-dateutil-1.5/dateutil dateutil)

if which yarn; then
  yarn
else
  echo "You really should install yarn see https://yarnpkg.com/en/docs/install"
  npm install
fi

./node_modules/.bin/gulp
