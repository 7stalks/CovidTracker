import csv
import datetime
import re
import sys
from collections import defaultdict, OrderedDict

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
        try:
            row['deaths'] = int(row['deaths'])
        except ValueError:
            row['deaths'] = 0
        results[key].append(row)
    return results



def get_combined_row_data(start_date, state=None, county=None, data_types=['cases', 'deaths'],
                          include_census=False, my_county=None):
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
        elif state and state.lower() == state_key and county is None:
            local_counties[(county_key, state_key)] = data
            found_counties.append((county_key, state_key))

    print("\nNarrowed down to %s based on %r" %(len(found_counties), state if state else county))

    # Now lets fill in the gaps in data..

    covid_results = []
    found_counties.sort()
    my_county_1x_rate = {'County': '%s 1x day/day growth' % my_county}
    for county in found_counties:
        baseline_start_date = datetime.date(2019, 1, 1)
        prior_result = {'cases': 0, 'deaths': 0, 'date': baseline_start_date}

        covid_result = OrderedDict([("County", local_counties[county].get('county'))])
        if include_census:
            covid_result = OrderedDict([
                ("County", local_counties[county].get('county')),
                ("State", local_counties[county].get('state')),
                ("Population", local_counties[county].get('population')),
            ])

        if not isinstance(data_types, (list, tuple)) and include_census:
            covid_result['Initial Case'] = None
            covid_result['Datatype'] = data_types
        for key, data in covid_data.items():
            if key == county:
                print("  County: {:<16} Population: {:,}".format(
                    covid_result['County'], local_counties[county].get('population')))
                while baseline_start_date < datetime.date.today():
                    result = next((x for x in data if x['date'] == baseline_start_date), None)
                    if result is None:
                        prior_result['date'] = baseline_start_date
                        result = prior_result
                    elif 'Initial Case' in covid_result and covid_result['Initial Case'] is None:
                        covid_result['Initial Case'] = '%s' % result['date']
                    if baseline_start_date >= start_date:
                        if isinstance(data_types, (list, tuple)):
                            covid_result["%s" % result['date']] = {
                                k: v for k, v in result.items() if k in ['cases', 'deaths']
                            }
                        else:
                            covid_result["%s" % result['date']] = result.get(data_types, 0)

                    if 'county' in result:
                        if my_county and key[0].lower() == my_county:
                            _1x_growth = (result['cases'] - prior_result['cases'])/24.0
                            my_county_1x_rate["%s" % result['date']] = "%.2f" % _1x_growth
                        prior_result = result
                    baseline_start_date += datetime.timedelta(days=1)
                covid_results.append(covid_result)
    if my_county:
        covid_results.append({k: None for k in covid_results[0].keys()})
        covid_results.append({k: None for k in covid_results[0].keys()})
        covid_results.append({k: k for k in covid_results[0].keys()})
        covid_results.append({k: my_county_1x_rate.get(k) for k in covid_results[0].keys()})
        latest_day = list(covid_results[0].keys())[-1]
        print("\n   %s county latest rate is current %s cases/hour for %s" % (
            my_county, my_county_1x_rate[latest_day], latest_day))
    return covid_results