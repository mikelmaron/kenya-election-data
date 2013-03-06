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
other_dir = base_dir + 'latest/'
geo_dir = './data/'

CACHE = True

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
	elif CACHE:
		return
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

def get_county_result(c,i):
	return loadjson(county_url + c + '/', 'post=' + str(i),other_dir)

def get_ward_results(c):
	for i in range(1,7):
		loadjson(ward_url + c + '/', 'post=' + str(i),other_dir)

def get_ward_result(c,i):
	return loadjson(ward_url + c + '/', 'post=' + str(i),other_dir)

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

def get_county(name):
	counties = get_counties()
	for county in counties['region']['locations']:
		if county['name'] == name:
			return county

def get_constituency(c, name):
	constituencies = get_county_constituencies(c)
	for constituency in constituencies['region']['locations']:
		if constituency['name'] == name:
			return constituency

sys.stdout.write('{"type": "FeatureCollection","features": [')

first = True
counties = get_counties()
for county in counties['region']['locations']:
	constituencies = get_county_constituencies(county['code'])
	for constituency in constituencies['region']['locations']:
		wards = get_constituency_wards(constituency['code'])
		for ward in wards['region']['locations']:
			ward_geo = loadjson(ward['polygon'], "", geo_dir)
			if ward_geo is None:
				continue

			ward_result = get_ward_result(ward['code'], 1)
			if ward_result is not None and ward_result['contests'][0]['locations'] is not None:
				ward_geo['features'][0]['properties']['RESULT'] = "1"
				ward_geo['features'][0]['properties']['DISPUTED'] = ward_result['contests'][0]['locations'][0]['disputed']
				ward_geo['features'][0]['properties']['REGISTERED'] = ward_result['contests'][0]['locations'][0]['registered']
				ward_geo['features'][0]['properties']['SPOILT'] = ward_result['contests'][0]['locations'][0]['spoilt']
				ward_geo['features'][0]['properties']['REJECTED'] = ward_result['contests'][0]['locations'][0]['rejected']
				ward_geo['features'][0]['properties']['REPORTED'] = ward_result['contests'][0]['locations'][0]['reported']
				ward_geo['features'][0]['properties']['VALID'] = ward_result['contests'][0]['locations'][0]['valid']
				ward_geo['features'][0]['properties']['SPOILT_VALID'] = float(ward_result['contests'][0]['locations'][0]['spoilt']) / float(ward_result['contests'][0]['locations'][0]['valid'])
			else:
				ward_geo['features'][0]['properties']['RESULT'] = "0"

			ward_geo['features'][0]['properties']['NAME'] = ward['name']

 
		
			if first == False:
				print ","
			first = False
			print json.dumps(ward_geo['features'][0])				

sys.stdout.write(']}')

#		if result is None:
#			print "\tNO RESULT:" + str(i)
#		else:
#			print "\tRESULT:" + str(i)
	
#def get_county_results(c):
#	for i in range(1,7)		
#nairobi = get_county("NAIROBI")
#kibra = get_constituency(nairobi['code'], "KIBRA")
#print kibra['code']

