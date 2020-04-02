import datetime
import sys

try:
    from ..tracker import get_county_census_data, get_covid_data, get_combined_row_data
except ImportError:
    from covid.tracker import get_county_census_data, get_covid_data, get_combined_row_data

def main():

    county_data = get_county_census_data()
    covid_data = get_covid_data()

    # print(county_data[('maricopa', 'arizona')])
    # print(covid_data[('maricopa', 'arizona')][-1])

    results = get_combined_row_data(start_date=datetime.date(2020,3, 15), state='arizona')
    print(results)


    # url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
    # data = requests.get(url).content.decode('utf-8')
    #
    # result = defaultdict(defaultdict)
    # az_counties, others = set(), set()
    # first_date = None
    # for item in data.split("\n")[1:]:
    #     try:
    #         _date, county, state, fips, cases, deaths = item.split(",")
    #     except ValueError:
    #         pass
    #     else:
    #         _date = datetime.date(int(_date.split("-")[0]), int(_date.split("-")[1]),
    #                               int(_date.split("-")[2]))
    #         if state == "Arizona" or county in ["New York City", "Snohomish", "Los Angeles"]:
    #             if first_date is None:
    #                 first_date = _date
    #             az_counties.add(county) if state == "Arizona" else others.add("%s, %s" % (county, state))
    #             result[_date][county] = {'date': _date, 'county': county,
    #                                      'fips': fips, 'cases': int(cases), 'deaths': int(deaths)}
    #
    # _cases_dates, _death_dates = [''], ['None']
    # current_date = first_date
    # while current_date != datetime.date.today():
    #     _cases_dates.append("%s" % current_date)
    #     _death_dates.append("%s" % current_date)
    #     current_date += datetime.timedelta(days=1)
    #
    # cases = [_cases_dates]
    # deaths = [_death_dates]
    # for county in sorted(az_counties) + sorted(others):
    #     current_date = first_date
    #     county_case_line = [county]
    #     county_death_line = [county]
    #     prior_case, prior_death = 0, 0
    #     while current_date != datetime.date.today():
    #         county_case = result[current_date].get(county, {}).get('cases', prior_case)
    #         county_death = result[current_date].get(county, {}).get('deaths', prior_death)
    #         county_case_line.append(county_case)
    #         county_death_line.append(county_death)
    #         prior_case = county_case
    #         prior_death = county_death
    #         current_date += datetime.timedelta(days=1)
    #     cases.append(county_case_line)
    #     deaths.append(county_death_line)
    #
    # for line in cases:
    #     print("\t".join([str(x) for x in line]))
    # print(cases)


if __name__ == '__main__':
    sys.exit(main())