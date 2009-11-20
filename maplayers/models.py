# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import text

import simplejson as json
from tagging.fields import TagField
from tagging.models import Tag
from tinymce import models as tinymce_models
from maplayers.countries import CountryField, COUNTRIES 

from maplayers.utils import is_empty
from maplayers.constants import GROUPS

class Project(models.Model): 
    name = models.CharField(max_length=30, null=True, blank=True) 
    description = tinymce_models.HTMLField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    location = models.CharField(max_length=50, null=True, blank=True)
    website_url = models.URLField(null=True, blank=True)
    project_image = models.URLField(null=True, blank=True)
    imageset_feedurl = models.CharField(max_length=1000, null=True, blank=True)
    youtube_playlist_id = models.CharField(max_length=20, null=True, blank=True)
    parent_project = models.ForeignKey('self', null=True, blank=True)
    status = models.CharField(max_length=50)
    created_by = models.ForeignKey(User)
    groups = models.ManyToManyField(Group)

    
    def _get_tags(self):
        '''
        Get tags seperated by spaces for the project
        '''
        tags = Tag.objects.get_for_object(self) 
        return " ".join([tag.name for tag in tags])
    
    def _set_tags(self, tag_list):
        '''
        Add tags to the tag list for the project
        '''
        Tag.objects.update_tags(self, tag_list)

    tags = property(_get_tags, _set_tags)  
      
    def contains_tag(self, tag):
        '''
        Return true if tag is in project's tag list
        '''
        if self.tags.split(" ").__contains__(tag):
            return True
        return False     
    
    def is_parent_project(self):
        '''
        Checks parent_project_id and returns true if not None
        '''
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
        return self.name + " : " + text.truncate_html_words(self.description, 25)
    
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
    country = models.CharField(max_length=50)
    region_statistics = tinymce_models.HTMLField(null=True, blank=True)

    class Admin:
        pass
   
        
class ReviewFeedback(models.Model):
    feedback = models.CharField(max_length=1000)
    project = models.ForeignKey(Project)
    reviewed_by = models.ForeignKey(User)
    
class ProjectComments(models.Model):
    text = models.CharField(max_length=1000)
    status = models.CharField(max_length=20)
    project = models.ForeignKey(Project)
    comment_by = models.CharField(max_length=100)
    email = models.EmailField()
    date = models.DateTimeField()
    
