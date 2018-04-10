#!/usr/bin/python
# -*- coding: utf-8 -*-
import pyrebase
import os
import json
import optparse
from time import time
import re
from thumbnails import Thumbnails

def main():

    try:
        f = open('../firebase.json', 'rb+')
    except IOError:
        print "Did you remember to include in the directory a firebase.json file"

    else:
        config = json.load(f)
        firebase = pyrebase.initialize_app(config)

        storage = firebase.storage()
        auth = firebase.auth()

        p = optparse.OptionParser()
        p.add_option('--put', '-p', type="str", help="put file in storage with proper storage-path-rule")
        p.add_option('--thumbnails', '-t', type="str", help="Toggles thumbnails upload on/off")
        p.add_option('--email', type="str", help="firebase auth email")
        p.add_option('--password', type="str", help="firebase auth password")
        options, arguments = p.parse_args()

        if options.email and options.password:
            user = auth.sign_in_with_email_and_password(options.email, options.password)
            if user is None:
                raise ValueError("User is not signed in. Please sign in and make sure you have the right permissions.")

            if options.put:
                completed_uploads = {}
                filepath = options.put.strip("/")

                # thumbnail logic goes here.
                thumbs_toggle = options.thumbnails
                if thumbs_toggle is None:
                    thumbs_toggle = 0
                else:
                    thumbs_toggle = int(thumbs_toggle)

                for i in xrange(len(arguments)):
                    completed_uploads = {}

                    argpath = arguments[i]

                    if thumbs_toggle == 0:
                        with open(argpath, 'rb+') as f:
                            response = storage.child(filepath).put(f, user['idToken'])
                            if "name" in response.keys() and "bucket" in response.keys():
                                print "Success. File is saved at: https://{0}/{1}".format(response["bucket"], response["name"])
                                completed_uploads[filepath] = storage.child(response["name"]).get_url(None)
                            else:
                                print "Oops! Something went wrong writing to storage."

                    else:
                        completed_uploads[str(i)] = {}

                        _format = False
                        for x in [".jpeg", ".jpg"]:
                            if argpath.endswith(x):
                               _format = True
                               break

                        if _format is False:
                            raise ValueError("[Only supports jpg, jpeg] File of unkown type: " + argpath)

                        thumbs = Thumbnails("thumbnail_rules.json")
                        thumbs_resp = thumbs.generate(argpath, "/tmp/thumbnails")

                        for name, path in thumbs_resp.iteritems():
                            with open(path, 'rb+') as f:
                                response = storage.child("/{0}/{1}/{2}".format(filepath, str(i), name)).put(f, user['idToken'])
                                if "name" in response.keys() and "bucket" in response.keys():
                                    print "Success. File is saved at: https://{0}/{1}".format(response["bucket"], response["name"])
                                    completed_uploads[str(i)][name] = storage.child(response["name"]).get_url(None)

                                else:
                                    print "Oops! Something went wrong writing to storage."

                print "Completed Uploads:"
                print json.dumps(completed_uploads, indent=4, sort_keys=True)
        else:
            print "--email and --password options are missing."

if __name__ == "__main__":
    main()
