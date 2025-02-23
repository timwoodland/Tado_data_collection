# Tado Data Collection

This is a simple python script that runs in a docker container to collect data from the Tado system and writes this to an influxDB.

Right now this is very much a beta version with a number of limitations, the major one being your version of influxDB must be 1.8 or lower to enable using a database with no credentials. This script is also only tested on the "original" Tado family of devices, not the newer "X" models.

## Setup
You will need to configure the following environement variables:
- TADO_USERNAME=yourTadoUserName
- TADO_PASSWORD=yourTadoPassword
- TADO_CLIENT_SECRET=youTadoClientSecret-see below
- INFLUX_URL=yourInfluxdbUrl
- INFLUX_DB=yourInfluxdbName

To get the Tado Client Secret you can simply access [https://app.tado.com/env.js](https://app.tado.com/env.js)


