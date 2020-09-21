#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import randint
import urllib3
import json

session = urllib3.PoolManager()

class TwitterHttpHelper:
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
            '78.0.3904.87',
            '77.0.3865.90',
            '75.0.3770.100',
            '60.0.3112.113',
            '60.0.3112.90',
            '57.0.2987.133',
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
        r = session.request('GET', url=url, headers=TwitterHttpHelper.get_json_header())
        return json.loads(r.data.decode('utf-8'))

    @staticmethod
    def get_html_response(url):
        r = session.request('GET', url=url, headers=TwitterHttpHelper.get_html_header())
        return r.data.decode('utf-8')
