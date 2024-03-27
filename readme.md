River gauges
============

* [What is this?](#what-is-this)
* [Where does it live?](#where-does-it-live)
* [Where does the data come from?](#where-does-the-data-come-from)


What is this?
-------------

This repository hosts a scraper that gets data related to forecast levels at gauges along the Mississippi, Missouri, and other local rivers. It also scrapes historic river crest information.

All of this information is obtained from NOAA data feeds.

This repo also contains the CSS, HTML, and JS for a map powered by this data.


Where does it live?
-------------------

The scrapers live in this directory:

* `/home/newsroom/scrapers/river-gauges/`

The scraped data is then saved into two JSON files:

* `/home/newsroom/graphics.stltoday.com/public_html/data/weather/river-gauges/local_river_gauges.json`
* `/home/newsroom/graphics.stltoday.com/public_html/data/weather/river-gauges/river_gauge_records.json`

The map itself lives in this directory:

* `/home/newsroom/graphics.stltoday.com/public_html/apps/river-gauges/`


Where does the data come from?
------------------------------

As of June 2023, we obtain the live data from NOAA's new cloud-based [ArcGIS server](https://mapservices.weather.noaa.gov/eventdriven/rest/services/water/ahps_riv_gauges/). We monitor Layer 0 (observed river stages), and Layer 1 (forecast river stages, 72-hour).

We obtain historic crests from NOAA's [ahps](https://water.weather.gov/ahps/) system. We have to fetch them one gage at a time, using this URL format: `http://water.weather.gov/ahps2/crests.php?wfo=lsx&crest_type=historic&gage={GAGENAME}`.

NWS has a new, improved map for viewing gauges (powered by the same data we're scraping) here: 
https://water.noaa.gov/wfo/lsx



