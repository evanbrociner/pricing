
from geopy.geocoders import Nominatim
from doltpy.cli.read import read_pandas_sql
from doltpy.cli import Dolt, DoltException

import os
import pandas as pd
import sqlite3
import geopy.distance

from census import Census
from us import states

c = Census("abe3720d8eb4822a29b319de128a64889e61f957")

va_census = c.acs5.state_county_tract(fields = ('NAME', 'C17002_001E', 'C17002_002E', 'C17002_003E', 'B01003_001E'),
                                      state_fips = '*',
                                      county_fips = "*",
                                      tract = "*",
                                      year = 2017)

print(va_census)


conn = sqlite3.connect('pricing_database')
c = conn.cursor()


def get_geo(result_df):

    result_df['combined_address'] = result_df[[
        'street_address', 'city', 'state']].values.tolist()

    result_df['latitude'] = 'NA'
    result_df['longitude'] = 'NA'
    result_df['coordinates'] = 'NA'

    for index in range(len(result_df)):
        try:

            geolocator = Nominatim(user_agent="my_user_agent")
            combined_address = ', '.join(result_df.loc[index]['combined_address'])
            loc = geolocator.geocode(combined_address)

            if loc is None:
                loc = geolocator.geocode(
                    result_df.loc[index]['city'] + ', ' +
                    result_df.loc[index]['state'])

            if hasattr(loc,'latitude'):
                # "coordinates": [ longitude, latitude ]
                result_df.loc[index, 'coordinates'] = [loc.longitude,loc.latitude]
                result_df.loc[index, 'longitude'] = loc.longitude
                result_df.loc[index, 'latitude'] = loc.latitude

        except Exception:
            pass

    return result_df





def close_hospital(df):
    for index_i in range(len(df) ):
        km_distance =[]
        for index_j in range(len(df) ):
            if index_i != index_j:
                loc1 = (df.loc[index_i, 'latitude'],
                       df.loc[index_i, 'longitude'])

                loc2 = (df.loc[index_j, 'latitude'],
                       df.loc[index_j, 'longitude'])
                km_distance.append( geopy.distance.geodesic(loc1, loc2).km)
        df.loc[index_i, 'km_distance'] = min(km_distance)



def hospitals_per_state():
    query = '''
    SELECT state,
    npi_number,
    COUNT(state) AS sum
    FROM hospitals
    GROUP BY state'''

    query = '''SELECT *
    FROM hospitals'''

    repo = Dolt(
        '/Users/evan.brociner/Desktop/Job_Hunting_Projects/hospital-price-transparency')
    result_df = read_pandas_sql(repo, query)

    c.execute(
        'CREATE TABLE IF NOT EXISTS hospital_per_stat (state text, sum number)')
    conn.commit()
    result_df.to_sql('hospital_per_state', conn,
                     if_exists='replace', index=False)

    result_df = get_geo(result_df)
    result_df= result_df[result_df.columns[result_df.columns.isin(['longitude', 'latitude'])]]
    result_df = result_df[result_df.longitude != 'NA']

    print(result_df)
    result_df = result_df.reset_index(drop=True)


    close_hospital(result_df)

    result_df.to_csv('data/hospitals.csv', sep=',')
    result_df.to_json('data/hospitals.json')


def average_price_per_code():

    cpt_codes_interest = ['80048', '80053', '80055', '80061', '80069', '80076',
                          '81000', '81001', '81002', '81003', '84153', '84154', '84443', '85025',
                          '85027', '85610', '85730']

    query = '''
    SELECT *

     FROM prices
     WHERE code IN ('80048', '80053', '80055', '80061', '80069', '80076',
                           '81000', '81001', '81002', '81003', '84153', '84154', '84443', '85025',
                           '85027', '85610', '85730')
     '''

    repo = Dolt(
        '/Users/evan.brociner/Desktop/Job_Hunting_Projects/hospital-price-transparency')

    result_df = read_pandas_sql(repo, query)


    # df = pd.DataFrame(c.fetchall(), columns=['text', 'number'])
    # print(df)

    result_df.to_csv('data/avg_price.csv', sep=',')


def price_per_hospital():

    # need to match codes together to create a far way to mesure the
    #  price data

    query = '''SELECT prices.npi_number,
                        AVG(prices.price),
                        hospitals.name
    FROM prices


     INNER JOIN
            hospitals ON prices.npi_number=hospitals.npi_number
    GROUP BY
             prices.npi_number,
             hospitals.name

             '''
    repo = Dolt(
        '/Users/evan.brociner/Desktop/Job_Hunting_Projects/hospital-price-transparency')

    result_df = read_pandas_sql(repo, query)
    result_df.to_csv('data/price_per_hospital.csv', sep=',')


def price_per_hospital_and_insurance():

    query = '''SELECT AVG(price)
    FROM prices
    GROUP BY code,
            npi_number'''
    repo = Dolt(
        '/Users/evan.brociner/Desktop/Job_Hunting_Projects/hospital-price-transparency')

    result = read_pandas_sql(repo, query)
    print(result)

# The Spearman test


if __name__ == "__main__":

    if not os.path.isfile('data/hospitals.csv'):
        hospitals_per_state()

    if not os.path.isfile('data/price_per_hospital.csv'):
         average_price_per_code()
    # if not os.path.isfile('data/price_per_hospital.csv'):
    #     price_per_hospital()
