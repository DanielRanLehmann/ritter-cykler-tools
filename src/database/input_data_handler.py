#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os
from time import time
import re

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

# TOO CLEVER.
def filter_props(props, filters):
    if type(props) is not dict:
        print ValueError("props type is not of type dict.")

    f_props = {}
    for key, value in props.iteritems():
        match = True
        for (m_key, m_value) in filters:
            m_value = m_value.replace(m_key, "value[m_key]")
            if m_key in value.keys() and eval(m_value) is not True:
                match = False
                break

        if match:
            f_props[key] = value

    return f_props

def cast(val, _type):
    _type = _type.lower()

    if _type == "str":
        val = str(val)

    elif _type == "float":
        val = float(val)

    elif _type == "int":
        val = int(val)

    elif _type == "y/n": # DEPRECATED
        val = True if val.lower() == "y" else False

    # COMMA DELIMITED
    # OR ';'?
    elif _type.startswith("list"):
        val = [x.strip() for x in val.split(',')]
    else:
        raise ValueError('cannot cast to type: {0}'.format(_type))

    return val

def handle_input_props(props, level=-1): # carry over data.
    level += 1
    if level > 1:
        raise ValueError("Nested props exceeded max level of 1. Consider making your model more flat to accomodate for firebase db best terms of use.")

    data = {}
    for name in props.keys():
        prop_type = props[name]["type"]

        should_eval = props[name]["shouldEval"]
        value = props[name]["value"]
        default_value = props[name]["defaultValue"] # not being used right now

        prefixers = {
            0: "\t •",
            1: "\t\t ◦"
        }
        prompt = "{prefixers} {name} [{type}]: ".format(prefixers=prefixers[level], name=name, type=prop_type)

        if prop_type == "dict":
            prop_value = ""
            print prompt
            data[name] = handle_input_props(props[name]["props"], level) # calls this function recursively
        else:
            prop_value = raw_input(prompt)
            if prop_value != '':

                prop_value = cast(prop_value, prop_type)
                data[name] = prop_value

    return data

def handle_input_data(db_location):
    model = None
    data = None
    with open(os.path.join(__location__, 'models.json'), 'rb+') as f:
        models = json.load(f)
        if db_location not in models.keys():
            raise ValueError('Did not find model assosiated with db_location of ' + db_location)
        else:
            model = models[db_location]
            prop_type = model["type"]
            if prop_type != "dict" and "props" not in model.keys():
                raise ValueError("Prop type is not a dict or props was not found.")
            else:

                f_props = filter_props(model["props"], [("shouldEval", "shouldEval is False"), ("value", "value is None")])
                data = handle_input_props(f_props)

                value_props = filter_props(model["props"], [("shouldEval", "shouldEval is False"), ("value", "value is not None")])
                for key, value in value_props.iteritems():
                    data[key] = value["value"]

                autofill_props = filter_props(model["props"], [("shouldEval", "shouldEval is True")])
                for key, value in autofill_props.iteritems():
                    should_eval = value["shouldEval"]
                    _value = value["value"]
                    data[key] = eval(_value) if should_eval is True else _value

    return data
