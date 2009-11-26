# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import re as regex

class GROUPS(object):
    ADMINS = u'admins'
    PROJECT_AUTHORS = 'project_authors'
    EDITORS_PUBLISHERS = 'editors_publishers'
    
class PROJECT_STATUS(object):
    PUBLISHED= u'Published'
    DRAFT = u'Draft'
    UNPUBLISHED = u'Unpublished'
    REVIEW = u'Review'
    REJECTED= u'Rejected'
    REQUEST_CHANGES= u'Change requested'
    
class COMMENT_STATUS(object):
    PUBLISHED = u'Published'
    UNMODERATED = u'UnModerated'
    
class VIDEO_PROVIDER(object):
    YOUTUBE = u'youtube'
    VIMEO = u'vimeo'

EMAIL_REGEX = regex.compile("^[a-zA-Z][\w\.-]*[a-zA-Z0-9]@[a-zA-Z0-9][\w\.-]*[a-zA-Z0-9]\.[a-zA-Z][a-zA-Z\.]*[a-zA-Z]$")
YOUTUBE_REGEX = '^[^v]+v.(.{11}).*'
VIMEO_REGEX = '.*/(\d+)'
