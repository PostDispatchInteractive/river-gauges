River gauges
============

* [What is this?](#what-is-this)
* [Where does it live?](#where-does-it-live)


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

