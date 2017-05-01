#!/usr/bin/env python
import re
import datetime
import json
from json import encoder
from random import choice
import mechanize
from bs4 import BeautifulSoup
import time

crests_url = 'http://water.weather.gov/ahps2/crests.php?wfo=lsx&crest_type=historic&gage='
json_dir = '/home/newsroom/graphics.stltoday.com/public_html/data/weather/river-gauges/'

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




def scrapeFeeds( gauges ):

	historic_crests = None

	# Read previous JSON file, so we can use old values as starting point.
	# We will overwrite these values with new scraped data.
	# If there's a timeout while scraping a gauge, its old data will simply remain. No more missing keys.
	try:
		with open(records_path, 'r') as json_file:
			historic_crests = json.load( json_file )
	# If the JSON file doesn't exist yet, then create a new dict
	except:
		historic_crests = {}


	for gauge in gauges:
		response = None
		# Add a little bit of a wait so we don't hammer the site.
		time.sleep(5)
		# Try to read the page.
		try:
			random_user_agent = choice(user_agents)
			br = mechanize.Browser()
			br.set_handle_robots(False)
			br.addheaders = [('User-agent', random_user_agent)]
			br.open( crests_url + gauge, timeout=150.0 )
			response = br.response().read()
		except:
			# If it failed once, give it one more try.
			try:
				response = None
				br.open( crests_url + gauge, timeout=150.0 )
				response = br.response().read()
			except:
				print 'ERROR IN HISTORIC CREST SCRAPER: Reading ' + gauge + ' crests web page\n'

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
				#print gauge + ' | ' + str(recordLevel) + ' | ' + str(recordDate)


	# Output our new JSON file
	with open(records_path, 'wb') as j:
		j.write( json.dumps(historic_crests,sort_keys=True, indent=4) )




# begin scraping
scrapeFeeds( local_gauges )



