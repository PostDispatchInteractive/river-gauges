#!/usr/bin/env python
import re
import datetime
import json
import os
import sys
from json import encoder
from random import choice
import mechanize
from urllib.error import HTTPError
import argparse

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
		print(message)
	# Otherwise, it's a cronjob, so let's suppress output


def parse_feeds(forecast, levels, records, output_gauges_file):
	log(' - Parsing the feeds')

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
		try:
			current = [d for d in levels if d['attributes']['gaugelid'] == lid][0]
			f['attributes']['observed'] = current['attributes']['observed']
			f['attributes']['obstime'] = current['attributes']['obstime']

			# Use observed status, rather than forecast status
			f['attributes']['status'] = current['attributes']['status']
		except Exception as e:
			f['attributes']['observed'] = None
			f['attributes']['obstime'] = None
			f['attributes']['status'] = None
			print('ERROR IN NOAA PARSER: Exception during feed parsing')
			print(str(e))
			print(' - Gauge LID: ' + str(lid) )


		# Remove unnecessary fields, part 1
		if 'geometry' in f:
			del f['geometry']

		# Remove unnecessary fields, part 2
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
			print('ERROR IN STATUS FOR ' + f['attributes']['gaugelid'] + '\n')

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
	with open(output_gauges_file, 'w') as j:
		j.write( json.dumps(new_features, sort_keys=True, indent=4) )


def main(output_gauges_file, output_records_file, forecast_url, observed_url):
	# Layer 0 = Observed river stages ("LEVELS=observed")
	# Layer 2 = Forecast river stages (72-hour) ("FLOODS=forecast")

	response = None
	records = None
	forecast = None
	levels = None

	# Grab the NOAA forecast json feed
	log(' - Fetching forecast')
	try:
		br = mechanize.Browser()
		br.set_handle_robots(False)
		br.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9) AppleWebKit/537.71 (KHTML, like Gecko) Version/7.0 Safari/537.71')]
		br.open( forecast_url, timeout=150.0 )
		forecast = br.response().read()
	except HTTPError as e:
		print('ERROR IN NOAA PARSER: Reading NOAA forecast JSON file\n')
		print(str(e.code) + ' ' + str(e.reason))


	# Grab the NOAA observations json feed
	log(' - Fetching observations')
	try:
		br = mechanize.Browser()
		br.set_handle_robots(False)
		br.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9) AppleWebKit/537.71 (KHTML, like Gecko) Version/7.0 Safari/537.71')]
		br.open( observed_url, timeout=150.0 )
		levels = br.response().read()
	except HTTPError as e:
		print('ERROR IN NOAA PARSER: Reading NOAA observations JSON file\n')
		print(str(e.code) + ' ' + str(e.reason))

	# Grab my local copy of historical river gauge levels
	log(' - Fetching local copy of historic crests')
	try:
		with open(output_records_file, 'r') as j:
			records = j.read()
	except:
		print('ERROR IN NOAA PARSER: Reading local river gauges records json file\n')


	# Only process if we have all three data feeds.
	if forecast and levels and records:
		parse_feeds(
			forecast=forecast, 
			levels=levels, 
			records=records,
			output_gauges_file=output_gauges_file,
		)









