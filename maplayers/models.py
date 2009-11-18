# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.db import models
from django.contrib.auth.models import User, Group
from maplayers.constants import GROUPS

import simplejson as json
from tagging.fields import TagField
from tagging.models import Tag
from tinymce import models as tinymce_models

from maplayers.utils import is_empty

class Project(models.Model): 
    name = models.CharField(max_length=30, null=True, blank=True) 
    description = tinymce_models.HTMLField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    location = models.CharField(max_length=50, null=True, blank=True)
    website_url = models.URLField(null=True, blank=True)
    project_image = models.URLField(null=True, blank=True)
    imageset_feedurl = models.CharField(max_length=1000,null=True, blank=True)
    youtube_playlist_id = models.CharField(max_length=20, null=True, blank=True)
    parent_project = models.ForeignKey('self', null=True, blank=True)
    status = models.CharField(max_length=12)
    created_by = models.ForeignKey(User)
    groups = models.ManyToManyField(Group)

    
    def _get_tags(self):
        tags = Tag.objects.get_for_object(self) 
        return " ".join([tag.name for tag in tags])
    
    def _set_tags(self, tag_list):
        Tag.objects.update_tags(self, tag_list)

    tags = property(_get_tags, _set_tags)  
      
    def contains_tag(self, tag):
        if self.tags.split(" ").__contains__(tag):
            return True
        return False     
    
    def is_parent_project(self):
        if self.parent_project:
            return False
        return True
    
    def is_editable_by(self, user):
        if self.created_by == user: return True
        return self._check_user_groups(user)
        
    def is_publishable_by(self, user):
        return self._check_user_groups(user)
        
    def _check_user_groups(self, user):
        user_groups = set([group.name for group in user.groups.all()])
        if (user_groups & set((GROUPS.ADMINS, GROUPS.EDITORS_PUBLISHERS))) : return True
        return False
            
        
    def implementors_in_json(self):
        return json.dumps([implementor.name for implementor in Implementor.objects.filter(projects=self.id)])
    
    def sectors_in_json(self):
        return json.dumps([sector.name for sector in Sector.objects.filter(projects=self.id)])
    
    def __unicode__(self): 
        return ( 'No Name' if is_empty(self.name) else self.name)
        
    def snippet(self):
        return self.name + " : " + self.description[:50]
    
    class Admin: 
        pass
 
class Link(models.Model):
    title = models.CharField(max_length=50)
    url = models.URLField()
    project = models.ForeignKey(Project)

    def __unicode__(self): 
        return self.title

    class Admin: 
        pass
    
class Resource(models.Model):
    title = models.CharField(max_length=50)
    filename = models.CharField(max_length=250)
    project = models.ForeignKey(Project)
    filesize = models.IntegerField()
    
    def __unicode__(self): 
        return self.title

    class Admin: 
        pass
        
        
class Sector(models.Model):
    name = models.CharField(max_length=50)
    projects = models.ManyToManyField(Project, blank=True)
    
    def __unicode__(self): 
        return self.name

    class Admin: 
        pass
        
class Implementor(models.Model):
    name = models.CharField(max_length=50)
    projects = models.ManyToManyField(Project, blank=True)
    
    def __unicode__(self):
        return self.name
        
    class Admin:
        pass

class AdministrativeUnit(models.Model):
    name = models.CharField(max_length = 20)
    region_type = models.CharField(max_length=10)
    country = models.CharField(max_length=20)
    region_metrics = tinymce_models.HTMLField(null=True, blank=True)
    
        
class ReviewFeedback(models.Model):
    feedback = models.CharField(max_length=500)
    project = models.ForeignKey(Project)
    sent_by = models.ForeignKey(User)
    
