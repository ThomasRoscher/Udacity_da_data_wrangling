###############################################################################
# WRANGLE OPEN STREET MAP DATA FOR FRIEDRICHSHAIN-KREUZBERG ###################
# TESTED ONLY ON PYTHON 3
###############################################################################
# http://www.openstreetmap.org/relation/55764#map=13/52.5070/13.4298&layers=HN
# 
#THIS SCRIPT AUDITS OPEN STREET MAP DATA FOR FRIEDRICHSHAIN-KREUZBERG. AUDITING
#IS RESTRICTED TO ADDRESS RELATED INFORMATION SUCH AS COUNTRY, CITY AND NAME OF
#STREET AND CONTACT RELATED INFORMATION SUCH AS PHONE AND WEB PAGE.
#
###############################################################################

import xml.etree.cElementTree as ET
import re
from collections import Counter

###############################################################################
####### EXPLORE TAGS ##########################################################
###############################################################################

## - GET NUMBER OF UNIQUE TOP LEVEL TAGS 
## - GET NUMBER OF UNIQUE ATTRIBUTES
## - GET VALUES OF ATTRIBUTES RELATED TO ADDRESS AS WELL AS CONTACT
## - GENERALLY JUST GET A FEELING FOR THE DATA

###############################################################################
# CREATE FUNCTION TO COUNT UNIQUE TOP LEVEL TAGS
def count_unique_tags(filename):
    tags = []
    for event, element in ET.iterparse(filename):
        tags.append(element.tag)
    k = Counter(tags).keys()
    v = Counter(tags).values()
    dic = dict(zip(k, v))
    dic = sorted(dic.items(), key = lambda x:x[1], reverse = True)
    return dic

tags_unique = count_unique_tags("fk.osm")

###############################################################################
# CREATE FUNCTION TO COUNT UNIQUE VALUES OF K
def count_unique_keys(filename):
    attrib_k = []
    for event, element in ET.iterparse(filename):      
        if element.tag == "tag":
            for tag in element.iter("tag"):
                attrib_k.append(tag.attrib["k"])
    k = Counter(attrib_k).keys()
    v = Counter(attrib_k).values()
    dic = dict(zip(k, v))
    dic = sorted(dic.items(), key = lambda x:x[1], reverse = True)
    return dic

keys_unique = count_unique_keys("fk.osm")
print(len(keys_unique))
keys_unique[:10]

###############################################################################
# CREATE FUNCTION TO COUNT UNIQUE VALUES OF V FOR K
def count_unique_key_values(filename, kvalue, topx):
    attrib_v = []
    for event, element in ET.iterparse(filename):
        if element.tag == "tag":
            for tag in element.iter("tag"):
                if element.attrib['k'] == kvalue:
                    attrib_v.append(element.attrib["v"])
    k = Counter(attrib_v).keys()
    v = Counter(attrib_v).values()
    dic = dict(zip(k, v))
    dic = sorted(dic.items(), key = lambda x:x[1], reverse = True)
    dic = dic[:topx]
    return dic

###############################################################################

# get top 20 values for keys related to address 
val_country   = count_unique_key_values("fk.osm", "addr:country", 20)
val_city      = count_unique_key_values("fk.osm", "addr:city", 20)
val_suburb    = count_unique_key_values("fk.osm", "addr:suburb", 20)
val_postcode  = count_unique_key_values("fk.osm", "addr:postcode", 20)
val_name      = count_unique_key_values("fk.osm", "addr:street", 20)
val_phone     = count_unique_key_values("fk.osm", "contact:phone", 20)
val_email     = count_unique_key_values("fk.osm", "contact:email", 20)

###############################################################################
# MOST RELEVANT FINDINGS
# PHONE SEEMS TO BE A MESS
# DATA IS NOT RESTRICTED TO FRIEDRICHSHAIN-KREUZBERG
# MOST TAGS ARE CODED SURPRISINGLY UNIFORM

###############################################################################
######### AUDIT TAGS ##########################################################
###############################################################################

# - BASED ON GENERAL KNOWLEDGE AND FINDINGS OF PREVIOUS PART SET RULES FOR 
#   VALID VALUES 
# - FILTER VALUES BASED ON THOSE RULES
# - DETECT RECURANT AND SYSTEMATICFLAWS IN THE REMAINING DATA TO GET AN IDEA 
#   WHICH CORRESPONDING CLEANING FUNCTIONS MUST BE WRITTEN LATER ON

###############################################################################
# SET EXPECTED VALUES/RULEZ FOR TAGS I WANT TO AUDIT
expected_country    = ["DE"]
expected_city       = ["Berlin"]
expected_suburb     = ["Friedrichshain", "Kreuzberg"]
expected_postcode   = [10243, 10245, 10247, 10249, 10785, 10961, 10963, 10965, 
                       10967, 10969, 10997, 10999]
