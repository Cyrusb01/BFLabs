# BFLABS Flask App

## Data
Data taken from database behind VPN, and updated with any necessary coinapi data.
CSV files stored, and then written to local postgresql database.

This enables REST API functionality; `https://blockforcelabs.com/api/api/v1/load_daily?symbol=BTC-USDT`

For the purposes of data disply, pull data from this local database to then plot using plotly

## Files
`variables.py` -> variables used to customize Plotly graphs and functionality
`helpers.py`   -> functions used to calculate correlations, and create graph dicts

