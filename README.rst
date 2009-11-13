Dependencies
------------

The following are external dependencies and their Ubuntu package names:

========================   ========================
Dependency                 Ubuntu Package
========================   ========================
Django                     python-django
TZ definitions             python-tz
Universal feed parser      (included in project dir as need at least rev295 from svn)
SimpleJson                 python-simplejson
django tagging plugin      python-django-tagging
tinymce                    python-django-tinymce
PyEnchant                  python-enchant
========================   ========================

The following are needed for staging deploy with PostGIS, Memcached, Nginx, Fastcgi, and BuildBot

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
Python Expect              python-pexpect
Buildbot (build servers)   buildbot
========================   ========================



