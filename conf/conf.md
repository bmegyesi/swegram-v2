# backend -> django
* pip install -r requirements.txt
* python manage.py makemigrations
* python manage.py migrate
* python manage.py createdatabase

# frontend -> vue2.js
* curl -s https://deb.nodesource.com/setup_16.x | sudo bash
* sudo apt install node
* cd $workspace/frontend
* npm install

# Database


# Network

url: 127.0.0.1:8000/v2/#/en

```
127.0.0.1:8000/v2/#/en
<hostname>:<port number>/<version number>/#/<vue router>
version number and port number is defined by django.
hashtag is an indicator to show where the vuejs starts
```

# NLP

## udpipe

The latest udpipe model for English, see [link](https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3131/english-ewt-ud-2.5-191206.udpipe?sequence=17&isAllowed=y)
[github repo](https://github.com/ufal/udpipe/tree/master/releases/pypi) 

## efselab


# Server

Apache2 is used as our proxy server.



