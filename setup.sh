#!/bin/bash

if [ ! -d vendor ]; then
    mkdir vendor
fi

(
  cd vendor
  if [ -d gdata-python-client ]; then
    (cd gdata-python-client && git pull)
  else
    git clone git@github.com:google/gdata-python-client.git
  fi
  cd gdata-python-client && python -W ignore::UserWarning:distutils.dist ./setup.py build
)
ln -s -f vendor/gdata-python-client/build/lib/atom
ln -s -f vendor/gdata-python-client/build/lib/gdata

(
  cd vendor
  if [ -d tlslite ]; then
    (cd tlslite && git pull)
  else
    git clone git@github.com:trevp/tlslite.git
  fi
  cd tlslite && python ./setup.py build
)
ln -s -f vendor/tlslite/build/lib/tlslite

if [ ! -d vendor/PyRSS2Gen-1.1 ]; then
  curl http://www.dalkescientific.com/Python/PyRSS2Gen-1.1.tar.gz | tar zxv -C vendor -f -
fi
(cd vendor/PyRSS2Gen-1.1 && python ./setup.py build)
ln -s -f vendor/PyRSS2Gen-1.1/build/lib/PyRSS2Gen.py

if [ ! -d  vendor/python-dateutil-1.5 ]; then
  curl http://labix.org/download/python-dateutil/python-dateutil-1.5.tar.gz | tar -zxv -C vendor -f -
fi
ln -s -f vendor/python-dateutil-1.5/dateutil dateutil
