from django import forms
from django.forms.util import ErrorList
from tinymce.widgets import TinyMCE


class ProjectForm(forms.Form): 
    name = forms.CharField(max_length=30) 
    description = forms.CharField(widget=TinyMCE(attrs={'cols':100, 'rows':30}))
    latitude = forms.DecimalField(max_digits=10, decimal_places=6)
    longitude = forms.DecimalField(max_digits=10, decimal_places=6)
    location = forms.CharField(max_length=50)
    website_url = forms.URLField()
    project_image = forms.URLField()
    project_sectors = forms.CharField(max_length = 500)
    project_implementors = forms.CharField(max_length = 500)
    imageset_feedurl = forms.CharField(max_length=1000, required=False)
    youtube_playlist_id = forms.CharField(max_length=20, required=False)
    tags = forms.CharField(max_length=500, required=False)
    
class AdminUnitForm(forms.Form):
    name = forms.CharField(max_length=50)
    type = forms.CharField(max_length=20)
    country = forms.CharField(max_length=20)
    metrics_data = forms.CharField(widget=TinyMCE(attrs={'cols':80, 'rows':30}))
    
class UserForm(forms.Form):
    username = forms.CharField(max_length=30) 
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    
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
