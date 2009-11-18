# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

'''
Constants for use anywhere in MapLayers

Created on Oct 29, 2009

@author: jeff wishnie
'''

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
