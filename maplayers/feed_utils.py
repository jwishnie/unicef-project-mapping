# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

"""
Utilities for dealing with RSS Feeds

"""
import urlparse
import re

IMAGE_TYPES = (
               'image/jpeg',
               'image/pjpeg',
               'image/gif',
               'image/png'
               )

def clean_feed_url(url):
    """
    Clean up urls for use with universal parser which:
    - doesn't understand 'feed'
    - doesn't seem to read flickr rss2.0 format without enclosures
    
    This basically encapsulates hacks need to get the feeds from
    different services to work properly with the feed parser library
    
    """
    
    # swap out 'feed:' for 'http:' as the python libraries seem to choke on it
    url = re.sub(r'^feed:', 'http:',url)
    
    # parse URL, note this call does _not_ throw any exceptions
    # and always returns something, even if garbage
    split_url = urlparse.urlsplit(url)
    scheme, loc, path, query, frag = split_url
    
    # if this is flickr, make sure the format is rss_200_enc
    if loc.endswith('flickr.com'):
        m = re.search(r'format=([^&]+)', query)
        if m is not None:
            query = query.replace(m.group(1),'rss_200_enc')
        else:
            frmt = ('&format=rss_200_enc' if len(query)>0 else 'format=rss_200_enc')
            query = query + frmt
     
    return urlparse.urlunsplit((scheme,loc,path,query,frag))
    
        