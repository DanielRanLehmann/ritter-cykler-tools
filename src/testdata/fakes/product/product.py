#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import json
from time import time
from loremipsum import *
import random
import math
import os
from .. import firebase_pushid

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

__ytapikey__ = "UNKOWN"

with open(os.path.join(__location__, 'youtube-credentials.json'), 'rb+') as f:
    creds = json.load(f)
    __ytapikey__ = creds["apikey"]

# cached responses goes here.
cached_names = {
    "Bike": [],
    "Bike Helmet": []
}

cached_images = {
    "Bike": [],
    "Bike Helmet": []
}

cached_img_headers = {}

# DEPRECATED class
class Product(object):
    def __init__(self, data={}):
        self.__dict__ = data

    def json(self):
        return self.__dict__

    def valid(self):
        return True

# helpers
# but can also be considered separate modules
def randcat():
    cats = ["Bike", "Bike Helmet"]
    return cats[random.randint(0, len(cats)-1)]

def randsubcat(cat):
    if cat is None:
        raise ValueError('cat parameter is null, please specify a category.')

    subcats = {
        "Bike": ["Mountain Bike", "Kids Bike", "Sports Bike", "City Bike"],
        "Bike Helmet": ["Adult Helmet", "Racer Helmet", "Kids Helmet"]
    }

    return subcats[cat][random.randint(0, len(subcats[cat])-1)]

def randsizes(cat):
    if cat is None:
        raise ValueError('cat parameter is null, please specify a category.')

    _sizes = ["*"] # one size fits all.

    if cat is not "Bike":
        _sizes = ["xs", "s", "m", "l", "xl", "xxl"]
        no_sizes = random.randint(0, len(_sizes)-1)
        for i in range(no_sizes):
            del _sizes[random.randint(0, len(_sizes)-1)]

    return _sizes

def randqty(sizes):
    if sizes is None:
        raise ValueError('sizes parameter is null, please specify some sizes.')

    total_no_items = 150
    _qty = {}
    for size in sizes:
        soldout = bool(random.randint(0, 1))
        _qty[size] = random.randint(0, total_no_items) if soldout is False else 0

    return _qty

def randprice(cat, subcat):
    if cat is None and subcat is None:
        raise ValueError("cat and or subcat parameter is null, please specify a category and subcategory")

    priceranges = {
        "Bike": {
            "Mountain Bike": [1500,10000],
            "Kids Bike": [1000,4000],
            "Sports Bike": [15000,200000],
            "City Bike": [1500,7500]
        },

        "Bike Helmet": {
            "Adult Helmet": [250,1000],
            "Racer Helmet": [1000,5000],
            "Kids Helmet": [100,500]
        }
    }

    _range = priceranges[cat][subcat]
    _min, _max = _range[0], _range[1]

    return math.ceil(float(random.randint(_min, _max)))

def randdiscount(cat, subcat):
    if cat is None and subcat is None:
        raise ValueError("cat and or subcat parameter is null, please specify a category and subcategory")

    discountranges = {
        "Bike": {
            "Mountain Bike": [0,5],
            "Kids Bike": [0,25],
            "Sports Bike": [0,5],
            "City Bike": [0,10]
        },

        "Bike Helmet": {
            "Adult Helmet": [0,5],
            "Racer Helmet": [0,5],
            "Kids Helmet": [0,10]
        }
    }

    cointoss = bool(random.randint(0, 1))
    _discount = 0.0
    if bool(cointoss):
        _range = discountranges[cat][subcat]
        _min, _max = _range[0], _range[1]
        _discount = float(random.randint(_min, _max)) / 100.0

    return _discount

def randchannel(channel_id):
    if channel_id is None:
        raise ValueError("channel_id parameter is null, please specify a channel_id")

