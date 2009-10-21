# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.shortcuts import render_to_response
from django.http import Http404
from maplayers.models import Project

def homepage(request):
    projects = Project.objects.all()
    return render_to_response('homepage.html', {'projects' : projects}) 
    
def projects(request):
    projects = Project.objects.all()
    return render_to_response("projects.html", {'projects' : projects})

def project(request, project_id):
    try:
        project = Project.objects.all()[int(project_id)]
    except IndexError:
      raise Http404
    return render_to_response('project.html', {'project': project, 'links' :project.link_set.all() }) 
