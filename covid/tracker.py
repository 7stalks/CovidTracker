import csv
import datetime
import re
import sys
from collections import defaultdict

import requests


def get_county_census_data():
    """Pull the 2019 Census data"""
    url = 'https://raw.githubusercontent.com/John-Jackson99/COVID-19-Data/master/Pop%20by%20County%202019.csv'
    data = requests.get(url).content.decode("ISO-8859-1")
    results = {}
    reader = csv.DictReader(data.splitlines())
    for _row in reader:
        row = {k.lower(): v for k, v in _row.items()}
        key = (row['county'].lower(), row['state'].lower())
        row['population'] = int(re.sub(",", "", row['population']))
        row['area in square miles - land area'] = float(row['area in square miles - land area'])
        row['population sq mi land'] = float(row['population sq mi land'])
        row['housing units sq mi'] = float(row['housing units sq mi'])
        results[key] = row
    return results


def get_covid_data():
    """Pull the latest COVID data"""
    url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
    data = requests.get(url).content.decode('utf8')

    results = {}
    reader = csv.DictReader(data.splitlines())
    for row in reader:
        key = (row['county'].lower(), row['state'].lower())
        if key not in results:
            results[key] = []
        row['date'] = datetime.date(int(row['date'].split("-")[0]),
                                    int(row['date'].split("-")[1]),
                                    int(row['date'].split("-")[2]))
        row['cases'] = int(row['cases'])
        row['deaths'] = int(row['deaths'])
        results[key].append(row)
    return results


def get_combined_row_data(start_date, state=None, county=None):
    """We need to combine these out."""

    county_data = get_county_census_data()
    covid_data = get_covid_data()

    local_counties = {}
    found_counties = []
    for (county_key, state_key), data in county_data.items():
        if county and county.lower() == county_key:
            if state:
                if state.lower() == state_key:
                    local_counties[(county_key, state_key)] = data
                    found_counties.append((county_key, state_key))
            else:
                local_counties[(county_key, state_key)] = data
                found_counties.append((county_key, state_key))
        elif state and state.lower() == state_key:
            local_counties[(county_key, state_key)] = data
            found_counties.append((county_key, state_key))

    print("Narrowed down to %s" % len(found_counties))

