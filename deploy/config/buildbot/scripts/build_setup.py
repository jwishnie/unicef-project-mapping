#!/usr/bin/env python

# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

SETTINGS = 'settings.py.production'
DATA = 'test_project_data.json'
if __name__ == '__main__':
	import sys
	if len(sys.argv)>1:
		print "Usage: %s" % sys.argv[0]
		sys.exit(1)

	import os
	print "Using %s for settings.py" % SETTINGS
	os.symlink(SETTINGS,'settings.py')
	wd = os.getcwd()
	os.chdir(os.path.join('maplayers','fixtures'))
	print "Using %s for initial_data.json" % DATA
	os.symlink(DATA,'initial_data.json')
	os.chdir(wd)
	print "Done"
	sys.exit(0)
