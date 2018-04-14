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
        p.add_option('--read', '-r', type="str", help="read data at this location in the [firebase] database.")
        p.add_option('--set', '-s', type="str", help="set data at this location in the [firebase] database")
        p.add_option('--push', '-p', type="str", help="push data at this location in the [firebase] database.")
        p.add_option('--email', type="str", help="firebase auth email")
        p.add_option('--password', type="str", help="firebase auth password")
        options, arguments = p.parse_args()

        user = None
        idToken = None
        if options.email and options.password:
            user = auth.sign_in_with_email_and_password(options.email, options.password)
            idToken = user["idToken"]

        #if user is None:
        #    raise ValueError("User is not signed in. Please sign in and make sure you have the right permissions.")


        if options.read:
            response = db.child(options.read.strip("/")).get(idToken)
            if response is None:
                print "an error occurred"
            else:
                print json.dumps(response.val(), indent=4, sort_keys=True)

        if options.set:
            with open(os.path.join(arguments[0]), 'rb+') as f:
                data = json.load(f)
                location = options.set
                print db.child(location).set(data, idToken)

        elif options.push:
            location = options.push
            location = location.replace("/", "") # why not use strip here?

            data = {}

            # FILEPATH IS GIVEN AS ARGUMENT
            if bool(arguments) is True:
                with open(arguments[0], 'rb+') as f:
                    data = json.load(f)
                    print db.child(location).push(data, idToken) # DUPLICATE

        #else:
        #    print "--email and --password options are missing."

if __name__ == "__main__":
    main()
