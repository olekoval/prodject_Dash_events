import dash
from dash import Dash, html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import polars as pl
from pathlib import Path


dash.register_page(__name__, 
                   path='/',
                   title='Головна',
                   name='Головна')


BASE_PATH = Path(__file__).resolve().parents[1]
file_name = BASE_PATH / "data" / "gr_services_first_letter_25_26.parquet"
df_service = pl.read_parquet(file_name)


# 1. Створюємо картки
card_C = dbc.Card(dbc.CardBody(
    [
        html.H4("Консультування та лікування", className="card-title"),
        html.P(
            "Кількість унікальних пацієнтів які отримували "
            "послугу в розрізі року"
        ),
        html.H4([
            "2025: ", 
            html.Span(id="un-patients-c-25", className="fw-bold")
        ], className="text-primary my-2"),
        html.H4([
            "2026: ", 
            html.Span(id="un-patients-c-26", className="fw-bold")
        ], className="text-primary my-2"),
    ]
))

card_L = dbc.Card(dbc.CardBody("Вміст картки L"))
card_I = dbc.Card(dbc.CardBody("Вміст картки I"))
card_P = dbc.Card(dbc.CardBody("Вміст картки P"))
card_E = dbc.Card(dbc.CardBody("Вміст картки e"))

cards = dbc.Row(
    [
        dbc.Col(card_C),
        dbc.Col(card_L),
        dbc.Col(card_I),
        dbc.Col(card_P),
        dbc.Col(card_E),
    ], 
    className="row-cols-1 row-cols-md-5 g-3 mb-3" 
)

# 3. Головний макет сторінки
layout = html.Div([
    dbc.Container([
        # Перший ряд з 5 картками
        cards,
        
        # Другий ряд
        dbc.Row(
            [
                dbc.Col(dbc.Card(dbc.CardBody("Графік 1")), width=6),
                dbc.Col(dbc.Card(dbc.CardBody("Графік 2")), width=6),
            ],
            className="mb-3"
        ),
             
        # Третій ряд
        dbc.Row(
            [
                dbc.Col(dbc.Card(dbc.CardBody("Графік 3")), width=6), 
                dbc.Col(dbc.Card(dbc.CardBody("Графік 4")), width=6),
            ]
        )
    ], fluid=True) # Розтягує контейнер на всю ширину екрану
])


@callback(
    Output("un-patients-c-25", "children"),
    Output("un-patients-c-26", "children"),
    
    Input("un-patients-c-25", "id")
)
def load_all_cards_data(init_id):
    c_25 = (df_service
            .filter((pl.col('year') == '2025') & (pl.col('first_letter_code') == 'C'))
            .select('count_un_patient')
            .item())
    c_26 = (df_service
            .filter((pl.col('year') == '2026') & (pl.col('first_letter_code') == 'C'))
            .select('count_un_patient')
            .item())
    
    val_c_25 = f"{c_25:,}".replace(",", " ")
    val_c_26 = f"{c_26:,}".replace(",", " ")
    
    return val_c_25, val_c_26














