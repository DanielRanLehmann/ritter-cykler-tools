#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from fakes.product.product import fake_product
from fakes.user.user import fake_user
import optparse
import os

class TestData:
    def __init__(self, style="default"):
        self.set_style(style)

    def set_style(self, astyle):
        if astyle is None:
            raise ValueError("please specify a style.")

        self.style = astyle
        if astyle == "default": self.tmp_fakes = []
        elif astyle == "firebase": self.tmp_fakes = {}

    def create(self, modelname, count=25):
        modelname = modelname.strip().lower()
        self.tmp_fakes = [] if self.style == "default" else {}
        if modelname == "products" or modelname == "users":
            for i in range(count):
                resp = fake_product() if modelname == "products" else fake_user()
                if self.style == "firebase":
                    key = resp["id"]
                    if "id" in resp: resp.pop("id")
                    self.tmp_fakes[key] = resp
                else:
                    self.tmp_fakes.append(resp)
        else:
            raise ValueError("modelname did not match either 'products' or 'users'")

        return self

    def create_products(self, count=25):
        if count < 0:
            raise ValueError("count cannot be less than 0")

        self.create("products", count)
        return self

    def create_users(self, count=25):
        if count < 0:
            raise ValueError("count cannot be less than 0")

        self.create("users", count)
        return self

    def download(self, filename):
        if filename is None:
            raise ValueError("filename cannot be null.")

        with open(os.path.join(filename), 'wb+') as outfile:
            json.dump(self.tmp_fakes, outfile, indent=4, sort_keys=True)
            self.tmp_fakes = [] if self.style == "default" else {}

def main():

    p = optparse.OptionParser()
    p.add_option('--products', '-p', type="str", help="writes fake products to path.")
    p.add_option('--users', '-u', type="str", help="writes fake users to path.")
    p.add_option('--style', '-s', type="str", default="default", help="style of written products. can either be the default or firebase.")
    p.add_option('--count', '-c', type="int", default=25, help="number of items created.")
    options, arguments = p.parse_args()

    td = TestData()

    if options.products:
        print "Writing fake products..."
        if options.count >= 25:
            print "This may take a while so grab a cup of coffee while you're at it."
        else:
            print "This will only take a minute."

        td.set_style(options.style)
        td.create_products(count=options.count).download(options.products)

        print "Task complete. You're testdata is ready at '{path}'".format(path = options.products)

    elif options.users:
        print "Writing fake users..."
        if options.count >= 25:
            print "This may take a while so grab a cup of coffee while you're at it."
        else:
            print "This will only take a minute."

        td.set_style(options.style)
        td.create_users(count=options.count).download(options.users)

        print "Task complete. You're testdata is ready at '{path}'".format(path = options.users)

if __name__ == "__main__":
    main()
