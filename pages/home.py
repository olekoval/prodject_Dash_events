import dash
from dash import Dash, html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import polars as pl
from pathlib import Path
import plotly.graph_objects as go


dash.register_page(__name__, 
                   path='/',
                   title='Головна',
                   name='Головна')

BASE_PATH = Path(__file__).resolve().parents[1]
FILE_SERVICE = BASE_PATH / "data" / "gr_services_first_letter_25_26.parquet"
FILE_ALL = BASE_PATH / "data" / "gr_services_all_25_26.parquet"
FILE_Q = BASE_PATH / "data" / "gr_services_Q_25_26.parquet"

CODE_NAMES = {
    'C': 'Консультування та лікування',
    'L': 'Лабораторна діагностика',
    'I': 'Інструментальна діагностика',
    'P': 'Процедури',
    'E': 'Ургентні стани'
}

def make_card(title, span_id_25, span_id_26):
    return dbc.Card([
        dbc.CardHeader("Кількість унікальних пацієнтів"),
        dbc.CardBody(
            [
                html.Div([
                    html.H5(title, className="card-title text-center"),
                 #   html.P("Кількість унікальних пацієнтів", className="card-text",),
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
            className="d-flex flex-column justify-content-between"
            # style={
            #         "display": "flex",
            #         "flexDirection": "column",
            #         "justify-content": "space-between",
            #     }
       ) # ---- тут закривається дужка CardBody (перший позиційний аргумент для Card)
    ], style={"width": "16rem"},) # ---- закриваємо Card


# -------------- Створюємо картки ------------------------
propetrs_cards = [
    ("Консультування та лікування", "un-patients-c-25", "un-patients-c-26"),
    ("Лабораторна діагностика", "un-patients-l-25", "un-patients-l-26"),
    ("Інструментальна діагностика", "un-patients-i-25", "un-patients-i-26"),
    ("Процедури", "un-patients-p-25", "un-patients-p-26"),
    ("Ургентні стани", "un-patients-e-25", "un-patients-e-26"),
    ("Загалом по пакету", "un-patients-all-25", "un-patients-all-26")
]

# --- Головний макет сторінки home.html -------------------------------
layout =  dbc.Container([
        html.Div([make_card(*card_data) for card_data in propetrs_cards], # Картки
                style={
                    "display": "flex",
                    "justify-content": "center",
                    "flex-wrap": "wrap",
                    "gap": "15px",
                }
                ),
     
        dbc.Row(
            [
                dbc.Col([
                dbc.Label("Вибіріть квартал"),
                dbc.RadioItems(
                    options=[
                        {"label": "Кв1", "value": "Q1"},
                        {"label": "Кв2", "value": "Q2"},
                        {"label": "Кв3", "value": "Q3"},
                        {"label": "Кв4", "value": "Q4"},
                    ],
                    value="Q1",
                    id="radio-input",
                    switch=True,
                  )
                ], xs=12, sm=12, md=4, lg=2),
                dbc.Col([
                    dcc.Graph(id="bar-chart-patients")
                    ], xs=12, sm=12, md=8, lg=5),
            ], className="mt-4"
        ),]
            , fluid=True )



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

@callback(
    Output("bar-chart-patients", "figure"),    
    Input("radio-input", "value")
)
def update_output(selected_quarter):
    df_quarter = pl.read_parquet(FILE_Q)
    df_q = df_quarter.filter(pl.col("quarter") == selected_quarter)
    
    letter_codes = list(CODE_NAMES.keys())
    
    # Фільтрація по роках з приведенням до стрічки
    df_2025 = df_q.filter(pl.col("year").cast(pl.Utf8) == "2025")
    df_2026 = df_q.filter(pl.col("year").cast(pl.Utf8) == "2026")
    
    # Словники для швидкого пошуку значень
    dict_2025 = dict(zip(df_2025["first_letter_code"], df_2025["count_un_patient"]))
    dict_2026 = dict(zip(df_2026["first_letter_code"], df_2026["count_un_patient"]))
    
    # Формуємо значення Y
    y_2025 = [dict_2025.get(code, 0) for code in letter_codes]
    y_2026 = [dict_2026.get(code, 0) for code in letter_codes]
    
    # Підписи для осі X (повна назва послуги)
    x_labels = [CODE_NAMES[code] for code in letter_codes]
    
    # Якщо назви занадто довгі, додаємо <br> для переносу рядків у підписах Plotly
    x_labels_formatted = [label.replace(" ", "<br>", 1) if " " in label else label for label in x_labels]
    
    fig = go.Figure(data=[
        go.Bar(name='2025 рік', x=x_labels_formatted, y=y_2025, marker_color='#0d6efd'),
        go.Bar(name='2026 рік', x=x_labels_formatted, y=y_2026, marker_color='#0dcaf0')
    ])
    
    fig.update_layout(
        barmode='group',
        title=f"Кількість унікальних пацієнтів за {selected_quarter}",
        xaxis_title="Сервіси",
        yaxis_title="Кількість пацієнтів",
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=50),
        legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5)
    )

    return fig
               
