# TODO
# urrlib <-> requests

import requests
from .http_helper import TwitterHttpHelper as HttpHelper
from urllib.parse import quote
from orderedset import OrderedSet
from lxml.html import document_fromstring
from lxml.etree import tostring, ParserError
import time
import re


class CircularOrderedSet(OrderedSet):
    def __init__(self, size=0):
        super(CircularOrderedSet, self).__init__()
        self.size = size

    def add(self, value):
        super(CircularOrderedSet, self).add(value)
        self._truncate()

    def _truncate(self):
        if len(self) > self.size:
            self.pop(last=False)


class BlueBird:

    API_WEB = 'web'
    API_1_1 = '1_1'
    API_2 = '2'

    emoji_flag = '24f2c44c'
    emoji_regex = re.compile(r'alt="(.{0,8})"')
    img_regex = re.compile(r'<img([\w\W]+?)/>')

    ACCESS_TOKEN = 'AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'

    def __init__(self):
        self.guest_tokens = list()
        self._request_guest_token()
        self.user_ids = dict()

    @staticmethod
    def get_emojis(text):
        return re.findall(BlueBird.emoji_regex, text)

    @staticmethod
    def get_tagged_html(text):
        return re.sub(BlueBird.img_regex, f'  {BlueBird.emoji_flag}  ', text)

    @staticmethod
    def insert_emojis(emojis, text):
        for emoji in emojis:
            text = text.replace(f' {BlueBird.emoji_flag} ', emoji, 1)
        text = text.replace(f' {BlueBird.emoji_flag} ', '')
        return text

    @staticmethod
    def post_process_text(text):
        text = text.replace('…', '')
        text = re.sub(r'\s+', ' ', text)
        return text

    @staticmethod
    def get_processed_text(html_content):
        emojis = BlueBird.get_emojis(html_content)
        tagged_html = BlueBird.get_tagged_html(html_content)
        tagged_text = document_fromstring(tagged_html).text_content()
        tagged_text_emojis = BlueBird.insert_emojis(emojis, tagged_text)
        text = BlueBird.post_process_text(tagged_text_emojis)
        return text.strip()

    @staticmethod
    def _get_auth_header(guest_token=None):
        headers = {'authorization': f'Bearer {BlueBird.ACCESS_TOKEN}'}
        if guest_token is not None:
            headers['x-guest-token'] = guest_token
        return headers

    @staticmethod
    def _get_guest_token():
        url = 'https://api.twitter.com/1.1/guest/activate.json'
        headers = BlueBird._get_auth_header()
        response = requests.post(url, headers=headers)
        return response.json()['guest_token']

    def _get_first_guest_token(self):
        return self.guest_tokens[0]

    def _rotate_guest_token(self):
        self.guest_tokens.append(self._pop_guest_token())

    def _pop_guest_token(self):
        return self.guest_tokens.pop(0)

    def _request_guest_token(self):
        guest_token = self._get_guest_token()
        self.guest_tokens.append(guest_token)

    def _get_api_response(self, url):
        first_guest_token = None
        valid_guest_token_found = False

        data = None
        while not valid_guest_token_found:
            guest_token = self._get_first_guest_token()

            if first_guest_token is None:
                first_guest_token = guest_token
            elif first_guest_token == guest_token:
                self._request_guest_token()

            headers = self._get_auth_header(guest_token=guest_token)
            response = requests.get(url, headers=headers)

            data = response.json()
            if 'errors' in data:
                error_message = data['errors'][0]['message']
                if error_message == 'Forbidden.':
                    self._pop_guest_token()
                elif error_message == 'Bad request.':
                    return
                else:
                    self._rotate_guest_token()
            else:
                valid_guest_token_found = True

        return data

    def get_user(self, username):
        url = f'https://api.twitter.com/1.1/users/show.json?screen_name={username}'
        return self._get_api_response(url)

    def get_user_id(self, username):
        if username not in self.user_ids:
            user_id = self.get_user(username)['id']
            self.user_ids[username] = user_id
        return self.user_ids[username]

    @staticmethod
    def _update_url_with_params(url, params):
        first = True
        for key, value in params.items():
            symbol = '&'
            if first:
                symbol = '?'
                first = False
            url += f'{symbol}{key}={value}'
        return url

    @staticmethod
    def _encode_query(query) -> str:
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

        match = None
        if 'match' in query:
            match = query['match']

        fields = []
        if 'fields' in query:
            fields = query['fields']

        for field in fields:
            target = None
            if 'target' in field:
                target = field['target']

            items = field['items']

            field_match = None
            if 'match' in field:
                field_match = field['match']

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

            if field_match == 'any':
                marginal_query = ' OR '.join(marginal_query.split())
            elif field_match == 'none':
                marginal_query = '-' + ' -'.join(marginal_query.split())

            if match == 'any':
                if encoded_query:
                    encoded_query += ' OR ' + marginal_query
                else:
                    encoded_query = marginal_query
            else:
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

        print(f'[Test URL] https://twitter.com/search?f=tweets&vertical=default&q={encoded_query}')
        return encoded_query

    def _get_tweets_web(self, url, deep, sleep_time, query_type, min_tweets):
        seen_tweets = 0

        if query_type == 'user':
            position = ''
        elif query_type == 'search':
            position = '&max_position=-1'

        # Generalizar con params como los otros
        if not '?' in url:
            url += '?'
        else:
            url += '&'
        url += 'include_available_features=1&include_entities=1'

        has_more_items = True
        while has_more_items:
            new_url = f'{url}{position}&reset_error_state=false'

            done = False
            while not done:
                try:
                    content = HttpHelper.get_json_response(new_url)
                    done = True
                except Exception:
                    continue

            items_html = content['items_html']
            try:
                root = document_fromstring(items_html)
            except ParserError:
                continue

            has_more_items = content['has_more_items']
            if not deep:
                has_more_items = False

            if 'min_position' in content:
                position = f"&max_position={content['min_position']}"
            else:
                continue

            tweets_data = root.xpath("//div[@data-tweet-id]")
            tweets_content = root.xpath("//p[@lang]")
            tweets_timestamps = root.xpath("//span[@data-time-ms]")

            for i, tweet_data in enumerate(tweets_data):
                seen_tweets += 1

                body_html = tostring(tweets_content[i], encoding='unicode')
                body = BlueBird.get_processed_text(body_html)
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

            # Restart if the min_tweets target wasn't achieved
            if not has_more_items and seen_tweets < min_tweets:
                seen_tweets = 0
                has_more_items = True
                if query_type == 'user':
                    position = ''
                elif query_type == 'search':
                    position = '&max_position=-1'
                continue

            if deep:
                time.sleep(sleep_time)

    def _search_web(self, query, deep, count, sleep_time, min_tweets):
        encoded_query = BlueBird._encode_query(query)
        base_url = f'https://twitter.com/i/search/timeline?f=tweets&vertical=news&q={encoded_query}&src=typd'
        yield from self._get_tweets_web(base_url, deep, sleep_time, 'search', min_tweets)

    def _user_timeline_web(self, username, deep, count, include_replies, sleep_time, min_tweets):
        base_url = f'https://twitter.com/i/profiles/show/{username}/timeline/tweets'
        yield from self._get_tweets_web(base_url, deep, sleep_time, 'user', min_tweets)

    def _get_tweets_2(self, url, deep, sleep_time, min_tweets):
        seen_tweets = 0

        cursor = None
        done = False

        while not done:
            new_url = url
            if cursor is not None:
                new_url += f'&cursor={cursor}'

            response = self._get_api_response(new_url)
            if response is None:
                break

            tweets = response['globalObjects']['tweets']

            done = True
            for tweet_id, tweet in tweets.items():
                seen_tweets += 1

                tweet['id'] = tweet_id
                done = False
                yield tweet

            try:
                cursor = response['timeline']['instructions'][0]['addEntries']\
                ['entries'][-1]['content']['operation']['cursor']['value']
            except (KeyError, IndexError):
                try:
                    cursor = response['timeline']['instructions'][-1]['replaceEntry']\
                    ['entry']['content']['operation']['cursor']['value']
                except KeyError:
                    done = True

            # Restart if the min_tweets target wasn't achieved
            if not done and seen_tweets < min_tweets:
                seen_tweets = 0
                cursor = None
                done = False
                continue

    def _search_2(self, query, deep, count, sleep_time, min_tweets):
        if count > 200:
            count = 200

        encoded_query = BlueBird._encode_query(query)

        base_url = 'https://api.twitter.com/2/search/adaptive.json'
        params = {'q': encoded_query, 'count': count, 'sorted_by_time': 'true', 'tweet_mode': 'extended'}

        url = BlueBird._update_url_with_params(base_url, params)
        print(url)

        yield from self._get_tweets_2(url, deep, sleep_time, min_tweets)

    def _user_timeline_2(self, username, deep, count, include_replies, sleep_time, min_tweets):
        user_id = self.get_user_id(username)

        if count > 200:
            count = 200

        if include_replies:
            include_tweet_replies = 'true'
        else:
            include_tweet_replies = 'false'

        url = f'https://api.twitter.com/2/timeline/profile/{user_id}.json'
        params = {
            'count': count,
            'include_entities': 'false',
            'tweet_mode': 'extended',
            'include_reply_count': 0,
            'include_user_entities': 'false',
            'send_error_codes': 'false',
            'include_tweet_replies': include_tweet_replies
        }

        url = BlueBird._update_url_with_params(url, params)

        yield from self._get_tweets_2(url, deep, sleep_time, min_tweets)

    def _get_tweets_1_1(self, url, deep, sleep_time, min_tweets):
        seen_tweets = 0

        max_id = None
        done = False
        while not done:
            new_url = url
            if max_id is not None:
                new_url += f'&max_id={max_id}'

            tweets = None
            attempts = 10
            retry = True
            while attempts and retry and not done:
                attempts -= 1
                response = self._get_api_response(new_url)

                # Search
                if 'statuses' in response:
                    tweets = response['statuses']
                else:
                    tweets = response

                retry = True
                for tweet in tweets:
                    retry = False
                    seen_tweets += 1

                    if max_id == tweet['id']:
                        done = True
                    else:
                        max_id = tweet['id']
                        yield tweet

            if not tweets:
                done = True

            # Restart if the min_tweets target wasn't achieved
            if done and seen_tweets < min_tweets:
                done = False
                continue

            if not deep:
                done = True
            else:
                time.sleep(sleep_time)

    def _search_1_1(self, query, deep, count, sleep_time, min_tweets):
        if count > 100:
            count = 100

        encoded_query = BlueBird._encode_query(query)

        base_url = 'https://api.twitter.com/1.1/search/tweets.json'
        params = {'q': encoded_query, 'count': count, 'result_type': 'recent', 'include_entities': 'false'}
        url = BlueBird._update_url_with_params(base_url, params)

        yield from self._get_tweets_1_1(url, deep, sleep_time, min_tweets)

    def _user_timeline_1_1(self, username, deep, count, include_replies, sleep_time, min_tweets):
        if count > 200:
            count = 200

        if include_replies:
            exclude_tweet_replies = 'false'
        else:
            exclude_tweet_replies = 'true'

        base_url = f'https://api.twitter.com/1.1/statuses/user_timeline.json'
        params = {
            'screen_name': username,
            'trim_user': 'true',
            'exclude_replies': exclude_tweet_replies,
            'count': count
        }
        url = BlueBird._update_url_with_params(base_url, params)

        yield from self._get_tweets_1_1(url, deep, sleep_time, min_tweets)

    def search(self, query, deep=False, count=100, sleep_time=0, min_tweets=0, mode=API_WEB):
        return getattr(self, f'_search_{mode}')(query, deep, count, sleep_time, min_tweets)

    def user_timeline(self,
                      username,
                      deep=False,
                      count=200,
                      include_replies=True,
                      sleep_time=0,
                      min_tweets=0,
                      mode=API_WEB):
        return getattr(self, f'_user_timeline_{mode}')(username, deep, count, include_replies, sleep_time, min_tweets)

    def stream(self, query, sleep_time=0, mode=API_WEB):
        known_tweets = CircularOrderedSet(50)
        while True:
            try:
                for tweet in self.search(query, mode=mode):
                    if tweet['id'] not in known_tweets:
                        known_tweets.add(tweet['id'])
                        yield tweet
            except Exception:
                pass
            time.sleep(sleep_time)

    @staticmethod
    def get_list_members(username, list_name):
        has_more_items = True
        min_position = -1

        while has_more_items:
            url = f'https://twitter.com/{username}/lists/{list_name}/members/timeline?include_available_features=1&include_entities=1&max_position={min_position}&reset_error_state=false'
            content = HttpHelper.get_json_response(url)

            items_html = content['items_html']

            try:
                root = document_fromstring(items_html)
            except ParserError:
                continue

            has_more_items = content['has_more_items']
            min_position = content['min_position']

            account_elements = root.xpath("//div[contains(@class, 'account') and @data-screen-name]")

            for account in account_elements:
                name = account.attrib['data-name']
                screen_name = account.attrib['data-screen-name']
                author_id = account.attrib['data-user-id']

                yield {'name': name, 'screen_name': screen_name, 'id': author_id}

    @staticmethod
    def get_followings(username):
        return BlueBird.get_followx(username, target='followings')

    @staticmethod
    def get_followers(username):
        return BlueBird.get_followx(username, target='followers')

    @staticmethod
    def get_followx(username, target):
        has_more_items = True
        min_position = 0

        while has_more_items:
            url = f'https://mobile.twitter.com/{username}/{target}?lang=en'
            if min_position:
                url += f'&cursor={min_position}'
            content = HttpHelper.get_html_response(url)

            try:
                root = document_fromstring(content)
            except ParserError:
                continue

            account_elements = root.xpath("//td[contains(@class, 'screenname')]/a[@name]")

            for account in account_elements:
                screen_name = account.attrib['name']
                yield screen_name

            try:
                min_position = root.xpath("//div[@class='w-button-more']/a")[0].attrib['href'].split('cursor=')[1]
            except IndexError:
                has_more_items = False

    @staticmethod
    def get_hashtags(place):
        raise NotImplementedError

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