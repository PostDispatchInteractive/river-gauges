#!/usr/bin/env python
import re
import datetime
import time
import arrow
import json
import os
import sys
import requests
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



def main(gauges, root_url, output_gauges_file):

	data = []

	for gauge in gauges:
		log(gauge)
		r = None
		# Add a little bit of a wait so we don't hammer the site.
		time.sleep(4)
		# Try to read the page.
		try:
			log(root_url + gauge)
			r = requests.get(root_url + gauge)
		except:
			time.sleep(15)
			# If it failed once, give it one more try.
			try:
				r = requests.get(root_url + gauge)
			except:
				print('ERROR IN HISTORIC CREST SCRAPER: Reading ' + gauge + ' crests web page\n')
				print(r)

		if r:
			gauge_json = r.json()
			data.append(gauge_json)

	# Output our new JSON file
	with open(output_gauges_file, 'w') as j:
		j.write( json.dumps(data, sort_keys=True, indent=4) )



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

	# # From NOAA directly
	# # ------------------
	# # The fieldnames in this feed are lowercase
	# # Layer 0 = Observed river stages ("LEVELS=observed")
	# # Layer 2 = Forecast river stages (72-hour) ("FLOODS=forecast")
	# #   * (Forecast stages begin at layer 1 (48 hours) and increment by 24 hours up to layer 12 (336 hour)

	# # # OLD:
	# # forecast_url = 'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Observations/ahps_riv_gauges/MapServer/2/query?where=WFO%3D%27lsx%27&outFields=*&f=pjson'
	# # observed_url = 'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Observations/ahps_riv_gauges/MapServer/0/query?where=WFO%3D%27lsx%27&outFields=*&f=pjson'

	# # URLs changed in June 2023.
	# # See: https://www.weather.gov/media/notification/pdf_2023_24/scn23-01_sunset_idp-gis.pdf
	# # And: https://www.weather.gov/media/notification/ref/On-premise__Mapping_To_AWS_Cloud_GIS%20Services_Links.pdf
	# # URLs changed again in May 2024.
	# # See: https://www.weather.gov/media/notification/pdf_2023_24/scn24-29_nwps_url_changes.pdf
	# forecast_url = 'https://mapservices.weather.noaa.gov/eventdriven/rest/services/water/riv_gauges/MapServer/2/query?where=WFO%3D%27lsx%27&outFields=*&f=pjson'
	# observed_url = 'https://mapservices.weather.noaa.gov/eventdriven/rest/services/water/riv_gauges/MapServer/0/query?where=WFO%3D%27lsx%27&outFields=*&f=pjson'

	root_url = 'https://api.water.noaa.gov/nwps/v1/gauges/'

	parser = argparse.ArgumentParser()
	parser.add_argument(
		'--output_path', '-o', nargs='?', default=None, help='Specify a directory where the JSON files will be saved',
	)
	parser.add_argument(
		'--url', '-u', nargs='?', default=None, help='Specify a different URL to NOAA\'s historic crests file. (e.g. `http://water.weather.gov/ahps2/crests.php?wfo=lsx&crest_type=historic&gage=`)',
	)

	args = vars( parser.parse_args() )

	# Default JSON output directory
	output_path = '/home/newsroom/graphics.stltoday.com/public_html/data/weather/river-gauges'

	# Override output path if user specifies a URL on the command line
	if args['output_path']:
		output_path = str( args['output_path'] )

	# Override URL if user specifies a URL on the command line
	if args['url']:
		root_url = str( args['url'] )

	# Create output directory if it doesn't exist
	if not os.path.exists(output_path):
		os.makedirs(output_path)


	# Set up JSON filepaths
	output_gauges_file = os.path.join(output_path, 'local_river_gauges.json')


	main(
		gauges=local_gauges,
		root_url=root_url,
		output_gauges_file=output_gauges_file,
	)