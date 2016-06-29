#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a small program cycles through words in a CSV file and gets their IPA and pronunciation audio.

"""

__author__ = 'kelvinn'
__email__ = 'kelvin@kelvinism.com'


import os
import platform
from bs4 import BeautifulSoup
import requests
import logging
from py_bing_search import PyBingImageSearch


class Word():
    """Word object to store desired word and perform operations with it"""

    def __init__(self, word, lang, pn_dict, pons_api_key, forvo_api_key, output_folder, microsoft_api_key):
        self.word = word
        self.lang = lang
        self.pons_api_key = pons_api_key
        self.forvo_api_key = forvo_api_key
        self.output_folder = output_folder
        self.microsoft_api_key = microsoft_api_key
        self.pn_dict = pn_dict

        self.local_file_name = None
        self.download_links = []

    def get_images(self):
        """Get images of a given word from the Bing Search

        :return:
        """

        IMAGE_QUERY_BASE = 'https://api.cognitive.microsoft.com/bing/v5.0/images/search' \
                     + '?q={}&mkt=%27fr-FR%27'

        filters = requests.utils.quote("'{}'".format('Size:Medium+Aspect:Wide'))
        response_format = 'json'
        url = IMAGE_QUERY_BASE.format(requests.utils.quote("'{}'".format(self.word)))
        headers = {'Ocp-Apim-Subscription-Key':  self.microsoft_api_key}
        r = requests.get(str(url), headers=headers)

        try:
            json_results = r.json()

        except ValueError as vE:
            pass

        results = json_results['value']
        #bing_image = PyBingImageSearch(self.microsoft_api_key, self.word, image_filters='Size:Medium+Aspect:Wide')
        #first_fifty_result= bing_image.search(limit=50, format='json')
        return results

    def get_ipa(self):
        """Get IPA of a given word from the PONS API

        :return: dictionary of IPA and word class (e.g. noun or verb)
        """
        base_url = 'https://api.pons.com/v1/dictionary'
        data = None

        try:
            query = '?q=%s&in=%s&l=%s' % (self.word, self.lang, self.pn_dict )
            url = base_url + query

            headers = {'X-Secret': str(self.pons_api_key)}

            r = requests.get(url, headers=headers)
        except:
            return None

        try:
            data = r.json()
        except ValueError:
            logging.info("Unable to retrieve JSON from API")

        if data:
            word_dict = {}
            try:
                soup = BeautifulSoup(data[0]['hits'][0]['roms'][0]['headword_full'], "html.parser")
                word_dict['ipa'] = soup.find('span', attrs={'class': 'phonetics'}).getText()
                word_dict['wordclass'] = data[0]['hits'][0]['roms'][0]['wordclass']
                return word_dict
            except (KeyError, AttributeError, TypeError) as e:
                logging.info('Unable to get IPA for word %s' % self.word)

        return None

    def get_audio_links(self, ACT='word-pronunciations', FORMAT='mp3', free= True):
        """Get list of audio pronunciation links from Forvo

        :param ACT:
        :param FORMAT:
        :param free:
        :return: items
        """

        base_url = 'http://apifree.forvo.com/'

        key = [
            ('action', ACT),
            ('format', 'json'),
            ('word', requests.utils.quote(self.word)),
            ('language', self.lang),
            ('key', self.forvo_api_key)
            ]

        url = base_url + '/'.join(['%s/%s' % a for a in key if a[1]]) + '/'

        try:
            r = requests.get(url)
        except:
            return None

        data = r.json()

        if 'items' in data:
            items = {}
            for i in data[u'items']:
                audioFormat = u'path'+FORMAT
                identifier = str(i['id'])
                items[identifier] = i[audioFormat]
            return items

        else:
            return None

    def download(self, url):
        """Download pronunciation audio (MP3) from Forvo

        :param url:
        :return: file path and name to downloaded file
        """


        mp3 = requests.get(url)
        file_name = 'forvo_pronunciation_' + requests.utils.quote(self.word) + '.mp3'
        file_path = os.path.join(self.output_folder, file_name)

        if not os.path.exists(self.output_folder):
              os.makedirs(self.output_folder)
        else:
            with open(file_path,"wb") as out:
                #we open a new mp3 file and we name it after the word we're downloading.
                #The file it's opened in write-binary mode
                out.write(mp3.content)

        return file_path, file_name

    def play(self, file_name):
        """Plays downloaded audio file

        :param file_name:
        :return:
        """

        if platform.system() == 'Linux':
            os.system('mpg123 -q %s' % file_name)
        else:
            os.system('afplay %s &' % file_name)
