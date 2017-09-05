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
import csv
from collections import Counter

###############################################################################
####### 1. EXPLORE TAGS #######################################################
###############################################################################

## - GET NUMBER OF UNIQUE TOP LEVEL TAGS 
## - GET NUMBER OF UNIQUE ATTRIBUTES
## - GET VALUES OF ATTRIBUTES RELATED TO ADDRESS AS WELL AS CONTACT
## - GENERALLY JUST GET A FEELING FOR THE DATA

###############################################################################
def count_unique_tags(filename, outputname):
    """Get prevelance of all unique top level tags of an XML file. For example
    "nodes"

        Input: XML file 
        
        Args:
            filename: Filename of imput XML file
            outputname: Filename of output csv file

        Output:
            csv file with two variables: name of top level node and number
            of occurances (ordered)
        """
    tags = []
    for event, element in ET.iterparse(filename):
        tags.append(element.tag)
    k = Counter(tags).keys()
    v = Counter(tags).values()
    dic = dict(zip(k, v))
    dic = sorted(dic.items(), key = lambda x:x[1], reverse = True)
    with open(outputname, "w", newline="", encoding = "utf-8") as out:
        csv_out = csv.writer(out)
        csv_out.writerow(["tags", "num"])
        for row in dic:
            csv_out.writerow(row)
       
###############################################################################
def count_unique_keys(filename, outputname):
    """Get prevelance of all unique attributes for the top level tag "tag". For 
    example, "addr:street"

        Input: XML file 
        
        Args:
            filename: Filename of imput XML file
            outputname: Filename of output csv file

        Output:
            csv file with two variables: name of attribute and number
            of occurances
        """
    attrib_k = []
    for event, element in ET.iterparse(filename):      
       if element.tag == "tag":
            for tag in element.iter("tag"):
                attrib_k.append(tag.attrib["k"])
    k = Counter(attrib_k).keys()
    v = Counter(attrib_k).values()
    dic = dict(zip(k, v))
    dic = sorted(dic.items(), key = lambda x:x[1], reverse = True)
    with open(outputname, "w", newline="", encoding = "utf-8") as out:
        csv_out = csv.writer(out)
        csv_out.writerow(["attrib", "num"])
        for row in dic:
            csv_out.writerow(row)

###############################################################################
def count_unique_key_values(filename, outputname, kvalue, topx):
    """Get prevelance of all values for the attribute x of the tag "tag". For
    example, "Köpenicker Straße" for "addr:street"
    
        Input: XML file 
        
        Args:
            filename: Filename of imput XML file
            outputname: Filename of output csv file
            kvalue: the name of the attribute
            topx: the number of top n values 

        Output:
            csv file with two variables: name of attribute value and number
            of occurances
    """
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
    with open(outputname, "w", newline="", encoding = "utf-8") as out:
       csv_out = csv.writer(out)
       csv_out.writerow(["attrib_value", "num"])
       for row in dic:
           csv_out.writerow(row)
    
###############################################################################
######### 2. AUDIT TAGS #######################################################
###############################################################################

# - BASED ON GENERAL KNOWLEDGE AND FINDINGS OF PREVIOUS PART SET RULES FOR 
#   VALID VALUES 
# - FILTER VALUES BASED ON THOSE RULES
# - DETECT RECURANT AND SYSTEMATICFLAWS IN THE REMAINING DATA TO GET AN IDEA 
#   WHICH CORRESPONDING CLEANING FUNCTIONS MUST BE WRITTEN LATER ON

