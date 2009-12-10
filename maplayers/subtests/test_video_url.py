from django.test import TestCase
from maplayers.video_url import VideoUrl, Youtube, Vimeo, NoVideo


class VideoUrlCreation(TestCase):
    def test_gives_youtube_processor_if_video_is_youtube(self):
        processor = VideoUrl('http://www.youtube.com/watch?v=ZQogoEVXBSA')
        self.assertTrue(self._processor_is_of_type(processor, 'Youtube'))

    def test_gives_youtube_processor_if_video_is_vimeo(self):
        processor = VideoUrl('http://www.vimeo.com/7567626')
        self.assertTrue(self._processor_is_of_type(processor, 'Vimeo'))

    def test_gives_no_video_processor_if_url_is_neither_youtube_or_vimeo(self):
        processor = VideoUrl('http://www.viddler.com/7567626')
        self.assertTrue(self._processor_is_of_type(processor, 'NoVideo'))

    def test_gives_no_video_processor_when_url_is_invalid(self):
        url = 'http://www.vimeo.com/abcf'
        processor = VideoUrl(url)
        self.assertTrue(self._processor_is_of_type(processor, 'NoVideo'))

        url = 'http://www.youtube.com/watch?invalid'
        processor = VideoUrl(url)
        self.assertTrue(self._processor_is_of_type(processor, 'NoVideo'))

    def _processor_is_of_type(self, processor, type):
        return processor.__str__().__contains__(type)


class YoutubeUrl(TestCase):
    def test_gives_youtube_video_id(self):
        url = 'http://www.youtube.com/watch?v=ZQogoEVXBSA'
        video = Youtube(url)
        self.assertEquals(video.video_id(), 'ZQogoEVXBSA')

    def test_tells_url_is_valid(self):
        url = 'http://www.youtube.com/watch?v=ZQogoEVXBSA'
        video = Youtube(url)
        self.assertTrue(video.is_valid)

class VimeoUrl(TestCase):
    def test_gives_vimeo_video_id(self):
        url = 'http://www.vimeo.com/7567626'
        video = Vimeo(url)
        self.assertEquals(video.video_id(), '7567626')

    def test_tells_url_is_valid(self):
        url = 'http://www.vimeo.com/7567626'
        video = Vimeo(url)
        self.assertTrue(video.is_valid)

class InvalidUrlProcessor(TestCase):
    def test_tells_url_is_invalid(self):
        url = 'http://www.wetube.com/watch?v=ZQogoEVXBSA'
        video = NoVideo(url)
        self.assertFalse(video.is_valid)
