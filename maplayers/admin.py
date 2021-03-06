# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

"""
Admin site definition for basic models

"""

from maplayers import models
from django.contrib import admin 

admin.site.register(models.Project)
admin.site.register(models.Link)
admin.site.register(models.Resource)
admin.site.register(models.Sector)
admin.site.register(models.Implementor)
admin.site.register(models.AdministrativeUnit)
admin.site.register(models.ReviewFeedback)
admin.site.register(models.ProjectComment)
admin.site.register(models.Video)
admin.site.register(models.KMLFile)