# -*- coding: utf-8 -*-

###############################################################################
# WRANGLE OPEN STREET MAP DATA FOR FRIEDRICHSHAIN-KREUZBERG ###################
###############################################################################
# http://www.openstreetmap.org/relation/55764#map=13/52.5070/13.4298&layers=HN
#
# BASED ON THE AUDITING IN THE "audit.py" FILE THIS SCRIPT CLEANS AND CONVERTS
# THE OPEN STREET MAP XML DATA TO THE CSV FORMAT. NOTE, MUCH OF THE SCRIPT IS
# PROVIDED BY UDACITY. PERSONAL CONTRIBUTION IS FOCUSED ON THE UPDATE FUNCTIONS
# DEVELOPED IN THE audit.py" AND WRITING THE "shape_element" FUNCTION.
#
# More precicely, the process for this transformation is as follows:
# - use iterparse to iteratively step through each top level element in the XML
# - shape each element into several data structures using a custom function
# - utilize a schema and validation library to ensure the transformed data is
#   in the correct format
# - write each data structure to the appropriate .csv files
###############################################################################
# IMPORT LIBRARIES

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import schema

###############################################################################
# DEFINE UPDATE FUNCTIONS FOR addr:country, addr:city, and contact:phone 

mapping_country = {"GE"  : "DE",
                   "GER" : "DE",
                   "D"   : "DE"
                   }

mapping_city = {"BERLIN"        : "Berlin",
                "Bln."          : "Berlin",
                "Lichtenberg"   : "Berlin"
                }

def update_country(country):
    if country in mapping_country:
            country = country.replace(country, mapping_country[country])
    return country

def update_city(city):
    if city in mapping_city:
            city = city.replace(city, mapping_city[city])
    return city

# I WAS FORCED TO DROP THE STREETNAME FUNCTION BECAUSE UFT8 ENCODING IN PYTHON 2
# APPARENTLY IS JUST A DICK. TRIED SEVERAL THINKS BUT NOTHING WORKED. ODDLY ENOGH
# IT DID WORK WHEN RUNNING IT ON PYTHON 3 
# 
# def update_streetname(streetname):
#    streetname = streetname[0].upper() + streetname[1:]
#    streetname = streetname.replace("street", "Straße")
#    streetname = streetname.replace("strasse", "straße")
#   streetname = streetname.replace("Strasse", "Straße")
#    if len(streetname.split()) > 2 and streetname[-1].isdigit():
#        streetname = streetname.rsplit(' ', 1)[0]
#    else:
#        streetname = streetname
#    return streetname
# update_streetname("samariterstrasse 48")
# update_streetname("Straße 122")

def update_phone(phone):
    prefixes = ["1", "2","3","4","5","6","7","8","9"]
    phone = ''.join(e for e in phone if e.isalnum())
    if not phone.startswith("49") and phone.startswith("01"):
        phone = phone.replace(phone[0], '')
        phone = ''.join(("49", phone))
    if not phone.startswith("49") and phone.startswith(tuple(prefixes)):
        phone = ''.join(("4903", phone))
    if phone.startswith("030"):
        phone = phone.replace(phone[:3], "4930")
    if phone.startswith("49030"):
        phone = phone.replace(phone[:5], "4930")
    if phone.startswith("4901"):
        phone = phone.replace(phone[:4], "491")
    phone = "+" + phone
    return phone

###############################################################################
# SET UP CSV BASE SETTINGS

# define csv file names
OSM_PATH = "fk.osm"
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

# tag value pattern with : such as "addr:street"
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
# tag value pattern with any of several special characters
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# define schema as schema.py 
SCHEMA = schema.schema

# restrict tags 
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

###############################################################################
# DEFINE SHAPE ELEMENT FUNCTION

