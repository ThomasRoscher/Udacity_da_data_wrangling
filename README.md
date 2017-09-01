# Udacity_da_data_wrangling

This project is connected to the Udacity Data Wrangling course. I used Open Streetmap data which is provided in XML format. The basic structure of this project is as follows:

- I explore the data and audit some features (see audit.py)
- Based on those findings I write cleaning functions (also see audit.py)
- I then write the XML data to csv files, cleanig is done during parsing leaving the original xml untouched (see parse_to_csv.py)
- Next, I store the csv files in a SQL database (see load_into_sql.py)
- Lastly, I do some queries to analyse the data (see analyse_sql.py)

I used the OSM data for Berlin's borough “Friedrichshain-Kreuzberg” which can be found here: http://www.openstreetmap.org/relation/55764
The reason for choosing this area is quiet straight forward: I live in this area and it surely is one of the most vibrating, coolest places on earth :)


