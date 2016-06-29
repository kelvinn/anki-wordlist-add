import unittest

import responses
import re
from api import Word
from go import read_config


class TestCase(unittest.TestCase):

    def setUp(self):
        lang, output, forvo_api_key, pons_api_key, pons_lang, pn_dict, microsoft_api_key = read_config()

        self.w = Word("sailing", lang, pn_dict, pons_api_key, forvo_api_key, output, microsoft_api_key)

    @responses.activate
    def test_bing_get_images(self):
        with open('testdata/bing.json', 'r') as f:
            bing_json = f.read()

        responses.add(responses.GET, 'https://api.cognitive.microsoft.com/bing/v5.0/images/search',
                      body=bing_json, status=200,
                      content_type='application/json')

        images = self.w.get_images()
        assert 35 == len(images)

    @responses.activate
    def test_test_forvo_get_audio_links(self):
        with open('testdata/forvo.json', 'r') as f:
            forvo_json = f.read()

        url_re = re.compile(r'http://apifree.forvo.com/action/word-pronunciations/format/json/word/sailing/language/fr/key/\w+/')

        responses.add(responses.GET, url_re,
                      body=forvo_json, status=200,
                      content_type='application/json')

        audio_links = self.w.get_audio_links()
        assert 8 == len(list(audio_links.items()))

if __name__ == '__main__':

    unittest.main()
