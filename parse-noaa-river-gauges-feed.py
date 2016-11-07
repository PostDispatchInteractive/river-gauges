#!/usr/bin/env python
import re
import datetime
import json
from json import encoder
from random import choice
import mechanize


noaa_midwest_floods_url = 'https://emgis.oa.mo.gov/arcgis/rest/services/feeds/noaa_midwest_river_gauges/MapServer/0/query?where=WFO%3D%27lsx%27&outFields=*&f=pjson'
noaa_midwest_levels_url = 'https://emgis.oa.mo.gov/arcgis/rest/services/feeds/noaa_midwest_river_gauges/MapServer/1/query?where=WFO%3D%27lsx%27&outFields=*&f=pjson'
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



def parseFeed(forecast,levels, records):
	forecast = json.loads(forecast)
	levels = json.loads(levels)
	records = json.loads(records)

	features = forecast['features']
	features = [d for d in features if d['attributes']['GaugeLID'] in local_gauges]
	# features = [d for d in features if d['attributes']['Status'] != 'no_forecast']

	new_features = []
	for f in features:
		# Store this gauge's id and location
		lid = f['attributes']['GaugeLID']
		loc = f['attributes']['Location']

		# Add current observed level from NOAA levels json file
		current = [d for d in levels['features'] if d['attributes']['GaugeLID'] == lid][0]
		f['attributes']['Observed'] = current['attributes']['Observed']
		f['attributes']['ObsTime'] = current['attributes']['ObsTime']

		# Use observed status, rather than forecast status
		f['attributes']['Status'] = current['attributes']['Status']


		# Remove unnecessary fields
		del f['geometry']
		del f['attributes']['WFO']
		del f['attributes']['HDatum']
		del f['attributes']['SecValue']
		del f['attributes']['SecUnit']
		del f['attributes']['LowThresh']
		del f['attributes']['LowThreshU']
		del f['attributes']['FID']
		del f['attributes']['PEDTS']

		# Change status strings into integers to save space and be more easily parsed
		if f['attributes']['Status'] in ['no_forecast','not_defined','obs_not_current','out_of_service','low_threshold']:
			f['attributes']['Status'] = None
		elif f['attributes']['Status'] == 'no_flooding':
			f['attributes']['Status'] = 1
		elif f['attributes']['Status'] == 'action':
			f['attributes']['Status'] = 2
		elif f['attributes']['Status'] == 'minor':
			f['attributes']['Status'] = 3
		elif f['attributes']['Status'] == 'moderate':
			f['attributes']['Status'] = 4
		elif f['attributes']['Status'] == 'major':
			f['attributes']['Status'] = 5
		else:
			print 'ERROR IN STATUS FOR ' + f['attributes']['GaugeLID']

		# Shrink names
		if 'Lock and Dam' in loc:
			f['attributes']['Location'] = loc.replace('Lock and Dam','L&D')

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

# Grab the NOAA forecast json feed
try:
	random_user_agent = choice(user_agents)

	br = mechanize.Browser()
	br.set_handle_robots(False)
	br.addheaders = [('User-agent', random_user_agent)]
	br.open( noaa_midwest_floods_url, timeout=120.0 )
	forecast = br.response().read()
except:
	print 'ERROR IN NOAA PARSER: Reading NOAA JSON file'


# Grab the NOAA observations json feed
try:
	random_user_agent = choice(user_agents)

	br = mechanize.Browser()
	br.set_handle_robots(False)
	br.addheaders = [('User-agent', random_user_agent)]
	br.open(noaa_midwest_levels_url)
	levels = br.response().read()
except:
	print 'ERROR IN NOAA PARSER: Reading NOAA JSON file'


# Grab my local copy of historical river gauge levels
try:
	with open(records_url, 'rb') as j:
		records = j.read()
except:
	print 'ERROR IN NOAA PARSER: Reading local river gauges records json file'


parseFeed(forecast, levels, records)



