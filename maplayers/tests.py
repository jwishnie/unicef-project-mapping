# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

# import all files in maplayers/subtests/*tests.py as modules

"""
from glob import glob

for t in glob('maplayers/subtests/*tests.py'):
    # convert from file name to module name
    mod = t.replace('/','.')[:-3]
    print mod
    __import__(mod)
"""   


from maplayers.subtests.utils_tests import * 
from maplayers.subtests.tag_utils_tests import *
from maplayers.subtests.homepage_view_tests import *
from maplayers.subtests.project_view_tests import * 
from maplayers.subtests.admin_views_tests import *
from maplayers.subtests.project_model_tests import *