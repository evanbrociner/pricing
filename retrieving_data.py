
from geopy.geocoders import Nominatim
from doltpy.cli.read import read_pandas_sql
from doltpy.cli import Dolt, DoltException

import os
import pandas as pd
import sqlite3
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

def hospitals_per_state():
    query = '''SELECT state,COUNT(state) AS sum
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
    result_df= result_df[result_df.columns[~result_df.columns.isin(['longitude', 'latitude'])]]


    result_df.to_csv('data/hospitals.csv', sep=',')
    result_df.to_json('data/hospitals.json')


def average_price_per_code():

    query = '''SELECT code,price
     FROM prices'''

    repo = Dolt(
        '/Users/evan.brociner/Desktop/Job_Hunting_Projects/hospital-price-transparency')

    result_df = read_pandas_sql(repo, query)

#     cpt_codes_interest= [
#
#     '90834','90832','90837','90846','90847','90832','90834','90837',
#      '90846' ,'90847' ,'90853','99203' ,'99204' ,'99205' ,'99243' , '99244' ,
#     '99385' ,'99386' ,'80048' ,'80053' ,'80055' , '80061' ,'80069' ,'80076' ,
#      '81000' ,'81001','81002' ,'81003','84153', '84154' ,'84443' ,'85025' ,
#      '85027' ,'85610' ,'85730' ,'70450','70553' ,'72110' ,'72148' ,'72193' ,
#  '73721', '74177' , '76700' ,'76805' ,'76830' ,'77065' ,'77066' ,'77067' ,
# '216''460' ,'470' ,'473' ,'743' ,'19120' ,'29826' ,'29881' ,'42820' ,'43235' ,
# '43239' ,'45378' ,'45380' ,'45385' ,'45391','47562' ,'49505' ,'55700'  ,
# '55866' ,'59400' ,'59510' ,'59610' ,'62322' ,'62323' ,'64483' ,'66821' ,
# '66984' ,'93000' ,'93452' ,'95810','97110']
    cpt_codes_interest = ['80048', '80053', '80055', '80061', '80069', '80076',
                          '81000', '81001', '81002', '81003', '84153', '84154', '84443', '85025',
                          '85027', '85610', '85730']

    #

    # c.execute('''
    #     SELECT * FROM hospital_per_state
    #               ''')
    #
    #

    df = pd.DataFrame(c.fetchall(), columns=['text', 'number'])
    print(df)

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

    # if not os.path.isfile('data/hospitals_per_state.csv'):
    hospitals_per_state()

    # if not os.path.isfile('data/price_per_hospital.csv'):
    #     price_per_hospital()
    # if not os.path.isfile('data/price_per_hospital.csv'):
    #     price_per_hospital()