expected_streetname = ["Weg", "Allee", "Straße", "Platz", "Ufer", "Park", 
                       "Tor", "Brücke", "Damm", "straße", "damm", "weg", 
                       "brücke", "platz", "allee", "gasse", "ufer"]
expected_email      = [".com", ".org", ".de", "net"]
expected_phone      = ["+49 30", "+49 1"]

###############################################################################
# FUNCTION THAT FILTERS VALUES ACCORDING TO THE PATTERN: TAG V IS NOT ELEMENT 
# OF EXPECTED VALUE(S)

def audit_value_isnot_x(filename, vvalue, expected, spec):
    attrib_v = []
    for event, element in ET.iterparse(filename):
        if element.tag == "tag":
            for tag in element.iter("tag"):
                if element.attrib['k'] == vvalue and element.attrib["v"] not in expected:
                    attrib_v.append(element.attrib["v"])
    k = Counter(attrib_v).keys()
    v = Counter(attrib_v).values()
    dic = dict(zip(k, v))
    dic = sorted(dic.items(), key = lambda x:x[1], reverse = True)
    return dic

audit_country   = audit_value_isnot_x("fk.osm", "addr:country", expected_country)
audit_city      = audit_value_isnot_x("fk.osm", "addr:city", expected_city)
audit_suburb    = audit_value_isnot_x("fk.osm", "addr:suburb", expected_suburb)
audit_postcode  = audit_value_isnot_x("fk.osm", "addr:postcode", expected_postcode)

audit_postcode2 = [x[0] for x in audit_postcode]
[elem for elem in audit_postcode2 if len(elem) != 5] 

###############################################################################
# FUNCTION THAT FILTERS VALUES ACCORDING TO THE PATTERN: TAG V DOES NOT END 
# WITH EXPECTED VALUE
def audit_value_ends_with_x(filename, vvalue, expected):
    attrib_v = []
    for event, element in ET.iterparse(filename):
        if element.tag == "tag":
            for tag in element.iter("tag"):
                if element.attrib['k'] == vvalue and not element.attrib["v"].endswith(tuple(expected)):
                    attrib_v.append(element.attrib["v"])
    k = Counter(attrib_v).keys()
    v = Counter(attrib_v).values()
    dic = dict(zip(k, v))
    dic = sorted(dic.items(), key = lambda x:x[1], reverse = True)
    return dic

audit_streetname  = audit_value_ends_with_x("fk.osm", "addr:street", expected_streetname)
audit_email       = audit_value_ends_with_x("fk.osm", "contact:email", expected_email)

# further investiagtionss just some examples
audit_streetname2 = [x[0] for x in audit_streetname]
[a for a in audit_streetname2 if a.endswith(".")]
[a for a in audit_streetname2 if a[1].isdigit()]
[a for a in audit_streetname2 if not a[0].isupper()]
[a for a in audit_streetname2 if re.match(r'.*[\%\$\^\*\@\!\_\-\(\)\:\;\'\"\{\}\[\]].*', a)]

###############################################################################
# FUNCTION THAT FILTERS VALUES ACCORDING TO THE PATTERN: TAG V DOES NOT START 
# WITH EXPECTED VALUE
def audit_value_starts_with_x(filename, vvalue, expected):
    attrib_v = []
    for event, element in ET.iterparse(filename):
        if element.tag == "tag":
            for tag in element.iter("tag"):
                if element.attrib['k'] == vvalue and not element.attrib["v"].startswith(tuple(expected)):
                    attrib_v.append(element.attrib["v"])
    k = Counter(attrib_v).keys()
    v = Counter(attrib_v).values()
    dic = dict(zip(k, v))
    dic = sorted(dic.items(), key = lambda x:x[1], reverse = True)
    return dic

audit_phone = audit_value_starts_with_x("fk.osm", "contact:phone", expected_phone)

###############################################################################
# MOST RELEVANT FINDINGS
# CONFIRMED: MAP DATA SPANS TO MUCH AREA
# ADRESS RELATED TAGS ARE SURPRISINGLY WELL CODED -> NO SYSTEMATIC DIFFERENCES
# SUCH AS ABBRIVATIONS IN STREET NAMES
# SAME HOLDS FOR ZIPS -> SAME LENGTH NO SPECIAL CHARACTERS
# COUNTRY IS ONLY IN A SINGLE CASE NOT "DE"
# ALL WEBSITES END WITH A PROPER ."valid something"
# PHONE NUMBER REQUIRES QUIET SOME CHANGES

###############################################################################
########## WORKFLOW ###########################################################
###############################################################################

