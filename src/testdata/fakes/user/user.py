#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import json
from time import time
import datetime
from loremipsum import *
import random
import math
import os
from .. import firebase_pushid

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

kortforsyningen_config = {}

with open(os.path.join(__location__, 'kortforsygningen.json'), 'rb+') as f:
    kortforsyningen_config = json.load(f)

# use these instead of reading from disk all the time.
email_providers = []
first_names = {
    "female": [],
    "male": []
}
last_names = []

# DEPRECATED class
class User(object):
    def __init__(self, data={}):
        self.__dict__ = data

    def valid(self):
        return True

# helpers
# but can also be used as separate 'modules'
def randgender():
    genders = ['male', 'female']
    return genders[random.randint(0, len(genders)-1)]

# scope can be set to: small, medium, large, max
def randfn(scope, gender=None):
    if scope not in ["small", "medium", "large", "max"]:
        return None

    global first_names

    if gender is None:
        gender = randgender()

    if bool(first_names[gender]) is False:
        # read
        with open("../../danish-names/src/first-names/{gender}/{scope}.txt".format(gender=gender, scope=scope)) as f:
            fns = f.read().split('\n')
            first_names[gender] = fns
            return fns[random.randint(0, len(fns)-1)]

    fns = first_names[gender]
    return fns[random.randint(0, len(fns)-1)]

def randln(scope):
    if scope not in ["small", "medium", "large", "max"]:
        return None

    global last_names
    if bool(last_names) is False:
        with open("../../danish-names/src/last-names/{scope}.txt".format(scope=scope)) as f:
            lns = f.read().split('\n')
            last_names = lns
            return lns[random.randint(0, len(lns)-1)]

    return last_names[random.randint(0, len(last_names)-1)]

def randprovider():
    global email_providers

    if bool(email_providers) is False:
        with open(os.path.join(__location__, 'free_email_provider_domains.txt'), 'rb+') as f:
            providers = f.read().split('\n')
            email_providers = providers
            return email_providers[random.randint(0, len(email_providers)-1)]

    return email_providers[random.randint(0, len(email_providers)-1)]

# https://english.stackexchange.com/questions/210483/birthdate-vs-birthday-i-know-three-other-people-who-share-my-birthdate

def randts(start, end):
    ts = random.randint(start, end)
    return ts

def randdate(start_ts=-688007541, end_ts=952987659, dateformat='%b %m, %Y'): # -688007541 = 1948 (70 years old) , 952987659 = 2000 (18 years old)
    ts = randts(start_ts, end_ts)
    return datetime.datetime.fromtimestamp(ts).strftime(dateformat)

# You can specify a gender
# if no gender specified, a random one will be given.

# NSN LENGTH: https://en.wikipedia.org/wiki/Telephone_numbers_in_Denmark
def randphone(country_code, length):
    number = country_code
    for i in range(4):
        number += str(random.randint(0, 99)).zfill(2)
    return number

def randpicture(gender=None):
    if gender is None:
        gender = randgender()

    _type = "men"
    if gender == "female":
        _type = "women"
    no = random.randint(0, 99)

    return {
        "large": "https://randomuser.me/api/portraits/{0}/{1}.jpg".format(_type, no),
        "medium": "https://randomuser.me/api/portraits/med/{0}/{1}.jpg".format(_type, no),
        "thumbnail": "https://randomuser.me/api/portraits/thumb/{0}/{1}.jpg".format(_type, no)
    }

def closest_addrs(coord, hits):
    addrs = []

    url = "https://services.kortforsyningen.dk/"

    # remove password and login you idiot!!

    params = {
        "login": kortforsyningen_config["login"],
        "password": kortforsyningen_config["password"],
        "servicename": "RestGeokeys_v2",
        "method": "nadresse",
        "geop": "{lng}, {lat}".format(lng=coord[1], lat=coord[0]),
        "hits": str(hits),
        "geometry": "true",
        "georef": "EPSG:4326"
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, params=params)
    data = response.json()

    # right formatting.
    # Klampenborgvej 88, 2800 Kongens Lyngby

    for feature in data["features"]:
        properties = feature["properties"]

        # check for nullability
        street = properties["vej_navn"].encode('utf-8')
        no = properties["husnr"].encode('utf-8')
        postcode = properties["postdistrikt_kode"].encode('utf-8')
        city = properties["postdistrikt_navn"].encode('utf-8')

        geometry = feature["geometry"]
        coordinate = geometry["coordinates"] # note: the coordinate points are reversed
        lat = coordinate[1]
        lng = coordinate[0]

        addrs.append({
            "formattedAddress": "{street} {no}, {postcode} {city}".format(street = street, no = no, postcode = postcode, city = city),
            "address": {
                "street": street,
                "no": no,
                "postcode": postcode,
                "city": city,
                "countryName": "Denmark",
                "countryCode": "DK",
                "coordinate": {
                    "lat": lat,
                    "lng": lng
                }
            }
        })

    return addrs

def fetch_muni_details(name):
    url = "https://services.kortforsyningen.dk/"

    params = {
        "login": kortforsyningen_config["login"],
        "password": kortforsyningen_config["password"],
        "servicename" : "RestGeokeys_v2",
        "method" : "kommune",
        "komnavn" : "Kolding",
        "geometry" : "true",
        "georef" : "EPSG:4326"
    }

    headers = { 'Content-Type': 'Application/json' }

    response = requests.request("GET", url, headers=headers, params=params)
    return response.json()

def randmuni():
    url = "http://dawa.aws.dk/kommuner/"
    response = requests.request("GET", url)
    munis = response.json()

    muni = munis[random.randint(0, len(munis)-1)]
    muni_name = muni["navn"]
    return fetch_muni_details(muni_name)

# helper method for randpoint
# http://alienryderflex.com/polygon/
def inside(point, bbox):
    # x1 < x < x2 and y1 < y < y2
    return bbox[1] < point[0] < bbox[3] and bbox[0] < point[1] < bbox[2]

# Core logic taken from:
# https://gis.stackexchange.com/questions/163044/mapbox-how-to-generate-a-random-coordinate-inside-a-polygon
def randpoint(bbox):
    sw = (bbox[1], bbox[0])
    ne = (bbox[3], bbox[2])

    x_min = sw[0]
    x_max = ne[0]
    y_min = ne[1]
    y_max = sw[1]

    lat = x_min + (random.random() * (x_max - x_min))
    lng = y_min + (random.random() * (y_max - y_min))

    point = (lat, lng)

    if inside(point, bbox):
        return point
    else:
        return randpoint(bbox)

def randaddr():
    return None

def fake_user(gender=None):
    if gender is None:
        gender = randgender()

    u = {}
    u["id"] = firebase_pushid.PushID().next_id()
    u["isEmployee"] = False
    u["gender"] = gender
    u["firstName"] = randfn("large", u["gender"])
    u["lastName"] = randln("large")
    u["fullName"] = u["firstName"] + " " + u["lastName"]
    u["email"] = "{fn}.{ln}@{provider}".format(fn=u["firstName"].lower(), ln=u["lastName"].lower(), provider=randprovider())
    u["phone"] = randphone("+45", 8)
    u["birthdate"] = randdate()
    u["picture"] = randpicture(u["gender"])

    muni = randmuni()
    bbox = muni["features"][0]["bbox"]
    addr_resp = closest_addrs(randpoint(bbox), 1)

    u["formattedAddress"] = addr_resp[0]["formattedAddress"]
    u["address"] = addr_resp[0]["address"]

    return u