# parse the information from each parent ement and it's 
# childeren into dictionaries. "element" refers to a single top level node
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    
    # initialite empty dictionaries and lissts
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  

    # if top level tag is "node"
    if element.tag == 'node':
        # check if top level node attributes belong to NODE_FIELDS
        for node in NODE_FIELDS:
            # and collect them to  node_attribs dictionary
            node_attribs[node] = element.attrib[node]

        # initialize empty dictionary for tags
        node_tags_dict = {}

        # collect attributes of childs 
        for child in element:
            # if attribute has pattern something:something 
            if LOWER_COLON.match(child.attrib["k"]):
                # store first part as type in node_tags_dict
                node_tags_dict['type'] =  child.attrib["k"].split(":",2)[0]
                # store second part as key in node_tags_dict
                node_tags_dict['key']  =  child.attrib["k"].split(":",1)[1]
                # store id as id in node_tags_dict
                node_tags_dict['id']   =  element.attrib['id']
                #if child.attrib["k"] == "addr:street":
                #    node_tags_dict["value"] = update_streetname(child.attrib["v"])
                # apply cleaning functions if child.attrib["k"] matches
                if child.attrib["k"] == "addr:country":
                    node_tags_dict["value"] = update_country(child.attrib["v"])
                elif child.attrib["k"] == "addr:city":
                    node_tags_dict["value"] = update_city(child.attrib["v"])
                elif child.attrib["k"] == "contact:phone":
                    node_tags_dict["value"] = update_phone(child.attrib["v"])
                else:
                    node_tags_dict["value"] = child.attrib["v"]
                # otherwise just use regular value and append to tag list 
                tags.append(node_tags_dict)
            # if attribute has any of several special characters ignore entry
            elif PROBLEMCHARS.match(child.attrib["k"]):
                continue
            # for "regular"  attributes
            else:
                # type is always "regular"
                node_tags_dict['type']  = "regular"
                # store key as key in node_tags_dict
                node_tags_dict['key']   = child.attrib["k"]
                # store id as id in node_tags_dict                                
                node_tags_dict['id']    = element.attrib['id']
                # If there would be any cleaning functions that refer to 
                # regular child.attrib["k"] they need to replace the line
                # below
                # store value as value in node_tags_dict               
                node_tags_dict["value"] = child.attrib['v']
                tags.append(node_tags_dict)
        return {'node': node_attribs, 'node_tags': tags}

    # procedure is basically the same as above except the distinction between
    # child tag "tag" and "nd"
    elif element.tag == 'way':
        for field in WAY_FIELDS:
            way_attribs[field] = element.attrib[field]

        position = 0
        way_tags_dict = {}
        way_nodes_dict = {}

        for child in element:
            if child.tag == 'tag':
                if LOWER_COLON.match(child.attrib["k"]):
                    way_tags_dict['type'] =  child.attrib["k"].split(":",2)[0]
                    way_tags_dict['key']  = child.attrib["k"].split(":",1)[1]
                    way_tags_dict['id']   = element.attrib['id']
                    #if child.attrib["k"] == "addr:street":
                    #    way_tags_dict["value"] = update_streetname(child.attrib["v"])
                    if child.attrib["k"] == "addr:country":
                        way_tags_dict["value"] = update_country(child.attrib["v"])
                    elif child.attrib["k"] == "addr:city":
                        way_tags_dict["value"] = update_city(child.attrib["v"])
                    elif child.attrib["k"] == "contact:phone":
                        way_tags_dict["value"] = update_phone(child.attrib["v"])
                    else:
                        way_tags_dict["value"] = child.attrib["v"]
                        tags.append(way_tags_dict)
                elif PROBLEMCHARS.match(child.attrib["k"]):
                    continue
                else:
                    way_tags_dict['type']  = "regular"
                    way_tags_dict['key']   = child.attrib["k"]
                    way_tags_dict['id']    = element.attrib['id']
                    way_tags_dict["value"] = child.attrib['v']
                    tags.append(way_tags_dict)
            elif child.tag == "nd":
                way_nodes_dict['id'] = element.attrib['id']
                way_nodes_dict['node_id'] = child.attrib['ref']
                way_nodes_dict['position'] = position
                position += 1
                way_nodes.append(way_nodes_dict)
        #print({'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags})
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate = False)