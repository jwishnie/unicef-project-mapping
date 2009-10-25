# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

"""
Template tags used to display project content

"""

from django import template
from django.core.cache import cache
import feedparser
from maplayers.utils import is_empty
from maplayers.feed_utils import parse_feed

register = template.Library()  

@register.inclusion_tag('feedgallery.html', takes_context=True)
def feed_gallery(context):
    """
    Parses an RSS feed, extracts images, and titles,
    places in a ordered sequence of dictionaries:
    { type: 'image/jpeg', # mime type
      url: 'http://etc...',
      caption: 'some caption'
    }
    
    this is then passed to the template to be rendered as a UL
    
    Context should include:
    feed_url: url to the feed
    feed_max_entries: maximum number of entries (defaults to all)
    
    Uses memcache and smart feed retrieval for optimization
    
    """
    print "gallery tag enter"
    # validate arguments
    if not context.has_key('feed_url') or \
        is_empty(context['feed_url']):
        return {}
    
    max_ = (int(context['feed_max_entries']) \
        if context.has_key('feed_max_entries') else 0)
    # fix url for use by feedparser
    return parse_feed(context['feed_url'], max_)
                                
