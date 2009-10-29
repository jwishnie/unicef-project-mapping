from django import forms

class ProjectForm(forms.Form): 
    name = forms.CharField(max_length=30) 
    description = forms.CharField(max_length = 250,widget=forms.Textarea())
    latitude = forms.DecimalField(max_digits=10, decimal_places=6)
    longitude = forms.DecimalField(max_digits=10, decimal_places=6)
    location = forms.CharField(max_length=50)
    website_url = forms.URLField()
    project_image = forms.URLField()
    project_sectors = forms.CharField(max_length = 500)
    project_implementors = forms.CharField(max_length = 500)
    imageset_feedurl = forms.CharField(max_length=1000, required=False)
    youtube_username = forms.CharField(max_length=100, required=False)
