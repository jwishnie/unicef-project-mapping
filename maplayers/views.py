# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.shortcuts import render_to_response
from maplayers.models import Project

def homepage(request):
    projects = Project.objects.all()
    return render_to_response('homepage.html', {'projects' : projects}) 
    


def project_details(request):
    project = Project.objects.all()[0]
    return render_to_response('project_details.html', {'project': project, 'links' :project.link_set.all() }) 