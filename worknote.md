# swegram usage case

## How statistics work

### resource structure

resources
├── corpus
│   ├── annotated
│   │   ├── 10-en.conll
│   │   ├── 10-en-norm.conll
│   │   ├── 10-en-norm.tag
│   │   ├── 10-en.spell
│   │   ├── 10-en.tag
│   │   ├── 10-en.tok
│   │   ├── 10-sv.conll
│   │   ├── 10-sv-metadata.conll
│   │   ├── 10-sv-norm.conll
│   │   ├── 10-sv-norm.tag
│   │   ├── 10-sv.spell
│   │   ├── 10-sv.tag
│   │   ├── 10-sv.tok
│   │   └── __init__.py
│   ├── europarl-v7.sv-en.en
│   ├── europarl-v7.sv-en.sv
│   ├── __init__.py
│   └── raw
│       ├── 100-en.txt
│       ├── 100k-en.txt
│       ├── 100k-sv.txt
│       ├── 100-sv.txt
│       ├── 10-en.txt
│       ├── 10k-en.txt
│       ├── 10k-sv.txt
│       ├── 10-sv.txt
│       ├── 1k-en.txt
│       ├── 1k-sv.txt
│       └── __init__.py
├── __init__.py
├── README.md
└── scripts
    ├── corpus_download.sh
    ├── initial.py
    └── __init__.py





# Database:

mysql

docker: https://hub.docker.com/_/mysql
github: https://github.com/docker-library/mysql


docker pull mysql


## Server

docker run -d --name mysql-server -e MYSQL_ROOT_PASSWORD=<password> -p 3306:3306 -v </path/to/mysql_data>:/var/lib/mysql mysql:latest


docker run -d --privileged --name mysql-server -e MYSQL_ROOT_PASSWORD=pass -e MYSQL_DATABASE=swegram_corpus -e MYSQL_USER=swegram -e MYSQL_PASSWORD=swegram_pass -p 3306:3306 -v $(pwd)/data:/var/lib/mysql mysql:latest

docker run -d --privileged --name mysql-server -e MYSQL_ROOT_PASSWORD=pass -e MYSQL_DATABASE=swegram_corpus -e MYSQL_USER=swegram -e MYSQL_PASSWORD=swegram_pass -p 3306:3306 mysql:latest


## Enter interactive shell for mysql

### Spin up container of mysql as a client

* docker run -it --name mysql-client --link mysql-server:mysql --rm mysql:latest mysql -hmysql -uroot -p

### from Host

* mysql -h 127.0.0.1 -P 3306 -u root -p


## Nginx


docker run --name vue-nginx --rm -p 8080:80 --network host vue-nginx-proxy

## docker compose

docker compose --profile client up -d
docker compose --profile client down

## DATABASE COMMAND

SHOW DATABASES;
CREATE DATABASE <database_name>;
USE <database_name>; # access to <database_name>
SELECT DATABASE(); # verify which database it is now
SHOW COLUMNS FROM table_name;


## USERS COMMAND

SELECT user, host FROM mysql.user;


In MySQL, the % symbol in the "host" column typically represents a wildcard character, indicating that the associated user account is allowed to connect from any host. When you see % in the "host" column, it means that the user account is not restricted to connections from a specific IP address or hostname; instead, it can connect from any host.

Here are a few common values you might encounter in the "host" column:

* %: Allows connections from any host.
* localhost: Allows connections only from the local machine.
* 192.168.1.%: Allows connections from any host on the 192.168.1 subnet.

When creating or managing MySQL user accounts, the "host" field is used to specify from which hosts a user is allowed to connect. If the "host" field is set to %, it means the user can connect from anywhere. If it is set to localhost, the user can only connect from the same machine where the MySQL server is running.


```
mysql> SELECT user, host FROM mysql.user;
+------------------+-----------+
| user             | host      |
+------------------+-----------+
| root             | %         |
| swegram          | %         |
| mysql.infoschema | localhost |
| mysql.session    | localhost |
| mysql.sys        | localhost |
| root             | localhost |
+------------------+-----------+
6 rows in set (0,00 sec)

```

SELECT user, host FROM mysql.db WHERE db = '<database_name>';





Bugfix for when

1. pos tagging is not flagged
2. upload more than one file at the same time



