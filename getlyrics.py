#!/usr/bin/python

import requests
import lxml.html
import sys
from urllib import urlencode

DEBUG = False

class NoLyricsDivFound(Exception):
    pass

class NoLyricsPageFound(Exception):
    pass

def debug(message):
    if DEBUG:
        print message

def get_lyrics(azlyrics_url):
    debug("Getting lyrics...")

    r = requests.get(azlyrics_url)

    html = lxml.html.fromstring(r.text)
    main = html.get_element_by_id("main")

    # Findnig the artist
    artist = main.find("h2").text
    # Geting rid of the last word, which is always "LYRICS"
    artist = ' '.join(artist.split(' ')[:-1])

    artist = "Artist: " + artist.title()


    # Finding the tile
    title = main.find("b").text
    # Getting rid of the beginning and ending quotes
    title = title[1:-1]

    title = "Title: " + title.title()


    main_divs = main.findall("div")

    lyrics_div = None

    for div in main_divs:
        div_comments = filter(lambda x: type(x) == lxml.html.HtmlComment, div.getchildren())
        if ' start of lyrics ' in map(lambda x: x.text, div_comments):
            lyrics_div = div
            break

    if lyrics_div is None:
        raise NoLyricsDivFound("Could not find div contaning lyrics in the page")

    debug(" Done!")

    result = "\n".join([artist, title, lyrics_div.text_content()])
    return result

def get_azlyrics_url(query):
    debug("Fetching azlyrics url...")
    r = requests.get("http://search.azlyrics.com/search.php?"+urlencode({"q": query}))
    html = lxml.html.fromstring(r.text)
    search_results = html.find_class("sen")

    if len(search_results) == 0:
        raise NoLyricsPageFound("Could not locate lyrics for query " + query)

    link = search_results[0].find("a")
    debug(" Done")
    return link.attrib["href"]

def print_usage():
    print "Usage: " + sys.argv[0] + " <title and artist>"

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    query = ' '.join(sys.argv[1:])
    url = get_azlyrics_url(query)
    lyrics = get_lyrics(url)
    print lyrics.encode('utf-8')
