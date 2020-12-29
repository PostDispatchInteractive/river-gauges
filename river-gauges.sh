#!/usr/bin/env bash

# Switching from a traditional shebang in hopes that using `env` will be cross-platform.
# Prior to this I had problems because bash was in different places:
#   * My Mac uses /bin/bash
#   * FreeBSD uses /usr/local/bin/bash
# See https://stackoverflow.com/questions/16365130/what-is-the-difference-between-usr-bin-env-bash-and-usr-bin-bash


# Store the script's directory
cwd=$(cd `dirname $0` && pwd)

# Store user directory (On the server, this will be `/home/newsroom/`. On development, it might be something like `/Users/stlrenaj`)
ud=~

# For running on graphics server (staging)
if [[ $cwd = *"staging"* ]]
then
  # If anything unique is needed for the Staging environment, you can put it here.
  script_dir="${cwd}"

# For running on graphics server (production)
elif [[ $cwd = *"stltoday.com"* ]]
then
  # If anything unique is needed for the Production environment, you can put it here.
  script_dir="${cwd}"

# For running on my local development Mac
else
  # If anything unique is needed for the Development environment, you can put it here.
  export PATH=/usr/local/bin:$PATH
  export WORKON_HOME=$HOME/.virtualenvs
  export PROJECT_HOME=$HOME/apps
  export VIRTUALENVWRAPPER_VIRTUALENV_ARGS='--no-site-packages'
  export PIP_VIRTUALENV_BASE=$WORKON_HOME
  export PIP_RESPECT_VIRTUALENV=true
  script_dir="${cwd}"
fi

# Activate `river-gauges` virtualenv
source "${ud}/.virtualenvs/river-gauges3/bin/activate"

# Fetch latest historic river crest data from NOAA and save to a JSON file.
python "${script_dir}/parse-historic-crests.py"

# Fetch latest observed and forecast river stages from NOAA and save to a JSON file.
python "${script_dir}/parse-noaa-river-gauges-feed.py"


