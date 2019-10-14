#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib.request import urlopen, Request
from urllib.parse import quote
import json
import gzip
import lxml.html
from lxml.html import document_fromstring
from lxml.etree import tostring
import re
import sys
from catenae import CircularOrderedSet
import time
from random import randint
from .polypus import HttpHelper


class TwitterHttpHelper(HttpHelper):
    @staticmethod
    def get_user_agent():
        system_info_lines = [
            'Windows NT 10.0; Win64; x64',  # Windows 10
            'Windows NT 6.3; Win64; x64',  # Windows 8.1
            'Windows NT 6.2; Win64; x64',  # Windows 8
            'Windows NT 6.1; Win64; x64',  # Windows 7
            'X11; Linux x86_64',
        ]

        chrome_version_lines = [
            '77.0.3865.90',
            '75.0.3770.100',
            '60.0.3112.113'
            '60.0.3112.90',
            '57.0.2987.133'
            '55.0.2883.87',
            '44.0.2403.157',
        ]

        system_info = system_info_lines[randint(0, len(system_info_lines) - 1)]
        chrome_version = chrome_version_lines[randint(0, len(chrome_version_lines) - 1)]

        user_agent = f'Mozilla/5.0 ({system_info}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36'
        return user_agent

    @staticmethod
    def get_json_header():
        return {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.5',
            'user-agent': TwitterHttpHelper.get_user_agent(),
            'x-requested-with': 'XMLHttpRequest',
            'x-twitter-active-user': 'yes'
        }

    @staticmethod
    def get_html_header():
        return {
            'accept': 'text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.5',
            'user-agent': '',
            'x-twitter-active-user': 'yes'
        }

    @staticmethod
    def get_json_response(url):
        request = Request(url=url, headers=TwitterHttpHelper.get_json_header())
        response = TwitterHttpHelper.get_response_from_request(request)
        return json.loads(response)

    @staticmethod
    def get_html_response(url):
        request = Request(url=url, headers=TwitterHttpHelper.get_html_header())
        response = TwitterHttpHelper.get_response_from_request(request)
        return response

    @staticmethod
    def get_response_from_request(request):
        response = urlopen(request)
        assert (response.info().get('Content-Encoding') == 'gzip')
        return gzip.GzipFile(fileobj=response).read()


