#!/usr/bin/python
# -*- coding: utf-8 -*-
import pyrebase
import os
import json
import optparse

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

def main():

    firebase = None
    with open(os.path.join(__location__, 'firebase.json'), 'rb+') as f:
        config = json.load(f)
        firebase = pyrebase.initialize_app(config)

    db = firebase.database()
    auth = firebase.auth()

    p = optparse.OptionParser()
    p.add_option('--set', '-s', type="str", help="set data in this location in the [firebase] database")
    p.add_option('--push', '-p', type="str", help="put data in this location in the [firebase] database.")
    p.add_option('--email', type="str", help="firebase auth email")
    p.add_option('--password', type="str", help="firebase auth password")
    options, arguments = p.parse_args()

    if options.email and options.password:
        user = auth.sign_in_with_email_and_password(options.email, options.password)

        if len(arguments) == 1:
            if options.set:
                with open(os.path.join(arguments[0]), 'rb+') as f:
                    data = json.load(f)
                    location = options.set
                    print db.child(location).set(data, user["idToken"])

            elif options.push:
                with open(os.path.join(arguments[0]), 'rb+') as f:
                    data = json.load(f)
                    location = options.push
                    print db.child(location).push(data, user["idToken"])
    else:
        print "Please auth with your firebase email and password."

if __name__ == "__main__":
    main()
