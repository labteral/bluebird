<h1 align="center">
<b>bluebird</b>
</h1>

<h3 align="center">
<b>An unofficial Twitter SDK for Python</b>
</h3>

<p align="center">
    <a href="https://pepy.tech/project/bluebird/"><img alt="Downloads" src="https://img.shields.io/badge/dynamic/json?style=flat-square&maxAge=3600&label=downloads&query=$.total_downloads&url=https://api.pepy.tech/api/projects/bluebird"></a>
    <a href="https://pypi.python.org/pypi/bluebird/"><img alt="PyPi" src="https://img.shields.io/pypi/v/bluebird.svg?style=flat-square"></a>
    <!--<a href="https://github.com/brunneis/pygram/releases"><img alt="GitHub releases" src="https://img.shields.io/github/release/brunneis/bluebird.svg?style=flat-square"></a>-->
    <a href="https://github.com/brunneis/bluebird/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/github/license/brunneis/bluebird.svg?style=flat-square&color=green"></a>
</p>

<p align="center">
    <a href="https://www.buymeacoffee.com/brunneis" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="35px"></a>
</p>

# Installation

> bluebird works with Python +3.7

You can install the `bluebird` package directly with `pip` / `pip3`:

```bash
pip install bluebird
```

# Twitter

To work with the Twitter Scraper module you have to import the corresponding module first:

```python
from bluebird import BlueBird
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

If not specified, the tweets will match ordinary keywords.

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
for tweet in BlueBird().search(query):
    print(tweet)
```

Search for all the available results:

```python
for tweet in BlueBird().search(query, deep=True):
    print(tweet)
```

## Stream

Search constantly for new results:

```python
for tweet in BlueBird().stream(query)
    print(tweet)
```

---
---
---
> Warning! It seems that Twitter disabled old endpoints so the following functionalities may not work.

## List members

```python
BlueBird().get_list_members(username, list_name)
```

Example:

```python
>>> for user in BlueBird().get_list_members('dalvarez37', 'xiii-legislatura-congreso'):
...     print(user)

{'name': 'Eva Bravo', 'screen_name': 'EvaBravoBarco', 'id': '1116022190154113030'}
{'name': 'Juan José Cortés', 'screen_name': 'JuanjoCortesHu', 'id': '1110994911741050888'}
{'name': 'José Ignacio Echániz', 'screen_name': 'JIEchaniz', 'id': '1110628846242594820'}

...
```

## Followings

```python
BlueBird().get_followings(username)
```

Example:

```python
>>> for username in BlueBird().get_followings('dalvarez37'):
...     print(username)

alfonsopmedina
juancarlosgp_
lafuentejuancar

...
```

## Followers

```python
BlueBird().get_followers(username)
```

Example:

```python
>>> for username in BlueBird().get_followers('dalvarez37'):
...     print(username)

jsierradelarosa
lafuentejuancar
crismadrid011

...
```