class TwitterScraper:
    emoji_flag = '24f2c44c'
    emoji_regex = re.compile(r'alt="(.{0,8})"')
    img_regex = re.compile(r'<img([\w\W]+?)/>')

    @staticmethod
    def get_emojis(text):
        return re.findall(TwitterScraper.emoji_regex, text)

    @staticmethod
    def get_tagged_html(text):
        return re.sub(TwitterScraper.img_regex, f'  {TwitterScraper.emoji_flag}  ', text)

    @staticmethod
    def insert_emojis(emojis, text):
        for emoji in emojis:
            text = text.replace(f' {TwitterScraper.emoji_flag} ', emoji, 1)
        text = text.replace(f' {TwitterScraper.emoji_flag} ', '')
        return text

    @staticmethod
    def post_process_text(text):
        text = text.replace('…', '')
        text = re.sub(r'\s+', ' ', text)
        return text

    @staticmethod
    def get_processed_text(html_content):
        emojis = TwitterScraper.get_emojis(html_content)
        tagged_html = TwitterScraper.get_tagged_html(html_content)
        tagged_text = document_fromstring(tagged_html).text_content()
        tagged_text_emojis = TwitterScraper.insert_emojis(emojis, tagged_text)
        text = TwitterScraper.post_process_text(tagged_text_emojis)
        return text.strip()

    @staticmethod
    def _encode_query(query: dict) -> str:
        encoded_query = ''

        since = None
        if 'since' in query:
            since = query['since']

        until = None
        if 'until' in query:
            until = query['until']

        near = None
        if 'near' in query:
            near = query['near']

        lang = None
        if 'lang' in query:
            lang = query['lang']

        fields = []
        if 'fields' in query:
            fields = query['fields']

        for field in fields:
            target = None
            if 'target' in field:
                target = field['target']

            items = field['items']

            match = None
            if 'match' in field:
                match = field['match']

            exact = False
            if 'exact' in field:
                exact = field['exact']

            if exact:
                marginal_query = '"' + '" "'.join(items) + '"'
            else:
                target = None
                if 'target' in field:
                    target = field['target']

                if target == 'from':
                    marginal_query = 'from:' + ' from:'.join(items)
                elif target == 'to':
                    marginal_query = 'to:' + ' to:'.join(items)
                elif target == 'hashtag':
                    marginal_query = '#' + ' #'.join(items)
                elif target == 'mention':
                    marginal_query = '@' + ' @'.join(items)
                else:
                    marginal_query = ' '.join(items)

            if match == 'any':
                marginal_query = ' OR '.join(marginal_query.split())
            elif match == 'none':
                marginal_query = '-' + ' -'.join(marginal_query.split())

            encoded_query += ' ' + marginal_query

        if since is not None:
            encoded_query += f' since:{since}'

        if until is not None:
            encoded_query += f' until:{until}'

        if near is not None:
            encoded_query += f' near:"{near[0]}" within:{near[1]}mi'

        encoded_query = encoded_query.strip()
        encoded_query = quote(encoded_query)

        if lang is not None:
            encoded_query += f'&l={lang}'

        print(f'[Test URL] https://twitter.com/search?q={encoded_query}')
        return encoded_query

    @staticmethod
    def stream(query):
        known_tweets = CircularOrderedSet(50)
        while True:
            try:
                for tweet in TwitterScraper.search(query):
                    if tweet['id'] not in known_tweets:
                        known_tweets.add(tweet['id'])
                        yield tweet
            except Exception:
                time.sleep(1)

    @staticmethod
    def search(query, deep=False):
        query = TwitterScraper._encode_query(query)

        has_more_items = True
        min_position = -1

        while has_more_items:
            url = f'https://twitter.com/i/search/timeline?f=tweets&vertical=news&q={query}&src=typd&include_available_features=1&include_entities=1&max_position={min_position}&reset_error_state=false'
            done = False
            while not done:
                try:
                    content = TwitterHttpHelper.get_json_response(url)
                    done = True
                except Exception:
                    continue

            items_html = content['items_html']
            has_more_items = content['has_more_items']
            min_position = content['min_position']

            try:
                root = document_fromstring(items_html)
            except lxml.etree.ParserError:
                continue

            tweets_data = root.xpath("//div[@data-tweet-id]")
            tweets_content = root.xpath("//p[@lang]")
            tweets_timestamps = root.xpath("//span[@data-time-ms]")

            if not deep:
                has_more_items = False

            for i, tweet_data in enumerate(tweets_data):
                body_html = tostring(tweets_content[i], encoding='unicode')
                body = TwitterScraper.get_processed_text(body_html)
                tweet_id = tweet_data.attrib['data-tweet-id']
                timestamp = tweets_timestamps[i].attrib['data-time-ms']
                language = tweets_content[i].attrib['lang']

                name = tweet_data.attrib['data-name']
                screen_name = tweet_data.attrib['data-screen-name']
                author_id = tweet_data.attrib['data-user-id']

                tweet = {
                    'user': {
                        'name': name,
                        'screen_name': screen_name,
                        'id': author_id
                    },
                    'id': tweet_id,
                    'language': language,
                    'timestamp': timestamp,
                    'text': body,
                    'url': f'https://twitter.com/{screen_name}/status/{tweet_id}',
                }
                yield tweet

    @staticmethod
    def get_list_members(username, list_name):
        has_more_items = True
        min_position = -1

        while has_more_items:
            url = f'https://twitter.com/{username}/lists/{list_name}/members/timeline?include_available_features=1&include_entities=1&max_position={min_position}&reset_error_state=false'
            content = TwitterHttpHelper.get_json_response(url)

            items_html = content['items_html']
            has_more_items = content['has_more_items']
            min_position = content['min_position']

            try:
                root = document_fromstring(items_html)
            except lxml.etree.ParserError:
                continue

            account_elements = root.xpath(
                "//div[contains(@class, 'account') and @data-screen-name]")

            for account in account_elements:
                name = account.attrib['data-name']
                screen_name = account.attrib['data-screen-name']
                author_id = account.attrib['data-user-id']

                yield {'name': name, 'screen_name': screen_name, 'id': author_id}

    @staticmethod
    def get_followings(username):
        return TwitterScraper.get_followx(username, target='followings')

    @staticmethod
    def get_followers(username):
        return TwitterScraper.get_followx(username, target='followers')

    @staticmethod
    def get_followx(username, target):
        has_more_items = True
        min_position = 0

        while has_more_items:
            url = f'https://mobile.twitter.com/{username}/{target}?lang=en'
            if min_position:
                url += f'&cursor={min_position}'
            content = TwitterHttpHelper.get_html_response(url)

            try:
                root = document_fromstring(content)
            except lxml.etree.ParserError:
                continue

            account_elements = root.xpath("//td[contains(@class, 'screenname')]/a[@name]")

            for account in account_elements:
                screen_name = account.attrib['name']
                yield screen_name

            try:
                min_position = root.xpath(
                    "//div[@class='w-button-more']/a")[0].attrib['href'].split('cursor=')[1]
            except IndexError:
                has_more_items = False

    @staticmethod
    def get_profile(username):
        # TODO url = f'https://mobile.twitter.com/{username}'
        raise NotImplementedError

    @staticmethod
    def get_likes_no(tweet):
        raise NotImplementedError

    @staticmethod
    def get_retweets_no(tweet):
        raise NotImplementedError

    @staticmethod
    def get_replies_no(tweet):
        raise NotImplementedError