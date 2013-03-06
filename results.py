import json
import urllib2
import re
import os
import sys
import requests
import hashlib
import hmac
import os
import time
from pprint import pprint

county_url = 'http://api.iebc.or.ke/results/county/'
constituency_url = 'http://api.iebc.or.ke/results/constituency/'
ward_url = 'http://api.iebc.or.ke/results/ward/'
pollingstation_url = 'http://api.iebc.or.ke/results/pollingstation/'

token = ''
appid = ""
appsecret = ""

base_dir = './download/'
static_dir = base_dir + 'static/'
other_dir = base_dir + 'test/'

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

def loadjson(baseurl, args, download_dir):
	url = baseurl + "?" + args
	url = re.sub('\s','+', url)
	slug = slugify(url)

	if (os.path.exists(download_dir + slug)):
		filehandle = open(download_dir + slug)
		data = filehandle.read()
		filehandle.close()
	else:
		try:
			keyString = args + 'token=' + token	
			new_key = hmac.new(appsecret, keyString, hashlib.sha256).hexdigest()
			filehandle=urllib2.urlopen(url + "&token=" + token + "&key=" + new_key)
			data = filehandle.read()
			filehandle.close()
		except:
			print "Could not load " + url
			return      

		filehandle = open(download_dir + slug, 'w')
		filehandle.write(data)
		filehandle.close()

	json_data = json.loads(data)
	return json_data

def get_token():
	baseurl = 'http://api.iebc.or.ke/token/'

	key = hmac.new(appsecret, "appid=" + appid, hashlib.sha256).hexdigest()
	filehandle=urllib2.urlopen(baseurl + "?appid="+appid + "&key=" + key)
	data = filehandle.read()
	filehandle.close()
	json_data = json.loads(data)
	return json_data['token']

def get_county_results(c):
	for i in range(1,7):
		loadjson(county_url + c + '/', 'post=' + str(i),other_dir)

def get_ward_results(c):
	for i in range(1,2):
		loadjson(ward_url + c + '/', 'post=' + str(i),other_dir)

def get_constituency_results(c):
	for i in range(1,7):
		loadjson(constituency_url + c + '/', 'post=' + str(i),other_dir)

def get_pollingstation_results(c):
	for i in range(1,7):
		loadjson(pollingstation_url + c + '/', 'post=' + str(i),other_dir)

def get_counties():
	return loadjson("http://api.iebc.or.ke/county/","", static_dir)

def get_county_constituencies(c):
  return loadjson("http://api.iebc.or.ke/constituency/", "county=" + c, static_dir)

def get_constituency_wards(c):
	return loadjson("http://api.iebc.or.ke/ward/", "constituency=" + c, static_dir)

def get_ward_pollingplaces(c):
	return loadjson("http://api.iebc.or.ke/pollingstation/", "ward=" + c, static_dir)

#other_dir = base_dir + str(time.time()) + '/'
#os.makedirs(other_dir)

token = get_token()
counties = get_counties()
for county in counties['region']['locations']:
	get_county_results(county['code'])
	constituencies = get_county_constituencies(county['code'])
	for constituency in constituencies['region']['locations']:
		get_constituency_results(constituency['code'])
		wards = get_constituency_wards(constituency['code'])
		for ward in wards['region']['locations']:
			get_ward_results(ward['code'])
			polling_stations = get_ward_pollingplaces(ward['code'])
#			for polling_station in polling_stations['region']['locations']:
#				get_pollingstation_results(polling_station['code'])