if __name__ == '__main__':

	local_gauges = [
		'LUSM7', # Mississippi River at Louisiana
		'ALNI2', # Mississippi River at Mel Price (Alton) Lock and Dam
		'GRFI2', # Mississippi River at Grafton
		'EADM7', # Mississippi River at St. Louis
		'CPGM7', # Mississippi River at Cape Girardeau
		'CHSI2', # Mississippi River at Chester
		'CAGM7', # Mississippi River at Winfield Lock and Dam 25

		'UINI2', # Mississippi River at Quincy
		'QLDI2', # Mississippi River at Quincy Lock and Dam 21
		'HNNM7', # Mississippi River at Hannibal

		# 'GSCM7', # Missouri River at Gasconade
		'HRNM7', # Missouri River at Hermann
		'SCLM7', # Missouri River at St. Charles
		'WHGM7', # Missouri River at Washington

		'ARNM7', # Meramec River near Arnold
		'ERKM7', # Meramec River near Eureka
		'PCFM7', # Meramec River near Pacific
		'SLLM7', # Meramec River near Sullivan
		'VLLM7', # Meramec River at Valley Park

		'BYRM7', # Big River at Byrnesville
		'UNNM7', # Bourbeuse River at Union
		'OMNM7', # Cuivre River at Old Monroe
		'TRYM7', # Cuivre River at Troy
		'DRCM7', # Dardenne Creek at St. Peters
		'HARI2', # Illinois River At Hardin
		'NASI2', # Kaskaskia River at New Athens (observations only)
	]


	# FLOODS AND LEVELS URLS
	# ======================

	# From NOAA directly
	# ------------------
	# The fieldnames in this feed are lowercase
	# Layer 0 = Observed river stages ("LEVELS=observed")
	# Layer 2 = Forecast river stages (72-hour) ("FLOODS=forecast")
	#   * (Forecast stages begin at layer 1 (48 hours) and increment by 24 hours up to layer 12 (336 hour)

	# # OLD:
	# forecast_url = 'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Observations/ahps_riv_gauges/MapServer/2/query?where=WFO%3D%27lsx%27&outFields=*&f=pjson'
	# observed_url = 'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Observations/ahps_riv_gauges/MapServer/0/query?where=WFO%3D%27lsx%27&outFields=*&f=pjson'

	# URLs changed in June 2023.
	# See: https://www.weather.gov/media/notification/pdf_2023_24/scn23-01_sunset_idp-gis.pdf
	# And: https://www.weather.gov/media/notification/ref/On-premise__Mapping_To_AWS_Cloud_GIS%20Services_Links.pdf
	# URLs changed again in May 2024.
	# See: https://www.weather.gov/media/notification/pdf_2023_24/scn24-29_nwps_url_changes.pdf
	forecast_url = 'https://mapservices.weather.noaa.gov/eventdriven/rest/services/water/riv_gauges/MapServer/2/query?where=WFO%3D%27lsx%27&outFields=*&f=pjson'
	observed_url = 'https://mapservices.weather.noaa.gov/eventdriven/rest/services/water/riv_gauges/MapServer/0/query?where=WFO%3D%27lsx%27&outFields=*&f=pjson'

	parser = argparse.ArgumentParser()
	parser.add_argument(
		'--output_path', '-o', nargs='?', default=None, help='Specify a directory where the JSON files will be saved',
	)
	parser.add_argument(
		'--forecast_url', '-f', nargs='?', default=None, help='Specify a different URL to the Forecast river stages ArcGIS database',
	)
	parser.add_argument(
		'--observed_url', '-O', nargs='?', default=None, help='Specify a different URL to the Observed river stages ArcGIS database',
	)

	args = vars( parser.parse_args() )

	# Default JSON output directory
	output_path = '/home/newsroom/graphics.stltoday.com/public_html/data/weather/river-gauges'

	# Override output path if user specifies a URL on the command line
	if args['output_path']:
		output_path = str( args['output_path'] )

	# Override URL if user specifies a URL on the command line
	if args['forecast_url']:
		forecast_url = str( args['forecast_url'] )

	# Override URL if user specifies a URL on the command line
	if args['observed_url']:
		observed_url = str( args['observed_url'] )

	# Create output directory if it doesn't exist
	if not os.path.exists(output_path):
		os.makedirs(output_path)


	# Set up JSON filepaths
	output_gauges_file = os.path.join(output_path, 'local_river_gauges.json')
	output_records_file = os.path.join(output_path, 'river_gauge_records.json')


	main(
		output_gauges_file=output_gauges_file,
		output_records_file=output_records_file,
		forecast_url=forecast_url,
		observed_url=observed_url,
	)