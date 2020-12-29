#!/usr/bin/env bash
source /home/newsroom/.virtualenvs/river-gauges/bin/activate
python /home/newsroom/scrapers/river-gauges/parse-historic-crests.py
python /home/newsroom/scrapers/river-gauges/parse-noaa-river-gauges-feed.py
