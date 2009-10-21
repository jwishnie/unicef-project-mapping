# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.shortcuts import render_to_response
from maplayers.models import Project, Sector
import decimal

def homepage(request):
    projects = Project.objects.all()
    return render_to_response('homepage.html', {'projects' : projects}) 
    
def projects(request):
    projects = Project.objects.all()
    return render_to_response("projects.html", {'projects' : projects})

def project_details(request):
    project = Project.objects.all()[0]
    return render_to_response('project_details.html', {'project': project, 'links' :project.link_set.all() }) 
    
def projects_in_map(request, left, bottom, right, top):
    left, bottom, right, top = decimal.Decimal(left), decimal.Decimal(bottom), decimal.Decimal(right), decimal.Decimal(top)
    sectors = Sector.objects.all()
    projects = Project.objects.filter(lon__gte=left, lon__lte=right,  lat__gte=bottom, lat__lte=top)
    return render_to_response('projects_in_map.html', {'projects': projects, 'sectors' : sectors})