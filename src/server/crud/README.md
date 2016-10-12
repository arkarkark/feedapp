# crud library

from:
https://github.com/GoogleCloudPlatform/Data-Pipeline/tree/master/app/lib

you'll need parsedatetime

```bash
mkdir vendor
# dateutil
curl -o - http://labix.org/download/python-dateutil/python-dateutil-1.5.tar.gz |
    tar -zxv -C vendor -f -
ln -s ../vendor/python-dateutil-1.5/dateutil dateutil
```
