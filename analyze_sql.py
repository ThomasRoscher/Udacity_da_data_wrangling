import sqlite3

# check the tables in the database
con = sqlite3.connect("fk_map")
cur = con.cursor() 
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
available_table = (cur.fetchall())

# number of nodes
cur.execute("SELECT COUNT(*) FROM nodes;")
number_nodes = (cur.fetchall())

# number of ways
cur.execute("SELECT COUNT(*) FROM ways;")
number_ways = (cur.fetchall())

# number of unique users
cur.execute("SELECT count(DISTINCT user) as num FROM (SELECT user from nodes union all select user from ways);")
unique_users = (cur.fetchall())

# number of unique users and their contributions
cur.execute("SELECT count(user) as num FROM (SELECT user from nodes union all select user from ways) GROUP BY user ORDER BY num DESC;")
unique_users2 = (cur.fetchall())

# number of rare users 
cur.execute("SELECT count(user) as num FROM (SELECT user from nodes union all select user from ways) GROUP BY user HAVING num < 4;")
rare_users = (cur.fetchall())

cur.execute("SELECT timestamp FROM nodes;")

# top ten amenities
cur.execute("SELECT value, COUNT(*) as num FROM nodes_tags WHERE key='amenity' GROUP BY value ORDER BY num DESC;")
top_amenites = (cur.fetchall())

# entries in nodes over time 
cur.execute("SELECT COUNT(*), strftime('%Y', timestamp) as Year FROM nodes Group by year ORDER by year;")
over_time_nodes = (cur.fetchall())

# entries in ways over time 
cur.execute("SELECT COUNT(*), strftime('%Y', timestamp) as Year FROM ways Group by year ORDER by year;")
over_time_ways = (cur.fetchall())