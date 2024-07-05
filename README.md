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

The scraper lives in this directory:

* `/home/newsroom/scrapers/river-gauges/`

The scraped data is then saved into one JSON file:

* `/home/newsroom/graphics.stltoday.com/public_html/data/weather/river-gauges/local_river_gauges.json`

The map itself lives in this directory:

* `/home/newsroom/graphics.stltoday.com/public_html/apps/river-gauges/`


Where does the data come from?
------------------------------

As of July 2024, we obtain the live data from NOAA's [National Water Prediction Service API](https://api.water.noaa.gov/nwps/v1/docs/). This single source provides current observations, 14-day forecasts, and historic crests for any specified gauge ID.

NWS has a new, improved map for viewing gauges (powered by the same data we're scraping) here:
https://water.noaa.gov/wfo/lsx



