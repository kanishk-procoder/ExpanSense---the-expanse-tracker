import pandas as pd
from db import get_connection
import streamlit as st

def fetch_table(table_name, user_specific=False, user_column=None):
    conn = get_connection()
    if user_specific and user_column and "user_id" in st.session_state:
        df = pd.read_sql(f"SELECT * FROM {table_name} WHERE {user_column} = ?", conn, params=[st.session_state.user_id])
    else:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

def insert_record(query, values):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, values)
    conn.commit()
    conn.close()
