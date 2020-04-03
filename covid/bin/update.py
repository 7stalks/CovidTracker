import csv
import datetime
import json
import sys

try:
    from ..tracker import get_county_census_data, get_covid_data, get_combined_row_data
except ImportError:
    from covid.tracker import get_county_census_data, get_covid_data, get_combined_row_data

def main():

    start_date = datetime.date(2020,3, 10)
    data_type = 'cases'

    areas = [
        {'state': 'arizona'},
        {'county': 'new york city'},
        {'county': 'los angeles'},
        {'county': 'snohomish'}
    ]

    results = []
    for area in areas:
        results += get_combined_row_data(start_date=start_date, data_types=data_type, **area)

    output = 'covid_info.csv'
    with open(output, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=results[0].keys())
        writer.writeheader()
        for row in results:
            writer.writerow(row)


if __name__ == '__main__':
    sys.exit(main())