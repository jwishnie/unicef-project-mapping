from django import forms
from django.forms.util import ErrorList


class ProjectForm(forms.Form): 
    name = forms.CharField(max_length=30) 
    description = forms.CharField(max_length = 2500,widget=forms.Textarea())
    latitude = forms.DecimalField(max_digits=10, decimal_places=6)
    longitude = forms.DecimalField(max_digits=10, decimal_places=6)
    location = forms.CharField(max_length=50)
    website_url = forms.URLField()
    project_image = forms.URLField()
    project_sectors = forms.CharField(max_length = 500)
    project_implementors = forms.CharField(max_length = 500)
    imageset_feedurl = forms.CharField(max_length=1000, required=False)
    youtube_username = forms.CharField(max_length=100, required=False)
    tags = forms.CharField(max_length=500, required=False)
    
    
    
class UserForm(forms.Form):
    username = forms.CharField(max_length=30) 
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    groups = forms.CharField(max_length = 500)
    
    def clean(self):
        cleaned_data = self.cleaned_data
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password != confirm_password:
            message = u"Passwords do not match"
            self._errors["password"] = ErrorList([message])
            
        return cleaned_data