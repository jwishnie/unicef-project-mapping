# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.db import models 

class Project(models.Model): 
    name = models.CharField(max_length=30) 
    description = models.TextField()

    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)
    location = models.CharField(max_length=50)
    
    def sector_names(self):
        return " ".join([sector.name for sector in self.sector_set.all()])

    def __unicode__(self): 
        return self.name

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
