
from twisted.application import service
from buildbot.slave.bot import BuildSlave

basedir = r'/var/lib/buildbot/mepe-slave'
buildmaster_host = 'localhost'
port = 9989
slavename = 'mepe-slave'
passwd = 'mepemepe'
keepalive = 600
usepty = 1
umask = None

application = service.Application('buildslave')
s = BuildSlave(buildmaster_host, port, slavename, passwd, basedir,
               keepalive, usepty, umask=umask)
s.setServiceParent(application)

