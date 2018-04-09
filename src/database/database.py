#!/usr/bin/python
# -*- coding: utf-8 -*-
import pyrebase
import os
import json
import optparse
from time import time
import re
from input_data_handler import *

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

def main():

    try:
        f = open(os.path.join(__location__, 'firebase.json'), 'rb+')
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
                    with open(os.path.join(arguments[0]), 'rb+') as f:
                        data = json.load(f)
                        print db.child(location).push(data, user["idToken"]) # DUPLICATE

                # AID THE USER IN CREATING THE
                # CORRECT MODEL FOR THE RIGHT DB_LOCATION
                else:
                    try:
                        print "Input data at database location {0}:".format(location)
                        data = handle_input_data(location)

                        print "Output data at database location {0}:".format(location)
                        print json.dumps(data, indent=4)

                        should_send_data = cast(raw_input("Ready to send it [Y/N]: "), "Y/N")
                        if should_send_data is not True:
                            print "Goodbye."
                        else:
                            response = db.child(location).push(data, user["idToken"])
                            if "name" in response.keys():
                                print "Success. Data is saved at: {0}/{1}/{2}".format(config["databaseURL"], location, response["name"])
                            else:
                                # error handling not complete
                                print "Oops! Something went wrong writing to the database."

                    except ValueError:
                        print "Something went wrong."

        else:
            print "--email and --password options are missing."

if __name__ == "__main__":
    main()