## - GENERATE A MAPPING DICTIONARY FOR FALSE ENTRIES AND CORRECTIONS
## - GONNA ADD SOME FAKE ERRORS TO BETTER ILLUSTRATE HOW IT WORKS
## - WRITE UPDATE FUNCTIONS THAT APPLY THOSE CORRECTIONS 
## - WRITE UPDATE FUNCTION WHICH RULES ARE NOT SET IN A MAPPING DICTIONARY
## - INCORPORATE UPDATE FUNCTIONS IN AUDIT FUNCTIONS TO TEST THEM
## - XML FILE IS NOT UPDATED! INSTEAD DATA IS CORRECTED WHEN CSVs ARE GENERATED
## - NOTE, I'AM NOT FAMILIAR ENOGH WITH XML TO DELETE EVERTHING THAT IS THE 

###############################################################################
# MAPPING DIRECTORIES (NOT REQUIRED FOR ALL VALUES)

mapping_country = {"GE"  : "DE",
                   "GER" : "DE",
                   "D"   : "DE"
                   }

mapping_city = {"BERLIN"        : "Berlin",
                "Bln."          : "Berlin",
                "Lichtenberg"   : "Berlin"
                }

###############################################################################
# UPDATE FUNCTIONS

def update_country(country):
    if country in mapping_country:
            country = country.replace(country, mapping_country[country])
    return country
update_country("GE")

def update_city(city):
    if city in mapping_city:
            city = city.replace(city, mapping_city[city])
    return city
update_city("Bln.")

def update_streetname(streetname):
    streetname = streetname[0].upper() + streetname[1:]
    streetname = streetname.replace("street", "Straße")
    streetname = streetname.replace("strasse", "straße")
    streetname = streetname.replace("Strasse", "Straße")
    if len(streetname.split()) > 2 and streetname[-1].isdigit():
        streetname = streetname.rsplit(' ', 1)[0]
    else:
        streetname = streetname
    return streetname
update_streetname("samariterstrasse 48")
update_streetname("Straße 122")

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

# valid patterns
# +4930... Ortsnetzrufnummer (Landline)
# +4915... Mobilfunknummer (Mobile)
# +4916... Mobilfunknummer (Mobile)
# +4917... Mobilfunknummer (Mobile)
# +4918... Mobilfunknummer (Mobile)

# test function
# enterred without any valid prefix 
update_phone("123456")          # correct
update_phone("0172 123456")     # correct 
# entered ony Berlin prefix
update_phone("030 123456")      # correct
# entered only German prefix  
update_phone("+49 123456")      # correct
# entered both prefixes with 0
update_phone("+49030 123456")   # correct
# entered both prefixes with 0
update_phone("+490172 123456")  # correct
# correct entries
update_phone("+49172 123456")   # correct
update_phone("+4930 123456")    # correct

###############################################################################
# AUDIT FUNCTIONS WITH UPDATE FUNCTIONS INCORPORATED
  
def audit_update_country(filename):
    up_country = []
    for event, element in ET.iterparse(filename):
        if element.tag == "tag":
            for tag in element.iter("tag"):
                if element.attrib['k'] == "addr:country":
                    changed_country = update_country(tag.attrib['v'])
                    up_country.append(changed_country)                    
    return up_country

audit_country_corrected = audit_update_country("fk.osm")

def audit_update_city(filename):
    up_city = []
    for event, element in ET.iterparse(filename):
        if element.tag == "tag":
            for tag in element.iter("tag"):
                if element.attrib['k'] == "addr:city":
                    changed_city = update_city(tag.attrib['v'])
                    up_city.append(changed_city)                    
    return up_city

audit_city_corrected = audit_update_city("fk.osm")

def audit_update_streetname(filename):
    up_streetname = []
    for event, element in ET.iterparse(filename):
        if element.tag == "tag":
            for tag in element.iter("tag"):
                if element.attrib['k'] == "addr:street":
                    changed_streetname = update_streetname(tag.attrib['v'])
                    up_streetname.append(changed_streetname)                    
    return up_streetname

audit_streetname_corrected = audit_update_streetname("fk.osm")

def audit_update_phone(filename):
    up_phone = []
    for event, element in ET.iterparse(filename):
        if element.tag == "tag":
            for tag in element.iter("tag"):
                if element.attrib['k'] == "contact:phone":
                    changed_phone = update_phone(tag.attrib['v'])
                    up_phone.append(changed_phone)                    
    return up_phone

audit_phone_corrected = audit_update_phone("fk.osm")

###############################################################################
# SUMMARY INVESTIGATING AND AUDITING THE DATA IS DONE. BASED ONE FINDINGS FOUR
# UPDATING FUNCTION WERE WRITTEN. THEY WILL BE IMPLEMENTED WHEN XML IS CHANGED
# TO CSV
###############################################################################
