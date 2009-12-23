from django.core.management import setup_environ 
import settings 
setup_environ(settings)

from maplayers.models import Project
from maplayers.constants import PROJECT_STATUS

draft_projects = Project.objects.filter(status=PROJECT_STATUS.DRAFT)
draft_projects.delete()