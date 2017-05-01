#!/usr/bin/env python
import re
import datetime
import json
from json import encoder
from random import choice
import mechanize
import urllib2


# From Missouri
# The fieldnames in this feed are mixed-case
noaa_midwest_floods_url = 'https://emgis.oa.mo.gov/arcgis/rest/services/feeds/noaa_midwest_river_gauges/MapServer/0/query?where=WFO%3D%27lsx%27&outFields=*&f=pjson'
noaa_midwest_levels_url = 'https://emgis.oa.mo.gov/arcgis/rest/services/feeds/noaa_midwest_river_gauges/MapServer/1/query?where=WFO%3D%27lsx%27&outFields=*&f=pjson'

# From NOAA directly
# The fieldnames in this feed are lowercase
# Layer 0 = Observed river stages
# Layer 2 = Forecast river stages (72-hour)
#   * (Forecast stages begin at layer 1 (48 hours) and increment by 24 hours up to layer 12 (336 hour)
# noaa_midwest_floods_url = 'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Observations/ahps_riv_gauges/MapServer/2/query?where=WFO%3D%27lsx%27&outFields=*&f=pjson'
# noaa_midwest_levels_url = 'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Observations/ahps_riv_gauges/MapServer/0/query?where=WFO%3D%27lsx%27&outFields=*&f=pjson'

json_dir = '/home/newsroom/graphics.stltoday.com/public_html/data/weather/river-gauges/'

json_filename = 'local_river_gauges.json'
json_path = json_dir + json_filename

records_filename = 'river_gauge_records.json'
records_path = json_dir + records_filename

local_gauges = [
	'LUSM7', #Mississippi River at Louisiana
	'ALNI2', #Mississippi River at Mel Price (Alton) Lock and Dam
	'GRFI2', #Mississippi River at Grafton
	'EADM7', #Mississippi River at St. Louis
	'CPGM7', #Mississippi River at Cape Girardeau
	'CHSI2', #Mississippi River at Chester
	'CAGM7', #Mississippi River at Winfield Lock and Dam 25

	'UINI2', #Mississippi River at Quincy
	'QLDI2', #Mississippi River at Quincy Lock and Dam 21
	'HNNM7', #Mississippi River at Hannibal

	'GSCM7', #Missouri River at Gasconade
	'HRNM7', #Missouri River at Hermann
	'SCLM7', #Missouri River at St. Charles
	'WHGM7', #Missouri River at Washington

	'ARNM7', #Meramec River near Arnold
	'ERKM7', #Meramec River near Eureka
	'PCFM7', #Meramec River near Pacific
	'SLLM7', #Meramec River near Sullivan
	'VLLM7', #Meramec River at Valley Park

	'BYRM7', #Big River at Byrnesville
	'UNNM7', #Bourbeuse River at Union
	'OMNM7', #Cuivre River at Old Monroe
	'TRYM7', #Cuivre River at Troy
	'DRCM7', #Dardenne Creek at St. Peters
	'NASI2', #Kaskaskia River at New Athens (observations only)

]

user_agents = [
	'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9) AppleWebKit/537.71 (KHTML, like Gecko) Version/7.0 Safari/537.71',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36',
	'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0',
	'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
	'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0',
]

def isFloat(value):
	try:
		float(value)
		return True
	except ValueError:
		return False

def isInt(value):
	try:
		int(value)
		return True
	except ValueError:
		return False

def log(message):
	# If we're running from command line, then print output
	if sys.stdout.isatty():
		print message
	# Otherwise, it's a cronjob, so let's suppress output


