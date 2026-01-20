from sqlalchemy import create_engine, text
import pandas as pd
import streamlit as st

@st.cache_data
def fetch_dataframe(query, params=None):
    engine = create_engine(st.secrets["DATABASE_URL"])

    with engine.connect() as conn:
        df = pd.read_sql(
            text(query),   
            conn,
            params=params
        )

    return df
