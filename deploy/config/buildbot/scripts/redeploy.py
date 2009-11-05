#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import os
import subprocess as sp
import pexpect

DB_NAME='unicefmapping'
DB_USER='unicefmapping'
DB_PWD='unicef'
DEPLOY_DIR='/var/www/mapping/app'
INIT_SCRIPT='/etc/init.d/maplayers'
CWD=os.getcwd()

def issue_cmd(cmd, failure_msg='Failed'):
	p = sp.Popen(cmd, stdout=sp.PIPE)
	print p.communicate()[0]
	if p.returncode != 0:
		print failure_msg
		os.chdir(CWD)
		sys.exit(p.returncode)
		

if __name__ == '__main__':
	import sys
	if len(sys.argv)>1:
		print "Usage: %s" % sys.argv[0]
		sys.exit(1)

	print "Stopping Maplayers server"
	issue_cmd([INIT_SCRIPT, 'stop'], 'Could not stop Maplayers server')

	print "Updating Git repo"
	os.chdir(DEPLOY_DIR)
	issue_cmd(['git', 'pull'], 'Could not pull git updates')

	print "Fixing ownership"
	os.chdir(DEPLOY_DIR)
	issue_cmd(['chown', '-R', 'www-data:www-data', DEPLOY_DIR], 'Could not set permissions')


	print "Dumping existing db"
	try:
		child = pexpect.spawn ('dropdb -U %s %s' % (DB_USER, DB_NAME))
		child.expect_exact ('Password:')
		child.sendline (DB_PWD)
	except:
		print "Failed to drop db"
		sys.exit(1)


	print "Creating blank db"
	try:
		child = pexpect.spawn ('createdb -U %s %s' % (DB_USER, DB_NAME))
		child.expect_exact ('Password:')
		child.sendline (DB_PWD)
	except:
		print "Failed to create db"
		sys.exit(1)


	print "Syncing db and loading initial data"
	issue_cmd(['python','manage.py','syncdb'], 'Could not sync db')

	print "Starting maplayers server"
	issue_cmd([INIT_SCRIPT, 'start'], 'Could not stop Maplayers server')


