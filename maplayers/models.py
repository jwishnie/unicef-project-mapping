# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.db import models 

class Project(models.Model): 
    name = models.CharField(max_length=30) 
    description = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)
    location = models.CharField(max_length=50)
    website_url = models.URLField()
    project_image = models.URLField()
    imageset_feedurl = models.CharField(max_length=1000)
    youtube_username = models.CharField(max_length=100)
    parent_project = models.ForeignKey('self', null=True, blank=True)
    
    def url(self):
        return "/projects/id/%s" %(self.id)        
    
    def __unicode__(self): 
        return self.name
        
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
    filename = models.FileField(upload_to="/resources")
    project = models.ForeignKey(Project)

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
