from django.shortcuts import render_to_response
from maplayers.models import Project

def project_details(request):
	project = Project.objects.all()[0]
	return render_to_response('project_details.html', {'project': project}) 