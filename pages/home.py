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


def make_card(title, span_id_25, span_id_26):
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div([
                    html.H4(title, className="card-title"),
                    html.P("Кількість унікальних пацієнтів", className="card-text",),
                ]),
                html.Div([
                    html.P(
                        [
                        "2025: ", 
                        html.Span(id=span_id_25, 
                                  className="fw-bold font-monospace fs-4", # зробити текст жирним
                                  style={"whiteSpace": "pre"} # збереження всіх пробілів
                                 )
                        ], className="card-text text-primary my-2"),
                     html.P(
                        [
                        "2026: ", 
                        html.Span(id=span_id_26, 
                                  className="fw-bold font-monospace fs-4", # зробити текст жирним
                                  style={"whiteSpace": "pre"} # збереження всіх пробілів
                                 )
                        ], className="card-text text-primary my-2"),
                ]),
            ], # ---- кінець списку CardBody
       ) # ---- закриваємо CardBody
    ) # ---- закриваємо Card
        
# 1. -------------- Створюємо картки ------------------------
card_C = make_card("Консультування та лікування", "un-patients-c-25", "un-patients-c-26")
card_L = make_card("Лабораторна діагностика", "un-patients-l-25", "un-patients-l-26")
card_I = make_card("Інструментальна діагностика", "un-patients-i-25", "un-patients-i-26")
card_P = make_card("Процедури", "un-patients-p-25", "un-patients-p-26")
card_E = make_card("Ургентні стани", "un-patients-e-25", "un-patients-e-26")

cards = dbc.Row(
    [
        dbc.Col(card_C), 
        dbc.Col(card_L),
        dbc.Col(card_I),
        dbc.Col(card_P),
        dbc.Col(card_E),
    ]
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
    Output("un-patients-l-25", "children"),
    Output("un-patients-l-26", "children"),
    Output("un-patients-i-25", "children"),
    Output("un-patients-i-26", "children"),
    Output("un-patients-p-25", "children"),
    Output("un-patients-p-26", "children"),
    Output("un-patients-e-25", "children"),
    Output("un-patients-e-26", "children"),
    
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
    l_25 = (df_service
            .filter((pl.col('year') == '2025') & (pl.col('first_letter_code') == 'L'))
            .select('count_un_patient')
            .item())
    l_26 = (df_service
            .filter((pl.col('year') == '2026') & (pl.col('first_letter_code') == 'L'))
            .select('count_un_patient')
            .item())
    i_25 = (df_service
            .filter((pl.col('year') == '2025') & (pl.col('first_letter_code') == 'I'))
            .select('count_un_patient')
            .item())
    i_26 = (df_service
            .filter((pl.col('year') == '2026') & (pl.col('first_letter_code') == 'I'))
            .select('count_un_patient')
            .item())
    p_25 = (df_service
            .filter((pl.col('year') == '2025') & (pl.col('first_letter_code') == 'P'))
            .select('count_un_patient')
            .item())
    p_26 = (df_service
            .filter((pl.col('year') == '2026') & (pl.col('first_letter_code') == 'P'))
            .select('count_un_patient')
            .item())
    e_25 = (df_service
            .filter((pl.col('year') == '2025') & (pl.col('first_letter_code') == 'E'))
            .select('count_un_patient')
            .item())
    e_26 = (df_service
            .filter((pl.col('year') == '2026') & (pl.col('first_letter_code') == 'E'))
            .select('count_un_patient')
            .item())
    
    val_c_25 = f"{c_25:>10,d}".replace(",", " ")
    val_c_26 = f"{c_26:>10,d}".replace(",", " ")
    val_l_25 = f"{l_25:>10,d}".replace(",", " ")
    val_l_26 = f"{l_26:>10,d}".replace(",", " ")
    val_i_25 = f"{i_25:>10,d}".replace(",", " ")
    val_i_26 = f"{i_26:>10,d}".replace(",", " ")
    val_p_25 = f"{p_25:>10,d}".replace(",", " ")
    val_p_26 = f"{p_26:>10,d}".replace(",", " ")
    val_e_25 = f"{e_25:>10,d}".replace(",", " ")
    val_e_26 = f"{e_26:>10,d}".replace(",", " ")
    
    return (
        val_c_25, val_c_26, 
        val_l_25, val_l_26, 
        val_i_25, val_i_26, 
        val_p_25, val_p_26, 
        val_e_25, val_e_26
    )
