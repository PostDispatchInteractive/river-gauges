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
# noaa_midwest_floods_url = 'https://emgis.oa.mo.gov/arcgis/rest/services/feeds/noaa_midwest_river_gauges/MapServer/0/query?where=WFO%3D%27lsx%27&outFields=*&f=pjson'
# noaa_midwest_levels_url = 'https://emgis.oa.mo.gov/arcgis/rest/services/feeds/noaa_midwest_river_gauges/MapServer/1/query?where=WFO%3D%27lsx%27&outFields=*&f=pjson'

# From NOAA directly
# The fieldnames in this feed are lowercase
# Layer 0 = Observed river stages
# Layer 2 = Forecast river stages (72-hour)
#   * (Forecast stages begin at layer 1 (48 hours) and increment by 24 hours up to layer 12 (336 hour)
noaa_midwest_floods_url = 'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Observations/ahps_riv_gauges/MapServer/2/query?where=WFO%3D%27lsx%27&outFields=*&f=pjson'
noaa_midwest_levels_url = 'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Observations/ahps_riv_gauges/MapServer/0/query?where=WFO%3D%27lsx%27&outFields=*&f=pjson'

json_dir = '/home/newsroom/graphics.stltoday.com/public_html/data/weather/river-gauges/'

json_file = 'local_river_gauges.json'
json_url = json_dir + json_file

records_file = 'river_gauge_records.json'
records_url = json_dir + records_file

local_gauges = [
	'CPGM7',
	'CHSI2',
	'GRFI2',
	'LUSM7',
	'ALNI2',
	# 'UINI2', #quincy
	# 'QLDI2', #quincy
	# 'HNNM7', #hannibal
	'EADM7',
	'CAGM7',
	'ARNM7',
	'ERKM7',
	'PCFM7',
	'SLLM7',
	'VLLM7',
	'GSCM7',
	'HRNM7',
	'SCLM7',
	'WHGM7',
	'BYRM7',
	'UNNM7'
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

	features = forecast['features']
	features = [d for d in features if d['attributes']['gaugelid'] in local_gauges]
	# features = [d for d in features if d['attributes']['status'] != 'no_forecast']

	new_features = []
	for f in features:
		# Store this gauge's id and location
		lid = f['attributes']['gaugelid']
		loc = f['attributes']['location']

		# Add current observed level from NOAA levels json file
		current = [d for d in levels['features'] if d['attributes']['gaugelid'] == lid][0]
		f['attributes']['observed'] = current['attributes']['observed']
		f['attributes']['obstime'] = current['attributes']['obstime']

		# Use observed status, rather than forecast status
		f['attributes']['status'] = current['attributes']['status']


		# Remove unnecessary fields
		del f['geometry']
		del f['attributes']['wfo']
		del f['attributes']['hdatum']
		del f['attributes']['secvalue']
		del f['attributes']['secunit']
		del f['attributes']['lowthresh']
		del f['attributes']['lowthreshu']
		del f['attributes']['objectid']
		del f['attributes']['pedts']
		del f['attributes']['idp_source']
		del f['attributes']['idp_subset']



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
	with open(json_url, 'wb') as j:
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
	with open(records_url, 'rb') as j:
		records = j.read()
except:
	print 'ERROR IN NOAA PARSER: Reading local river gauges records json file\n'


if forecast and levels and records:
	parseFeed(forecast, levels, records)



