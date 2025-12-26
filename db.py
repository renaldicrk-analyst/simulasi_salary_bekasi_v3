# db.py

import psycopg2
import pandas as pd
from config import DB_CONFIG

def fetch_dataframe(query, params):
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df
