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
FILE_SERVICE = BASE_PATH / "data" / "gr_services_first_letter_25_26.parquet"
FILE_ALL = BASE_PATH / "data" / "gr_services_all_25_26.parquet"

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
                        ], className="text-primary my-0"),
                     html.P(
                        [
                        "2026: ", 
                        html.Span(id=span_id_26, 
                                  className="fw-bold font-monospace fs-4", # зробити текст жирним
                                  style={"whiteSpace": "pre"} # збереження всіх пробілів
                                 )
                        ], className="text-primary my-0"),
                ]),
            ], # ---- кінець списку CardBody
       ) # ---- закриваємо CardBody
    ) # ---- закриваємо Card


# -------------- Створюємо картки ------------------------
propetrs_cards = [
    ("Консультування та лікування", "un-patients-c-25", "un-patients-c-26"),
    ("Лабораторна діагностика", "un-patients-l-25", "un-patients-l-26"),
    ("Інструментальна діагностика", "un-patients-i-25", "un-patients-i-26"),
    ("Процедури", "un-patients-p-25", "un-patients-p-26"),
    ("Ургентні стани", "un-patients-e-25", "un-patients-e-26"),
    ("Загалом по пакету", "un-patients-all-25", "un-patients-all-26")
]

# --- Головний макет сторінки -------------------------------
layout = html.Div([
    dbc.Container([
        # Перший ряд з 5 картками
        dbc.Row([dbc.Col(make_card(*card_data)) for card_data in propetrs_cards]),
        # Другий ряд
        dbc.Row(
            [
                dbc.Col(dbc.Card(dbc.CardBody("Графік 1")), width=6),
                dbc.Col(dbc.Card(dbc.CardBody("Графік 2")), width=6),
            ],
        ),
             
        # Третій ряд
        dbc.Row(
            [
                dbc.Col(dbc.Card(dbc.CardBody("Графік 3")), width=6), 
                dbc.Col(dbc.Card(dbc.CardBody("Графік 4")), width=6),
            ]
        )
    ], fluid=True)
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
    Output("un-patients-all-25", "children"),
    Output("un-patients-all-26", "children"),
    
    Input("un-patients-c-25", "id")
)
def load_all_cards_data(init_id):
    df_service = pl.read_parquet(FILE_SERVICE)
    df_all = pl.read_parquet(FILE_ALL)

    df_un_patient = pl.concat([df_service, df_all], how="vertical")
    # 1. Перетворюємо датафрейм у словник для швидкого доступу за ключем (year, first_letter_code)
    # Це робиться за один прохід замість 10 окремих фільтрацій
    data_dict = {
        (row["year"], row["first_letter_code"]): row["count_un_patient"] # составний ключ наприклад ('2025', 'L')
        for row in df_un_patient.iter_rows(named=True)
    }
    
    # Послідовність кодів, яка відповідає порядку Output у декораторі
    letter_codes = ['C', 'L', 'I', 'P', 'E', 'ALL']
    years = ['2025', '2026']
    
    formatted_values = []
    
    # 2. Проходимо по кодах та роках у правильному порядку
    for code in letter_codes:
        for year in years:
            # Беремо значення зі словника (0, якщо раптом комбінації немає в даних)
            val = data_dict.get((year, code), 0)
            # Форматуємо число із вирівнюванням та розділювачем тисяч
            formatted_values.append(f"{val:>10,d}".replace(",", " "))
            
    return tuple(formatted_values)
