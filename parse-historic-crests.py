#!/usr/bin/env python
import re
import datetime
import json
import sys
import os
from json import encoder
from random import choice
import mechanize
from bs4 import BeautifulSoup
import time
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




def main( gauges, root_url, output_file ):

	historic_crests = None

	# Read previous JSON file, so we can use old values as starting point.
	# We will overwrite these values with new scraped data.
	# If there's a timeout while scraping a gauge, its old data will simply remain. No more missing keys.
	try:
		with open(output_file, 'r') as json_file:
			historic_crests = json.load( json_file )
	# If the JSON file doesn't exist yet, then create a new dict
	except:
		historic_crests = {}


	for gauge in gauges:
		log(gauge)
		response = None
		# Add a little bit of a wait so we don't hammer the site.
		time.sleep(2)
		# Try to read the page.
		try:
			br = mechanize.Browser()
			br.set_handle_robots(False)
			br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36')]
			br.open( root_url + gauge, timeout=150.0 )
			response = br.response().read()
		except:
			# If it failed once, give it one more try.
			try:
				response = None
				br.open( root_url + gauge, timeout=150.0 )
				response = br.response().read()
			except:
				print('ERROR IN HISTORIC CREST SCRAPER: Reading ' + gauge + ' crests web page\n')

		if response:
			soup = BeautifulSoup( response, 'lxml' )
			blob = soup.find( 'div', class_='water_information' )
			# records = blob.split('<br/>\n')
			matchObj = re.search( r'\(1\) ([\d\.]+) ft on (\d+)/(\d+)/(\d+)', blob.text )
			if matchObj:
				recordLevel = float( matchObj.group(1) )
				mo = int( matchObj.group(2) )
				dy = int( matchObj.group(3) )
				yr = int( matchObj.group(4) )
				recordDate = datetime.datetime(yr, mo, dy, 12, 0)
				# Convert to string in format JSON expects
				recordDate = recordDate.isoformat(' ').split('.')[0]

				# Now add this historic crest to our master object
				if not gauge in historic_crests.keys():
					historic_crests[gauge] = {}
				historic_crests[gauge]['record-level'] = recordLevel
				historic_crests[gauge]['record-date'] = recordDate

				# log(gauge + ' | ' + str(recordLevel) + ' | ' + str(recordDate))


	# Output our new JSON file
	with open(output_file, 'w') as j:
		j.write( json.dumps(historic_crests, sort_keys=True, indent=4) )






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

		'GSCM7', # Missouri River at Gasconade
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

	parser = argparse.ArgumentParser()
	parser.add_argument(
		'--output_path', '-o', nargs='?', default=None, help='Specify a directory where the JSON file will be saved',
	)
	parser.add_argument(
		'--url', '-u', nargs='?', default=None, help='Specify a different URL to NOAA\'s historic crests file. (e.g. `http://water.weather.gov/ahps2/crests.php?wfo=lsx&crest_type=historic&gage=`)',
	)

	args = vars( parser.parse_args() )

	# Default URLs and paths
	root_url = 'http://water.weather.gov/ahps2/crests.php?wfo=lsx&crest_type=historic&gage='
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

	# Directory from which the script is running
	script_path = os.path.dirname(os.path.realpath(__file__))

	# Set up JSON filepath
	output_file = os.path.join(output_path, 'river_gauge_records.json')

	# Begin scraping
	main( 
		gauges=local_gauges,
		root_url=root_url,
		output_file=output_file,
	)