###############################################################################
def audit_value_isnot_x(filename, outputname, kvalue, expected):
    """Get prevelance of some values for the attribute x of the tag "tag". 
    Attribute values must match to past the test

        Input: XML file 
        
        Args:
            filename: Filename of imput XML file
            outputname: Filename of output csv file
            vvalue: the name of the attribute
            expected: a list of accapted values 

        Output:
            csv file with two variables: name of attribute value and number
            of occurances
    """
    attrib_v = []
    for event, element in ET.iterparse(filename):
        if element.tag == "tag":
            for tag in element.iter("tag"):
                if element.attrib['k'] == kvalue and element.attrib["v"] not in expected:
                    attrib_v.append(element.attrib["v"])
    k = Counter(attrib_v).keys()
    v = Counter(attrib_v).values()
    dic = dict(zip(k, v))
    dic = sorted(dic.items(), key = lambda x:x[1], reverse = True)
    with open(outputname, "w", newline="", encoding = "utf-8") as out:
       csv_out = csv.writer(out)
       csv_out.writerow(["attrib_value", "num"])
       for row in dic:
           csv_out.writerow(row)

###############################################################################
def audit_value_ends_with_x(filename, outputname, kvalue, expected):
    """Get prevelance of some values for the attribute x of the tag "tag". 
    Ending of attribute values must match to past the test

        Input: XML file 
        
        Args:
            filename: Filename of imput XML file
            outputname: Filename of output csv file
            vvalue: the name of the attribute
            expected: a list of accapted values 

        Output:
            csv file with two variables: name of attribute value and number
            of occurances
    """    
    attrib_v = []
    for event, element in ET.iterparse(filename):
        if element.tag == "tag":
            for tag in element.iter("tag"):
                if element.attrib['k'] == kvalue and not element.attrib["v"].endswith(tuple(expected)):
                    attrib_v.append(element.attrib["v"])
    k = Counter(attrib_v).keys()
    v = Counter(attrib_v).values()
    dic = dict(zip(k, v))
    dic = sorted(dic.items(), key = lambda x:x[1], reverse = True)
    with open(outputname, "w", newline="", encoding = "utf-8") as out:
       csv_out = csv.writer(out)
       csv_out.writerow(["attrib_value", "num"])
       for row in dic:
           csv_out.writerow(row)
###############################################################################
def audit_value_starts_with_x(filename, outputname, kvalue, expected):
    """Get prevelance of some values for the attribute x of the tag "tag". 
    Starting of attribute values must match to past the test

        Input: XML file 
        
        Args:
            filename: Filename of imput XML file
            outputname: Filename of output csv file
            vvalue: the name of the attribute
            expected: a list of accapted values 

        Output:
            csv file with two variables: name of attribute value and number
            of occurances
    """    
    attrib_v = []
    for event, element in ET.iterparse(filename):
        if element.tag == "tag":
            for tag in element.iter("tag"):
                if element.attrib['k'] == kvalue and not element.attrib["v"].startswith(tuple(expected)):
                    attrib_v.append(element.attrib["v"])
    k = Counter(attrib_v).keys()
    v = Counter(attrib_v).values()
    dic = dict(zip(k, v))
    dic = sorted(dic.items(), key = lambda x:x[1], reverse = True)
    with open(outputname, "w", newline="", encoding = "utf-8") as out:
       csv_out = csv.writer(out)
       csv_out.writerow(["attrib_value", "num"])
       for row in dic:
           csv_out.writerow(row)
###############################################################################
########## 3. WORKFLOW ########################################################
###############################################################################

## - WRITE UPDATE FUNCTIONS THAT APPLY CORRECTIONS 
## - INCORPORATE UPDATE FUNCTIONS IN AUDIT FUNCTIONS TO TEST THEM
## - XML FILE IS NOT UPDATED! INSTEAD DATA IS CORRECTED WHEN CSVs ARE GENERATED

###############################################################################
def update_country(country):
    """Changes a string to DE if it matches any of "mapping_country"

       Input: a single string
        
       Output: a single string 
    """      
    mapping_country = {"GE"  : "DE",
                       "GER" : "DE",
                       "D"   : "DE"
                   }
    if country in mapping_country:
            country = country.replace(country, mapping_country[country])
    return country

###############################################################################
def update_city(city):
    """Changes a string to Berlin if it matches any of "mapping_city"

       Input: a single string
        
       Output: a single string 
    """ 
    mapping_city = {"BERLIN"        : "Berlin",
                    "Bln."          : "Berlin",
                    "Lichtenberg"   : "Berlin"
                }
    if city in mapping_city:
            city = city.replace(city, mapping_city[city])
    return city

