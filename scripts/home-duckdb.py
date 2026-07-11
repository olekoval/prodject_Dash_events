import dash
from dash import dcc, html, Input, Output, callback
from dotenv import load_dotenv
import duckdb
import os
import dash_ag_grid as dag

# Реєстрація головної сторінки
dash.register_page(__name__, path='/home-duckdb')

load_dotenv()

ACCESS_KEY_ID = os.getenv("CF_ACCESS_KEY_ID", "").strip()
SECRET_ACCESS_KEY = os.getenv("CF_SECRET_ACCESS_KEY", "").strip()
BUCKET_NAME = os.getenv("CF_BUCKET_NAME", "").strip()
ENDPOINT_URL = os.getenv("CF_ENDPOINT_URL", "").strip()


def create_connection():
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute(f"""
        SET s3_endpoint='{ENDPOINT_URL.replace("https://", "")}';
        SET s3_access_key_id='{ACCESS_KEY_ID}';
        SET s3_secret_access_key='{SECRET_ACCESS_KEY}';
        SET s3_url_style='path';
        SET s3_use_ssl=true;
        SET s3_region='auto';
    """)
    return con


def get_data():
    con = create_connection()
    query = f"""
        SELECT
            year,
            service, 
            COUNT(DISTINCT patient_id) AS un_patient_id,
            SUM(count_service) AS count_service
        FROM read_parquet(
         --   's3://{BUCKET_NAME}/treatments/**/*.parquet',
         's3://{BUCKET_NAME}/treatments/year=2025/service=C/**/*.parquet',
            hive_partitioning = true
        )
      --  WHERE year = '2025'
        GROUP BY year, service
    """
    return con.execute(query).df()

def layout():
    return html.Div([
        html.H2("Ласкаво просимо до аналітичного центру!"),
        html.P("Оберіть потрібний звіт із списку нижче:"),
        dcc.Loading(html.Div(id="grid-container"))
    ])

@callback(
    Output("grid-container", "children"),
    Input("grid-container", "id")
)
def load_grid(_):
    df = get_data()
    columnDefs = [{'field': i} for i in df.columns]
    grid = dag.AgGrid(
        id="get-started-example",
        rowData=df.to_dict("records"),
        columnDefs=columnDefs,
    )
    return grid
