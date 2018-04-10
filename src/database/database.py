#!/usr/bin/python
# -*- coding: utf-8 -*-
import pyrebase
import os
import json
import optparse
from time import time
import re

def main():
    try:
        f = open('../firebase.json', 'rb+')
    except IOError:
        print "Did you remember to include in the directory a firebase.json file"

    else:
        config = json.load(f)
        firebase = pyrebase.initialize_app(config)

        db = firebase.database()
        auth = firebase.auth()

        p = optparse.OptionParser()
        p.add_option('--set', '-s', type="str", help="set data in this location in the [firebase] database")
        p.add_option('--push', '-p', type="str", help="push data in this location in the [firebase] database.")
        p.add_option('--email', type="str", help="firebase auth email")
        p.add_option('--password', type="str", help="firebase auth password")
        options, arguments = p.parse_args()

        if options.email and options.password:
            user = auth.sign_in_with_email_and_password(options.email, options.password)
            if user is None:
                raise ValueError("User is not signed in. Please sign in and make sure you have the right permissions.")

            if options.set:
                with open(os.path.join(arguments[0]), 'rb+') as f:
                    data = json.load(f)
                    location = options.set
                    print db.child(location).set(data, user["idToken"])

            elif options.push:
                location = options.push
                location = location.replace("/", "")

                data = {}

                # FILEPATH IS GIVEN AS ARGUMENT
                if bool(arguments) is True:
                    with open(arguments[0], 'rb+') as f:
                        data = json.load(f)
                        print db.child(location).push(data, user["idToken"]) # DUPLICATE

        else:
            print "--email and --password options are missing."

if __name__ == "__main__":
    main()

# usage
# python database.py --push=/product-drafts --email=danielran11@gmail.com --password=123456
