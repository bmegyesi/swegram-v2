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

# Database (postgres)
In order to check the status of database connection, use the following command:

## Enter database as postgres user
```
psql
```

## Check the status of database connection
```
SELECT 
    pid
    ,datname
    ,usename
    ,application_name
    ,client_hostname
    ,client_port
    ,backend_start
    ,query_start
    ,query
    ,state
FROM pg_stat_activity;
```

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

* To add site (localhost in this case)

```
sudo a2ensite 127.0.0.1.conf
```

* To get rid of CORS from server's side, try
* Enable module of headers

```
sudo a2enmod headers
```

* Add & Configure in the apache2.conf

```
Header add Access-Control-Allow-Origin "*"
```

* source the configuration before reload|restart

```
# set environment variables in this file
source envvar
sudo systemctl reload apache2
```





