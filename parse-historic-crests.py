#!/usr/bin/env python
import re
import datetime
import json
from json import encoder
from random import choice
import mechanize
from bs4 import BeautifulSoup


crests_url = 'http://water.weather.gov/ahps2/crests.php?wfo=lsx&crest_type=historic&gage='
json_dir = '/home/newsroom/graphics.stltoday.com/public_html/data/weather/river-gauges/'

records_file = 'river_gauge_records.json'
records_url = json_dir + records_file

local_gauges = [
	'CPGM7',
	'CHSI2',
	'GRFI2',
	'HNNM7',
	'LUSM7',
	'ALNI2',
	'UINI2',
	'QLDI2',
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



def scrapeFeeds( gauges ):

	historic_crests = {}

	for gauge in gauges:
		response = None
		try:
			random_user_agent = choice(user_agents)
			br = mechanize.Browser()
			br.set_handle_robots(False)
			br.addheaders = [('User-agent', random_user_agent)]
			br.open( crests_url + gauge, timeout=120.0 )
			response = br.response().read()
		except:
			print 'ERROR IN HISTORIC CREST SCRAPER: Reading ' + gauge + ' crests web page'

		if response:
			soup = BeautifulSoup( response )
			blob = soup.find('div',class_="water_information")
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
				historic_crests[gauge] = {}
				historic_crests[gauge]['record-level'] = recordLevel
				historic_crests[gauge]['record-date'] = recordDate
				print gauge + ' | ' + str(recordLevel) + ' | ' + str(recordDate)


	# Output our new JSON file
	with open(records_url, 'wb') as j:
		j.write( json.dumps(historic_crests,sort_keys=True, indent=4) )




# begin scraping
scrapeFeeds( local_gauges )



