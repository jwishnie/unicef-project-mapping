# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

"""
Template tags used to display project content

"""

from django import template
from django.core.cache import cache
import feedparser
from maplayers.utils import is_empty
from maplayers.feed_utils import clean_feed_url, IMAGE_TYPES

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

    # validate arguments
    if not context.has_key('feed_url') or \
        is_empty(context['feed_url']):
        return {}
    
    # fix url for use by feedparser
    clean_url = clean_feed_url(context['feed_url'])
                                
    # Try to retrieve from cache using cleaned url
    parsed_feed = cache.get(clean_url)
    
    # if we got one, make a etags or modified request to see if any updates
    if parsed_feed is not None:
        print "Cache Hit"
        updated_feed = None
        if parsed_feed.has_key('etag'):
            updated_feed = feedparser.parse(clean_url, etag=parsed_feed.etag)
        elif parsed_feed.has_key('modified'):
            updated_feed = \
                feedparser.parse(clean_url, modified=parsed_feed.modified)
                
        # did we get any changes?  
        if updated_feed is not None and updated_feed.status == 200:
            print 'cache feed updated'
            parsed_feed = updated_feed
            cache.set(clean_url, parsed_feed)
        print 'cache still valid'
    else:
        print 'cache miss'
        # no cached one, go get it
        parsed_feed = feedparser.parse(clean_url)
        cache.set(clean_url, parsed_feed)
        
    # extract media info
    max_ = (int(context['feed_max_entries']) \
            if context.has_key('feed_max_entries') else -1)
    media = []
    for e in parsed_feed.entries:
        if max_ == 0:
            break
        
        # check for all required info
        if e.has_key('enclosures') and \
            len(e.enclosures)>0:
            img = e.enclosures[0]
            
            if img.has_key('type') and \
                img.type in IMAGE_TYPES and \
                img.has_key('href'):
            
                # add info
                media.append({'img_url': img.href,
                              'title': 
                                  (e.title if e.has_key('title') else ''),
                              'entry_url': 
                                  (e.link if e.has_key('link') else '')})
                max_ = max_ -1
                
    # extract feed info
    f = parsed_feed.feed
    feed_meta = {'title':
                        (f.title if f.has_key('title') else ''),
                  'url':
                        (f.link if f.has_key('link') else '')}

    return { 'feed': feed_meta, 'media': media }
    
                         
        
            
    