from django.db import models 

class Location(models.Model):
	country = models.CharField(max_length=50) 
	admin_unit1 = models.CharField(max_length=50)
	admin_unit2 = models.CharField(max_length=50, blank=True, null=True)
	admin_unit3 = models.CharField(max_length=50, blank=True, null=True)
	admin_unit4 = models.CharField(max_length=50, blank=True, null=True)
	admin_unit5 = models.CharField(max_length=50, blank=True, null=True)

	def __str__(self):
		return "%s, %s, %s, %s, %s" % (self.country, self.admin_unit1, self.admin_unit2, self.admin_unit3, self.admin_unit4, self.admin_unit5)
		

class Project(models.Model): 
	name = models.CharField(max_length=30) 
	description = models.TextField()
	lat = models.DecimalField(max_digits=10, decimal_places=6)
	lon = models.DecimalField(max_digits=10, decimal_places=6)
	location = models.ForeignKey(Location)

	def __str__(self): 
		return self.name

	def geography(self):
		s = [self.location.admin_unit5, self.location.admin_unit4, self.location.admin_unit3, 
			self.location.admin_unit2, self.location.admin_unit1, self.location.country]
		location = [l for l in s if l!=None]
		return " ".join(location)


		

class Resource(models.Model):
	title = models.CharField(max_length=50)
	filename = models.FileField(upload_to="/resources")
	project = models.ForeignKey(Project)
	
	def __str__(self): 
		return self.title


class Link(models.Model):
	title = models.CharField(max_length=50)
	url = models.URLField()
	project = models.ForeignKey(Project)
	
	def __str__(self): 
		return self.title