def parseFeed(forecast,levels, records):
	forecast = json.loads(forecast)
	levels = json.loads(levels)
	records = json.loads(records)

	# convert keys to lowercase so I can switch easily between MO and NOAA feeds
	levels = [
		{
			dk.lower():{
				k.lower():v
					for k, v in dv.items()
			}
				for dk, dv in d.items()
		}
			for d in levels['features']
	]

	# convert keys to lowercase so I can switch easily between MO and NOAA feeds
	features = [
		{
			dk.lower():{
				k.lower():v
					for k, v in dv.items()
			}
				for dk, dv in d.items()
		}
			for d in forecast['features']
	]

	features = [d for d in features if d['attributes']['gaugelid'] in local_gauges]
	# features = [d for d in features if d['attributes']['status'] != 'no_forecast']

	new_features = []
	for f in features:
		# Store this gauge's id and location
		lid = f['attributes']['gaugelid']
		loc = f['attributes']['location']

		# Add current observed level from NOAA levels json file
		current = [d for d in levels if d['attributes']['gaugelid'] == lid][0]
		f['attributes']['observed'] = current['attributes']['observed']
		f['attributes']['obstime'] = current['attributes']['obstime']

		# Use observed status, rather than forecast status
		f['attributes']['status'] = current['attributes']['status']

		# Remove unnecessary fields
		if 'geometry' in f:
			del f['geometry']

		fields = ['wfo','hdatum','secvalue','secunit','lowthresh','lowthreshu','objectid','pedts','idp_source','idp_subset']
		for field in fields:
			if field in f['attributes']:
				del f['attributes'][field]



		# Change status strings into integers to save space and be more easily parsed
		if f['attributes']['status'] in ['no_forecast','not_defined','obs_not_current','out_of_service','low_threshold']:
			f['attributes']['status'] = None
		elif f['attributes']['status'] == 'no_flooding':
			f['attributes']['status'] = 1
		elif f['attributes']['status'] == 'action':
			f['attributes']['status'] = 2
		elif f['attributes']['status'] == 'minor':
			f['attributes']['status'] = 3
		elif f['attributes']['status'] == 'moderate':
			f['attributes']['status'] = 4
		elif f['attributes']['status'] == 'major':
			f['attributes']['status'] = 5
		else:
			print 'ERROR IN STATUS FOR ' + f['attributes']['gaugelid'] + '\n'

		# Shrink names
		if 'Lock and Dam' in loc:
			f['attributes']['location'] = loc.replace('Lock and Dam','L&D')

		# Add historical information from local records JSON file
		f['attributes']['record-level'] = records[ lid ]['record-level']
		f['attributes']['record-date'] = records[ lid ]['record-date']


		# Move everything under Attributes to top level of the feature
		f = f['attributes']

		new_features.append(f)

	# Output our new JSON file
	with open(json_path, 'wb') as j:
		j.write( json.dumps(new_features,sort_keys=True, indent=4) )




response = None
records = None
forecast = None
levels = None

# This is to work around "SSL: CERTIFICATE_VERIFY_FAILED" error
# As seen here: http://stackoverflow.com/a/35960702/566307
import ssl
try:
	_create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
	# Legacy Python that doesn't verify HTTPS certificates by default
	pass
else:
	# Handle target environment that doesn't support HTTPS verification
	ssl._create_default_https_context = _create_unverified_https_context


# Grab the NOAA forecast json feed
try:
	random_user_agent = choice(user_agents)
	br = mechanize.Browser()
	br.set_handle_robots(False)
	br.addheaders = [('User-agent', random_user_agent)]
	br.open( noaa_midwest_floods_url, timeout=150.0 )
	forecast = br.response().read()
except urllib2.HTTPError, e:
	print 'ERROR IN NOAA PARSER: Reading NOAA forecast JSON file\n'
	print e.code + ' ' + e.reason


# Grab the NOAA observations json feed
try:
	random_user_agent = choice(user_agents)
	br = mechanize.Browser()
	br.set_handle_robots(False)
	br.addheaders = [('User-agent', random_user_agent)]
	br.open( noaa_midwest_levels_url, timeout=150.0 )
	levels = br.response().read()
except urllib2.HTTPError, e:
	print 'ERROR IN NOAA PARSER: Reading NOAA observations JSON file\n'
	print e.code + ' ' + e.reason

# Grab my local copy of historical river gauge levels
try:
	with open(records_path, 'rb') as j:
		records = j.read()
except:
	print 'ERROR IN NOAA PARSER: Reading local river gauges records json file\n'


# Only process if we have all three data feeds.
if forecast and levels and records:
	parseFeed(forecast, levels, records)



