# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

"""
Admin site definition for basic models

"""

from maplayers.models import Link, Project, Resource, Sector
from django.contrib import admin 

admin.site.register(Project)
admin.site.register(Link)
admin.site.register(Resource)
admin.site.register(Sector)
