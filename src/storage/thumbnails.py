#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import json
from PIL import Image

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

accepted_img_types = ["jpeg", "jpg"]

class Thumbnails:
    def __init__(self, rules_path):
        self.rules = {}

        try:
            f = open(os.path.join(__location__, rules_path), 'rb+')
        except IOError:
            print "Please provide a path to your compression rules"

        else:
            self.rules = json.load(f)

    def generate(self, filepath, download_path="/tmp/thumbnails"):
        complete_download_paths = {}

        accepted_type = False
        for img_type in accepted_img_types:
            if filepath.endswith("." + img_type) is True:
                accepted_type = True
                break

        if accepted_type is False:
            raise ValueError("[dev only usage] Only image types are supported at this point in time.")

        if self.rules is None:
            raise ValueError("Please provide a path to your compression rules")

        self.download_path = download_path

        if self.download_path is None:
            raise ValueError("Please provide a download path")

        # create folder directory if it doesn't exist yet.
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)

        # create thumbnails
        for key, value in self.rules.items():
            filename = value["filename"]
            quality = value["quality"]

            size_enabled = False
            if  "width" in value.keys() and "height" in value.keys():
                size_enabled = True
                size = value["width"], value["height"]

            try:
                img = Image.open(open(filepath, 'rb+'))
                if size_enabled:
                    img.thumbnail(size)
                img.save(self.download_path + "/" + filename, "JPEG", quality=quality)

                complete_download_paths[filename] = self.download_path + "/" + filename

            except IOError:
                print "cannot create thumbnail of type " + key

        return complete_download_paths
