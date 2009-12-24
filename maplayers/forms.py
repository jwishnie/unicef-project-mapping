from django import forms
from django.forms.util import ErrorList
from tinymce.widgets import TinyMCE

from maplayers.countries import COUNTRIES
from maplayers.models import Project
from decimal import Decimal
from maplayers.models import Sector, Implementor
from django.contrib.auth.models import User
from maplayers.geoserver import GeoServer

def _get_sectors():
    return tuple([(sector.id, sector.name) for sector in Sector.objects.all()])
    
def _get_implementors():
    return tuple([(implementor.id, implementor.name) for implementor in Implementor.objects.all()])
    
class ProjectForm(forms.Form):
    name = forms.CharField(max_length=30) 
    description = forms.CharField(widget=TinyMCE(attrs={'cols' : 80, 'rows' : 20}))
    latitude = forms.DecimalField()
    longitude = forms.DecimalField()
    location = forms.CharField(max_length=50)
    website_url = forms.URLField()
    project_sectors = forms.MultipleChoiceField(required=True)
    project_implementors = forms.MultipleChoiceField(required=True)
    imageset_feedurl = forms.CharField(max_length=1000, required=False)
    tags = forms.CharField(max_length=500, required=False)
    
    def __init__(self, *args, **kwargs):
        self.base_fields['project_sectors'].choices = _get_sectors()
        self.base_fields['project_implementors'].choices = _get_implementors()
        super(ProjectForm, self).__init__(*args, **kwargs)
           
    
    def clean_latitude(self):
        cleaned_data = self.cleaned_data
        lat = cleaned_data.get("latitude")
        if lat<-90 or lat>90:
            self._errors['latitude'] = ErrorList([u'Latitude should be between -90 to 90'])
        lat = lat.quantize(Decimal('.0000001'))
        return lat
        
    def clean_longitude(self):
        cleaned_data = self.cleaned_data
        lon = cleaned_data.get("longitude")
        if lon<-180 or lon>180:
            self._errors['longitude'] = ErrorList([u'Longitude should be between -180 to 180'])
        lon = lon.quantize(Decimal('.0000001'))
        return lon
    
class AdminUnitForm(forms.Form):
    name = forms.CharField(max_length=50, required=True)
    region_type = forms.CharField(max_length=20, required=True)
    country = forms.ChoiceField(choices=COUNTRIES)
    health = forms.CharField(widget=TinyMCE(attrs={'cols':50, 'rows':10}), required=False)
    economy = forms.CharField(widget=TinyMCE(attrs={'cols':50, 'rows':10}), required=False)
    environment = forms.CharField(widget=TinyMCE(attrs={'cols':50, 'rows':10}), required=False)
    governance = forms.CharField(widget=TinyMCE(attrs={'cols':50, 'rows':10}), required=False)
    infrastructure = forms.CharField(widget=TinyMCE(attrs={'cols':50, 'rows':10}), required=False)
    social_sector = forms.CharField(widget=TinyMCE(attrs={'cols':50, 'rows':10}), required=False)
    agriculture = forms.CharField(widget=TinyMCE(attrs={'cols':50, 'rows':10}), required=False)
    dev_partners = forms.CharField(widget=TinyMCE(attrs={'cols':50, 'rows':10}), required=False)
    recent_reports = forms.CharField(widget=TinyMCE(attrs={'cols':50, 'rows':10}), required=False)
    resources = forms.CharField(widget=TinyMCE(attrs={'cols':50, 'rows':10}), required=False)
    
    
class UserForm(forms.Form):
    username = forms.CharField(max_length=30) 
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    
    def clean_username(self):
        cleaned_data = self.cleaned_data
        username = cleaned_data.get('username')
        user = User.objects.filter(username=username)
        if user:
            self._errors["username"] = ErrorList([u'Sorry, the user Name is not available'])
        return username


    def clean(self):
        cleaned_data = self.cleaned_data
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password != confirm_password:
            message = u"Passwords do not match"
            self._errors["password"] = ErrorList([message])
            
        return cleaned_data
        
class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput())
    new_password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    
    def clean(self):
        cleaned_data = self.cleaned_data
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if new_password != confirm_password:
            message = u"Passwords do not match"
            self._errors["new_password"] = ErrorList([message])
        return cleaned_data
        
    def validated_user(self, user):
        cleaned_data = self.cleaned_data
        old_password = cleaned_data.get("old_password")
        
        if not user.check_password(str(old_password)):
            self._errors["old_password"] = ErrorList(["Incorrect password"])
        return cleaned_data
        
class KMLFilesForm(forms.Form):
    name = forms.CharField(max_length = 50)
    filename = forms.FileField()

        
