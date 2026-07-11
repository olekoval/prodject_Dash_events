import dash
from dash import dcc, html, Input, Output, callback
from dotenv import load_dotenv
import polars as pl
import os
import dash_ag_grid as dag

# Реєстрація головної сторінки
dash.register_page(__name__, path='/')

load_dotenv()

ACCESS_KEY_ID = os.getenv("CF_ACCESS_KEY_ID", "").strip()
SECRET_ACCESS_KEY = os.getenv("CF_SECRET_ACCESS_KEY", "").strip()
BUCKET_NAME = os.getenv("CF_BUCKET_NAME", "").strip()
ENDPOINT_URL = os.getenv("CF_ENDPOINT_URL", "").strip()


def get_storage_options():
    return {
        "aws_access_key_id": ACCESS_KEY_ID,
        "aws_secret_access_key": SECRET_ACCESS_KEY,
        "aws_endpoint_url": ENDPOINT_URL,
        "aws_region": "auto",
        # для деяких S3-сумісних сховищ (у т.ч. R2) потрібен virtual-hosted-style off
        "aws_virtual_hosted_style_request": "false",
    }


def get_data():
    path = f"s3://{BUCKET_NAME}/treatments/year=2025/service=C/**/*.parquet"
    # path = f"s3://{BUCKET_NAME}/treatments/**/*.parquet"

    lf = pl.scan_parquet(
        path,
        hive_partitioning=True,
        storage_options=get_storage_options(),
    )

    df = (
        lf.group_by(["year", "service"])
        .agg([
            pl.col("patient_id").n_unique().alias("un_patient_id"),
            pl.col("count_service").sum().alias("count_service"),
        ])
        .collect()
    )
    return df.to_pandas()


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
