#!/bin/bash

if [ ! -d dist/lib ]; then
    mkdir -p dist/lib
fi

pip install -t dist/lib google-api-python-client

if [ ! -d dist/lib/PyRSS2Gen-1.1 ]; then
  curl http://www.dalkescientific.com/Python/PyRSS2Gen-1.1.tar.gz | tar zxv -C dist/lib -f -
fi
(cd dist/lib/PyRSS2Gen-1.1 && python ./setup.py build)
(cd dist/lib/; mkdir PyRSS2Gen; cd PyRSS2Gen; ln -s -f ../PyRSS2Gen-1.1/build/lib/PyRSS2Gen.py __init__.py)

if [ ! -d  dist/lib/python-dateutil-1.5 ]; then
  curl http://labix.org/download/python-dateutil/python-dateutil-1.5.tar.gz | tar -zxv -C dist/lib -f -
fi
(cd dist/lib/; ln -s -f python-dateutil-1.5/dateutil dateutil)