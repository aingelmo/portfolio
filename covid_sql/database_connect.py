#!/usr/bin/python3

import pandas as pd
import requests
from sqlalchemy import create_engine
import os


def downloader():
    r = requests.get(url)

    with open(filename, 'wb') as f:
        f.write(r.content)


def engine_sql():
    df = pd.read_csv(filename)

    engine = create_engine('postgresql://pi:raspberry@localhost:5432/pi')

    df.to_sql('covid_data', engine, if_exists='append', index=False)


if __name__ == '__main__':
    filename = 'owid-covid-data.csv'
    url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'

    downloader()
    engine_sql()