def randvideo(cat, api_key):
    if cat is None or api_key is None:
        raise ValueError("either cat or api_key parameter is null, please specify either a category or an api_key")


    url = "https://www.googleapis.com/youtube/v3/search"

    channel_ids = {
        "Bike": {
            "Colnago": "UCOYdXcCk_YmZXDRgznQv2nw",
            "Pinarello": "UCS5-VHtZE38jFhfxTZhcbzw",
            "Principia": "UCzMtPNBN9vTkLrFdsUbhVZQ",
            "Trek": "UCD9U24ny8q-mh25gCWfjV9g",
            "Giro": "UC6VDkpvLPIifUfNt4z-EsQQ",
            "Cube": "UCF9SrU6740dK8TmW9adIRkQ"
        },

        "Bike Helmet": {
            "Limar": "UC0jXP7KfLejitpuguWC7AjQ",
            "Reynolds": "UCjGiJWi5s9TSRSP-YYA9N0Q",
            "Nutcase": "UCNPs1CEILEwbn1cxtmWAB4g",
            "Bell": "UCZh6DHHLYpsNyxFztHXT4iA",
            "Mavic": "UCvCWdLK5BKIA0OPhv9LyGug",
        },

        "Shoes": {
            "Sidi": "UCaFplT7jZpbzbPe8nTGHTUg"
        },

        "Clothes": {
            "Nalini": "UCbwmXB_Ir9hxHRC8ED3XEEg",
        },

        "Wheels": {
            "Spinergy": "UCWu50qdiG1168_7Prn6L0_g",
            "Zipp": "UCfqe0wER0mdcpsI0JRpzisA"
        },

        "Apparel": {
            "Oakley": "UCgn0XMUGLhuDVw4lETlVvIw"
        },

        "Technology": {
            "Garmin": "UC6vopISsINRLQ8seRlI_LtA"
        }

    }
    params = {
        "key": api_key,
        "channelId": channel_ids[cat].values()[random.randint(0, len(channel_ids[cat].values()) - 1)],
        "part": "snippet,id",
        "order": "date",
        "maxResults": "20"
    }

    response = requests.request("GET", url, params=params)

    data = response.json()
    videourl = None
    if bool(data["items"]):
        videourls = []
        for item in data["items"]:
            if item["id"]["kind"] == "youtube#video":
                videourls.append("https://www.youtube.com/watch?v={0}".format(item["id"]["videoId"]))

        videourl = videourls[random.randint(0, len(videourls)-1)]

    return videourl

def scrape_names(url, cat):
    matches = []

    req  = requests.get(url) # check for url validity?
    data = req.text
    soup = BeautifulSoup(data, "lxml")

    for link in soup.find_all('a'):

        # LOGIC FOR SCRAPING BIKE NAMES
        if cat == "Bike":
            keyword = cat.lower()
            title = link.find('span')
            if title is not None and keyword in title.text.lower():
                matches.append(title.text)

        # LOGIC FOR SCRAPING BIKE HELMET NAMES
        elif cat == "Bike Helmet":
            keyword = "helmet"
            title = link.get('title')
            if title is not None and keyword in title.lower():
                matches.append(title)

    matches = list(set(matches))
    return matches

def search_imgs(cat, keyword, include_header=True):
    if cat is None or keyword is None:
        raise ValueError("cat and or keyword parameter was null, please specify a category and or keyword")

    if bool(cached_images[cat]) is False:
        url = "https://www.google.dk/search?q={0}&source=lnms&tbm=isch".format(keyword.replace(" ", "+"))

        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
        }
        req = requests.request("GET", url, headers=headers)
        data = req.text
        soup = BeautifulSoup(data, "lxml")

        imgs = []
        img_headers = []
        for div in soup.find_all("div", {"class": "rg_meta notranslate"}):
            imgurl = dict(eval(div.text))["ou"]

            try:
                r = requests.request("HEAD", imgurl, timeout=10)
                if r.status_code == 200:
                    imgs.append(imgurl)
                    if "Content-Type" in r.headers:
                        cached_img_headers[imgurl] = r.headers["Content-Type"].split("/")[-1]
            except requests.exceptions.RequestException as e:
                print e

        cached_images[cat] = imgs

    if bool(cached_images[cat]):

        count = random.randint(1, min(6, len(cached_images[cat]) - 1))
        randimgs = []
        for i in range(count):
            elem = random.choice(cached_images[cat])
            #del imgs[elem]

            randimgs.append(elem)
        return randimgs
    else:
        return None

