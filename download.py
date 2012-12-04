import json
import urllib2
import re
import os
import sys
from pprint import pprint

county_url = 'http://vote.iebc.or.ke/county/'
constituency_url = 'http://vote.iebc.or.ke/constituency/?county='
ward_url = 'http://vote.iebc.or.ke/ward/?constituency='
pollingstation_constituency_url = 'http://vote.iebc.or.ke/pollingstation/?constituency='
pollingstation_ward_url = 'http://vote.iebc.or.ke/pollingstation/?ward='

download_dir = './data/'

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    #import unicodedata
    #value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    value = re.sub('[-\s]+', '-', value)
    return value

def loadjson(url):
	url = re.sub('\s','+', url)
	slug = slugify(url)

	if (os.path.exists(download_dir + slug)):
		filehandle = open(download_dir + slug)
		data = filehandle.read()
		filehandle.close()
	else:
		filehandle=urllib2.urlopen(url)
		data = filehandle.read()
		filehandle.close()

		filehandle = open(download_dir + slug, 'w')
		filehandle.write(data)
		filehandle.close()

	json_data = json.loads(data)
	return json_data

data = loadjson(county_url)
for county in data['results']:
	#print county['name']
	constituencies = loadjson(constituency_url + county['name'])
	for constituency in constituencies['results']:
		#print "\t" + constituency['name']
		wards = loadjson(ward_url + constituency['name'])
		polling = loadjson(pollingstation_constituency_url + constituency['name'])
		for ward in wards['results']:
			#print "\t\t" + ward['name']
			stations = loadjson(pollingstation_ward_url + ward['name'])
			for station in stations['results']:
				sys.stdout.write(county['name'] + "\t")
				sys.stdout.write(constituency['name'] + "\t")
				sys.stdout.write(ward['name'] + "\t")
				if station['name']:
					sys.stdout.write(station['name'])
				print("\t" + str(station['point']['lat']) + "\t" + str(station['point']['lon']))
