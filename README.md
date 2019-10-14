# Polypus

Polypus is a multi-threaded Web scraper built and designed originally in 2014 for massive text extraction from Twitter. It was implemented in Java 8. Its purpose was to replace the Twitter Firehose API collecting massive amounts of tweets in real time without specifying any target. In [this paper](https://arxiv.org/pdf/1801.03710.pdf) its functioning is explained in detail.

Polypus 5, released in 2019, is a Python library for social media scraping. It supports Twitter and will support Reddit in the short term. You can expect future support for Instagram and LinkedIn in the future. Currently, the original Polypus software is discontinued. A Polypus 5 firehose alike horizontal scalable system will be implemented with the [Catenae Framework](https://github.com/catenae) in the short term.


# Installation
> Polypus only works with Python +3.7

You can install the `polypus` package directly with `pip` / `pip3`:
```bash
pip install polypus
```

# Twitter
To work with the Twitter Scraper module you have to import the corresponding module first:

```python
from polypus import TwitterScraper
```

The available methods and its usage are described below.


## Query language

For both `search` and `stream` methods a JSON-based query language must be used.
The query must be specified as a Python dictionary containing a list of fields and global options.

### Global options
---

#### lang
This option will force the tweets to match a given language. The language must be specified with its ISO 639-1 two-letter code (e.g., `es` for Spanish).

#### since
This parameter refers to the minimum allowed date. It has to be specified in the `YYYY-MM-DD` format.

#### until
This parameter refers to the maximum allowed date. It has to be specified in the `YYYY-MM-DD` format.

#### near
It has to be specified with a `tuple` object composed of a text location and a range in miles (e.g., `('Santiago de Compostela', 15)`).

### Fields
---

A query can specify multiple fields which are Python dictionaries with one or more keys and values:

#### items
This is a list of strings, either terms or phrases.

#### exact
If `True`, the specified terms or phrases must match exactly as they were written on the tweets (case/latin insensitive). If this flag is set, the `target` parameter will be ignored.

#### match
If not specified, the tweets will match every item.
- `'any'` (the tweets must match at least one of the items)
- `'none'` (the tweets won't match any item)

#### target
If not specified the
- `'hashtag'` (tweets containing `#item`)
- `'mention'` (tweets mentioning `@item`)
- `'from'` (tweets written by `@item`)
- `'to'` (tweets that are replies to `@item`)


### Examples
---
Search for tweets containing 'Santiago' and not 'Chile':
```python
query = {
    'fields': [
        {'items': ['Santiago']},
        {'items': ['Chile'], 'match': 'none'},
    ]
}
```

Search for tweets containing 'Santiago' and not 'Chile' written in Spanish:
```python
query = {
    'fields': [
        {'items': ['Santiago']},
        {'items': ['Chile'], 'match': 'none'},
    ],
    'lang': 'es'
}
```


Search for tweets containing 'Santiago' and not 'Chile' written in Spanish within a 50-mile radius around Santiago de Compostela.
```python
query = {
    'fields': [
        {'items': ['Santiago']},
        {'items': ['Chile'], 'match': 'none'},
    ],
    'lang': 'es',
    'near': ('Santiago de Compostela', 50)
}
```

Search for tweets containing 'Santiago' and not 'Chile' written in Spanish within a 50-mile radius around Santiago de Compostela in September 2019.
```python
query = {
    'fields': [
        {'items': ['Santiago']},
        {'items': ['Chile'], 'match': 'none'},
    ],
    'lang': 'es',
    'near': ('Santiago de Compostela', 50),
    'since': '2019-09-01',
    'until': '2019-09-30'
}
```

## Search
Search for the last 20 results:
```python
for tweet in TwitterScraper.search(query):
    print(tweet)
```

Search for all the available results:
```python
for tweet in TwitterScraper.search(query, deep=True):
    print(tweet)
```


## Stream
Search constantly for new results:
```python
for tweet in TwitterScraper.stream(query)
    print(tweet)
```
## List members


```python
TwitterScraper.get_list_members(username, list_name)
```
Example:
```python
>>> for user in TwitterScraper.get_list_members('dalvarez37', 'xiii-legislatura-congreso'):
...     print(user)

{'name': 'Eva Bravo', 'screen_name': 'EvaBravoBarco', 'id': '1116022190154113030'}
{'name': 'Juan José Cortés', 'screen_name': 'JuanjoCortesHu', 'id': '1110994911741050888'}
{'name': 'José Ignacio Echániz', 'screen_name': 'JIEchaniz', 'id': '1110628846242594820'}

...
```

## Followings
```python
TwitterScraper.get_followings(username, list_name)
```
Example:
```python
>>> for username in TwitterScraper.get_followings('dalvarez37'):
...     print(username)

alfonsopmedina
juancarlosgp_
lafuentejuancar

...
```


## Followers
```python
TwitterScraper.get_followers(username, list_name)
```
Example:
```python
>>> for username in TwitterScraper.get_followers('dalvarez37'):
...     print(username)

jsierradelarosa
lafuentejuancar
crismadrid011

...
```

# Reddit
> Not yet available

# Instagram
> Not yet available

# LinkedIn
> Not yet available
