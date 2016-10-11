dev:
	dev_appserver.py --host=0.0.0.0 --port 6724 .

setup: atom gdata tlslite PyRSS2Gen

atom: gdata-python-client
	ln -s -f vendor/gdata-python-client/build/lib/atom

gdata: gdata-python-client
	ln -s -f vendor/gdata-python-client/build/lib/gdata

vendor:
	mkdir vendor

gdata-python-client: vendor
	cd vendor && \
	  if [ -d gdata-python-client ]; then \
	    cd gdata-python-client && git pull; \
	  else \
	    git clone git@github.com:google/gdata-python-client.git; \
	  fi
	cd vendor/gdata-python-client && python -W ignore::UserWarning:distutils.dist  ./setup.py build

tlslite: vendor
	cd vendor && \
	  if [ -d tlslite ]; then \
	    cd tlslite && git pull; \
	  else \
	    git clone git@github.com:trevp/tlslite.git; \
	  fi
	cd vendor/tlslite && python ./setup.py build
	ln -s -f vendor/tlslite/build/lib/tlslite

PyRSS2Gen: vendor
	cd vendor && \
	  if [ ! -d PyRSS2Gen-1.1 ]; then \
	    curl http://www.dalkescientific.com/Python/PyRSS2Gen-1.1.tar.gz | tar xvf - ; \
	  fi
	cd vendor/PyRSS2Gen-1.1 && python ./setup.py build
	ln -s -f vendor/PyRSS2Gen-1.1/build/lib/PyRSS2Gen.py

install:
	gcloud --quiet app --project feedappywtwf deploy --version=2

test:
	for fil in *_test.py; do $$fil; done

clean:
	rm -rf  gdata atom tlslite vendor