# support subcats in the future?

def randname(cat):
    if cat is None:
        raise ValueError("cat parameter is null, please specify a category")

    if bool(cached_names[cat]) is False:

        urls = {
          "Bike": [
            "https://www.walmart.com/browse/sports-outdoors/adult-bikes/4125_1081404_1230089"
          ],
          "Bike Helmet": [
              "https://www.amazon.com/adult-bike-helmets/b?ie=UTF8&node=3404571",
              "http://www.wiggle.co.uk/helmets/"
          ]
        }

        names = []
        for url in urls[cat]:
            names.extend(scrape_names(url, cat))
        cached_names[cat] = names

    if bool(cached_names[cat]):
        return cached_names[cat][random.randint(0, len(cached_names[cat]) - 1)]
    else:
        return None

def randurl():
    urls = [
        "http://www.colnago.com/",
        "http://www.pinarello.com/it",
        "https://principia.dk/",
        "https://www.trekbikes.com/dk/da_DK/",
        "http://www.fondriestbici.com/",
        "http://www.giro.com/eu_en/",
        "https://mbk-cykler.dk/",
        "https://www.cube.eu/cube-bikes/",
        "http://www.limar.com/site/index.php?lng=eng",
        "https://reynoldscycling.com/",
        "http://dk.nutcasehelmets.com/",
        "https://www.bellhelmets.com/en_eu/",
        "http://www.ritterplus.dk/",
        "https://www.mavic.com/en-int?noredirect=1",
        "http://www.sidi.com/",
        "https://www.nalini.com/it/ss18/",
        "https://www.spinergy.com/",
        "http://www.zipp.com/",
        "http://www.oakley.com/",
        "http://www.garmin.com/da-DK",
        "https://www.trekbikes.com/us/en_US/bontrager/"
    ]
    return urls[random.randint(0, len(urls)-1)]

def fake_product(category=None):
    if category is None:
        category = randcat()

    p = {}
    p["id"] = firebase_pushid.PushID().next_id()
    p["createdAt"] = time()
    p["currencyCode"] = "DKK"
    p["currencySymbol"] = "kr"
    p["categoryName"] = category
    p["subcategoryName"] = randsubcat(category)

    p["descriptionText"] = get_sentence()
    p["didYouNoticeText"] = get_sentence()
    p["highlightTags"] = get_sentences(2)
    p["manifacturerInfoTags"] = get_sentences(7)
    p["outOfTheBoxTags"] = get_sentences(4)
    p["recommendedText"] = get_sentence()
    p["techSpecTags"] = get_sentences(5)

    p["sizes"] = randsizes(category)
    p["qty"] = randqty(p["sizes"])
    p["inStock"] = sum(p["qty"].values()) > 0

    p["normalPrice"] = randprice(category, p["subcategoryName"])
    p["discountPct"] = randdiscount(category, p["subcategoryName"])
    p["discountPrice"] = math.ceil(p["normalPrice"] - (p["normalPrice"] * p["discountPct"]))

    p["youtubeURL"] = randvideo(category, __ytapikey__)
    p["name"] = randname(category)

    keywords = {
        "Bike": ["pinarello"],
        "Bike Helmet": ["Giro Helmet"]
    }
    p["imageURLs"] = search_imgs(category, keywords[category][random.randint(0, len(keywords[category]) - 1)])
    p["officialProductURL"] = randurl()

    tmp = []
    for i in range(len(p["imageURLs"])):
        tmp.append("IMG_{count}.{format}".format(count=str(i+1).zfill(2), format=str(cached_img_headers[p["imageURLs"][i]])))
    p["imageNames"] = tmp

    return p
