Dependencies
------------

The following are external dependencies and their Ubuntu package names:

========================   ========================
Dependency                 Ubuntu Package
========================   ========================
Django                     python-django
TZ definitions             python-tz
Universal feed parser      (included in project dir as need at least rev295 from sv)
Python Tidy                python-utidylib
Tidy                       libtidy-0.99-0 
Chardet                    python-chardet
========================   ========================

The following are need for deploy with PostGIS, Memcached, Nginx, and Fastcgi

========================   ========================
Dependency                 Ubuntu Package
========================   ========================
Flup                       python-flup
Postgres                   postgresql
PostGIS                    postgis
Postgres Python driver     python-psycopg2
Nginx                      nginx
Memcached                  memcached
Python memcache            python-memcache
Buildbot (for build servers)                   buildbot
========================   ========================



