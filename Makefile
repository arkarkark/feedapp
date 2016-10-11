dev:
	dev_appserver.py --host=0.0.0.0 --port 6724 .

setup: gdata-python-client

gdata-python-client:
	git clone git@github.com:google/gdata-python-client.git
	cd gdata-python-client
	python ./setup.py build

atom: gdata-python-client
	ln -s gdata-python-client/build/lib/atom

gdata: gdata-python-client
	ln -s gdata-python-client/build/lib/gdata

install:
	gcloud --verbosity=info app --project feedappywtwf deploy --version=2

test:
	for fil in *_test.py; do $$fil; done
