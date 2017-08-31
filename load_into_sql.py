###############################################################################
# WRANGLE OPEN STREET MAP DATA FOR FRIEDRICHSHAIN-KREUZBERG ###################
###############################################################################
# This script loads csv files into a local sqlite database

# -*- coding: utf-8 -*-
import csv, sqlite3, pandas as pd

# Option1 using pandas which requires to actually read the data
def csv_to_sql(filename, connection, tablename):
    df    = pd.read_csv(filename, encoding = "utf-8")
    con   = sqlite3.connect(connection)
    df.to_sql(tablename, con, index = False)
    del df    
    con.close()  
    
csv_to_sql("nodes.csv", "fk_map", "nodes")
csv_to_sql("nodes_tags.csv", "fk_map", "nodes_tags")
csv_to_sql("ways.csv", "fk_map", "ways")
csv_to_sql("ways_nodes.csv", "fk_map", "ways_nodes")
csv_to_sql("ways_tags.csv", "fk_map", "ways_tags")

# Option2 for large files (only nodes.csv as example)
con = sqlite3.connect("fk_map")
cur = con.cursor()
cur.execute("CREATE TABLE nodes (id, lat, lon, user, uid, version, changeset, timestamp);")

with open("nodes.csv","rb") as fin: 
    dr = csv.DictReader(fin) 
    to_db = [(i['id'], i['lat'], i['lon'], i['user'], i['uid'], i['version'], i['changeset'], i['timestamp']) for i in dr]

cur.executemany("INSERT INTO nodes (id, lat, lon, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db)
con.commit()
con.close()


 
