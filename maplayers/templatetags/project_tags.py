# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

"""
Template tags used to display project content

"""

from django import template
import feedparser

register = template.Library()

@register.inclusion_tag('feedgallery.html')
def feed_gallery(ctxt):
    """
    Parses an RSS feed, extracts images, and titles,
    places in a ordered sequence of dictionaries:
    { type: 'image/jpeg', # mime type
      url: 'http://etc...',
      caption: 'some caption'
    }
    
    this is then passed to the template to be rendered as a UL
    
    'ctxt' should be a dictionary with arguments:
    feed_url: url to the feed
    max_entries: maximum number of entries (defaults to all)
    
    Uses memcache and smart feed retrieval for optimization
    
    """
    ctxt={}
    # validate arguments
    if ctxt == None or 
        not ctxt.has_key('feed_url') or
        :
        return {}
    
    pass  