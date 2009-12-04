# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

'''
Created on Oct 22, 2009

@author: jwishnie
'''
import unittest
from maplayers import tag_utils
import urllib2
from mock import Mock
FRMT = tag_utils.FLICKR_FEED_FORMAT


class FeedUtilsTest(unittest.TestCase):
    urlList = [
               ('http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us',
                'http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&'+FRMT),
                ('http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&format=atom',
                'http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&'+FRMT),
                ('http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&format=rss',
                'http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&'+FRMT),
                ('http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&format=rss_200_enc',
                'http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&'+FRMT),
                ('http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&format=rss_200',
                'http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&'+FRMT),
                ('http://api.flickr.com/services/feeds/photoset.gne?',
                'http://api.flickr.com/services/feeds/photoset.gne?'+FRMT),                
                ('feed://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&format=rss_200',
                 'http://api.flickr.com/services/feeds/photoset.gne?set=72157622616758268&nsid=36330826634@N01&lang=en-us&'+FRMT),
                ('http://www.nytimes.com/',
                'http://www.nytimes.com/'),
                ('Asdadaadfasdfn q3214 124 s,f asdf sdf a',
                 'Asdadaadfasdfn q3214 124 s,f asdf sdf a'),
              ]
    
    def testCleanURL(self):
        for src, expected in self.urlList:
            result = tag_utils.clean_feed_url(src)
            if result != expected:
                print "\nFAILURE\nsrc:\t  %s\nexpected: %s\nreceived: %s" % \
                    (src, expected, result)
                self.assertFalse(True)
    
    # def test_parse_img_feed_for_flickr_feeds(self):
    #     tag_utils.parse_feed = self._mock_parse_feed
    #     tag_utils.parse_img_feed("http://www.flickr.com")
    #     
    #     
    # def _mock_parse_feed(self, url):
    #     feed = Mock()
    #     content_array = Mock()
    #     content_array.content.return_value = [{
    #             'base': u'http://api.flickr.com/services/feeds/photoset.gne?set=72157609408183784&nsid=7496069@N08&format=atom',
    #             'type': 'text/html',
    #             'value': u'<p><a href="http://www.flickr.com/people/mylittlefinger/">MyLittleFinger</a> posted a photo:</p>\n<p><a href="http://www.flickr.com/photos/mylittlefinger/3464357201/" title="Mama bulbul, baby bulbul ..."><img alt="Mama bulbul, baby bulbul ..." height="204" src="http://farm4.static.flickr.com/3648/3464357201_b312a76ed9_m.jpg" width="240" /></a></p>\n\n<p>Shot @ my native place Gundmi, Karnataka ...<br />\n<br />\n<a href="http://www.flickr.com/photos/mylittlefinger/3464357201/sizes/o/"> View bigger size here </a></p>',
    #             'language': None
    #         }]
    #     feed.entries.return_value = ["hello", "world"]
    #     return feed
        
if __name__ == '__main__':
    unittest.main() 
    