###############################################################################
def update_streetname(streetname):
    """Changes a string that is supposed to contain a German streetname in the 
    following regards: capitalizes first letters, replaces some common errors 
    with adequate string (e.g. ss instead of ß, street instead of Straße) 
    and removes house number.

       Input: a single string
        
       Output: a single string 
    """ 
    streetname = streetname.title()
    streetname = streetname.replace("Street", "Straße")
    streetname = streetname.replace("strasse", "straße")
    streetname = streetname.replace("Strasse", "Straße")
    if streetname[-1].isdigit():
        streetname = streetname.rsplit(' ', 1)[0]
    else:
        streetname = streetname
    return streetname

###############################################################################
def update_phone(phone):
    """Changes a string that is supposed to contain a German phonenumber to a
    valid format with international and local prefix. Note that complete rubbish
    numbers will remain such. Therefore checking length of numbers as well as 
    occurance of letters is still required. Put differently, the function rather
    unifies the format and adjusts/adds international and local prefixes if 
    required:

       Input: a single string
        
       Output: a single string 
    """     
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

update_phone("56701748")
update_phone("030 56701748")
update_phone("0174477845")
update_phone("+49 0174477845")

###############################################################################
def audit_update_streetname(filename, outputname):
    """Get all values for the attribute addr:street of the tag "tag" and apply 
    cleaning function "update_streetname" to extracted values. 
        
    Input: XML file 
        
        Args:
            filename: Filename of imput XML file
            outputname: Filename of output csv file
            
        Output:
            csv file with each value of the attribute "addr:street"
    """    
    up_streetname = []
    for event, element in ET.iterparse(filename):
        if element.tag == "tag":
            for tag in element.iter("tag"):
                if element.attrib['k'] == "addr:street":
                    changed_streetname = update_streetname(tag.attrib['v'])
                    up_streetname.append(changed_streetname)
    k = Counter(up_streetname).keys()
    v = Counter(up_streetname).values()
    dic = dict(zip(k, v))
    dic = sorted(dic.items(), key = lambda x:x[1], reverse = True)
    with open(outputname, "w", newline="", encoding = "utf-8") as out:
      csv_out = csv.writer(out)
      csv_out.writerow(["attrib_value", "num"])
      for row in dic:
          csv_out.writerow(row)
###############################################################################
def main():
    
    count_unique_tags("fk.osm", "unique_tags.csv")
    count_unique_keys("fk.osm", "unique_keys.csv")

    count_unique_key_values("fk.osm", "country_values.csv","addr:country", 100)
    count_unique_key_values("fk.osm", "city_values.csv","addr:city", 100)
    count_unique_key_values("fk.osm", "suburb_values.csv","addr:suburb", 100)
    count_unique_key_values("fk.osm", "postcode_values.csv","addr:postcode", 100)
    count_unique_key_values("fk.osm", "streetname_values.csv","addr:street", 100,)
    count_unique_key_values("fk.osm", "phone_values.csv","contact:phone", 100)
    count_unique_key_values("fk.osm", "email_values.csv","contact:email", 100)

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

    audit_value_isnot_x("fk.osm", "country_audit.csv", "addr:country", expected_country)
    audit_value_isnot_x("fk.osm", "city_audit.csv", "addr:city", expected_city)
    audit_value_isnot_x("fk.osm", "suburb_audit.csv", "addr:suburb", expected_suburb)
    audit_value_isnot_x("fk.osm", "postcode_audit.csv", "addr:postcode", expected_postcode)
    audit_value_ends_with_x("fk.osm", "streetname_audit.csv", "addr:street", expected_streetname)
    audit_value_ends_with_x("fk.osm", "phone_audit.csv", "contact:email", expected_email)
    audit_value_starts_with_x("fk.osm", "email_audit.csv", "contact:phone", expected_phone)

    audit_update_streetname("fk.osm", "streetname_audit_cleaned.csv")
   
    if __name__ == '__main__':
        main()