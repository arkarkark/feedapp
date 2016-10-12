#!/bin/bash

if [ ! -d app/lib ]; then
    mkdir -p app/lib
fi

pip install -t app/lib google-api-python-client

if [ ! -d app/lib/PyRSS2Gen-1.1 ]; then
  curl http://www.dalkescientific.com/Python/PyRSS2Gen-1.1.tar.gz | tar zxv -C app/lib -f -
fi
(cd app/lib/PyRSS2Gen-1.1 && python ./setup.py build)
(cd app/lib/; mkdir PyRSS2Gen; cd PyRSS2Gen; ln -s -f ../PyRSS2Gen-1.1/build/lib/PyRSS2Gen.py __init__.py)

if [ ! -d  app/lib/python-dateutil-1.5 ]; then
  curl http://labix.org/download/python-dateutil/python-dateutil-1.5.tar.gz | tar -zxv -C app/lib -f -
fi
(cd app/lib/; ln -s -f python-dateutil-1.5/dateutil dateutil)
