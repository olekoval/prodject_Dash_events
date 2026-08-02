import dash
from dash import Dash, html, dcc, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go


dash.register_page(__name__, 
                   path='/',
                   title='Головна',
                   name='Головна',
                   order=0)

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

CODE_Q = {
    'Q1': 'Квартал 1',
    'Q2': 'Квартал 2',
    'Q3': 'Квартал 3',
    'Q4': 'Квартал 4',
}
    
def make_card(title, span_id_25, span_id_26):
    return dbc.Card([
        dbc.CardHeader("Кількість унікальних пацієнтів",
                       style={
                           "backgroundColor": "var(--color-accent)",
                           "color": "#FFFFFF",
                       }),
        dbc.CardBody(
            [
                html.H5(title, className="card-title text-center mb-3",
                        style={
                            "minHeight": "2.6em",   # місце під 2 рядки заголовка завжди
                            "display": "flex",
                            "alignItems": "center",  # 1-рядкові заголовки центруються по вертикалі
                            "justifyContent": "center",
                        }),
                        
                dbc.Row([
                    # --- колонка 2025 ---
                    dbc.Col([
                        html.P("2025", className="text-center mb-1 fw-medium",
                               style={"color": "var(--color-text-muted)"}),
                        html.Div(id=span_id_25,
                                 className="fw-bold font-monospace fs-5 text-center",
                                 style={"whiteSpace": "normal"}),
                    ], width=6),
                    # --- колонка 2026 (рівнозначна за розміром і вагою) ---
                    dbc.Col([
                        html.P("2026", className="text-center mb-1 fw-medium",
                               style={"color": "var(--color-accent)"}),
                        html.Div(id=span_id_26,
                                 className="fw-bold font-monospace fs-5 text-center",
                                 style={"whiteSpace": "normal"}),
                    ], width=6),
                ]),
            ],
       )
    ], style={"width": "19rem"},) # ---- закриваємо Card



# -------------- Створюємо метадані картки ------------------------
propetrs_cards = [
    ("Консультування та лікування", "un-patients-c-25", "un-patients-c-26"),
    ("Лабораторна діагностика", "un-patients-l-25", "un-patients-l-26"),
    ("Інструментальна діагностика", "un-patients-i-25", "un-patients-i-26"),
    ("Процедури", "un-patients-p-25", "un-patients-p-26"),
    ("Ургентні стани", "un-patients-e-25", "un-patients-e-26"),
    ("Загалом по пакету", "un-patients-all-25", "un-patients-all-26")
]

# --- Дані для вставку в таблицю -----------
df_q_base = pd.read_parquet(FILE_Q)
df_q_base["name_service"] = df_q_base["first_letter_code"].map(CODE_NAMES)
df_q_base["year"] = df_q_base["year"].astype(str)  # переконуємось, що рік — це рядок для безпечного pivot

# --- Головний макет сторінки home.html -------------------------------
layout =  dbc.Container([
    
        html.H3(["Річна динаміка"], className="mt-4 mb-4 text-center"),
        html.Div([
            dbc.Row(
                [
                    dbc.Col(
                        make_card(*card_data),
                        xs=12, sm=6, lg=4,  # 1 на мобільному, 2 на планшеті, 3 на великому екрані
                        className="d-flex justify-content-center mb-3",
                    )
                    for card_data in propetrs_cards
                ],
                className="g-3 justify-content-center",  # gap між картками + центрування
            ),
        ], style={"maxWidth": "1100px", "margin": "0 auto"}),  # обмежуємо ширину блоку карток
    
html.H3(["Квартальна динаміка"], className="mt-4 mb-4 text-center"),
        html.Div([
            # --- Картка з фільтром (горизонтально, на всю ширину) ---
            dbc.Card([
                dbc.CardHeader("Оберіть квартал для деталізації",
                               style={"backgroundColor": "var(--color-accent)", "color": "#FFFFFF"}),
                dbc.CardBody([
                    # dbc.Label("Оберіть квартал для деталізації",
                    #            className="mb-2"),
                                dbc.RadioItems(
                                    id="radio-input",
                                    className="quarter-filter-group",
                                    inputClassName="btn-check",
                                    labelClassName="quarter-filter-btn",
                                    labelCheckedClassName="active",
                                    options=[
                                        {"label": "Кв1", "value": "Q1"},
                                        {"label": "Кв2", "value": "Q2"},
                                        {"label": "Кв3", "value": "Q3"},
                                        {"label": "Кв4", "value": "Q4"},
                                    ],
                                    value="Q1",
                    ),
                ]),
            ], className="mb-3"),

            # --- Картка з графіком і таблицею поруч ---
            dbc.Card([
                dbc.CardHeader("Результати",
                               style={"backgroundColor": "var(--color-accent)", "color": "#FFFFFF"}),
                dbc.CardBody(
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id="bar-chart-patients")
                        ], xs=12, lg=5),
                        dbc.Col([
                            dbc.Label(id="label_table"),
                            dash_table.DataTable(
                                id="my-dash-table",
                                # css=[{'selector': 'table',
                                #       'rule': 'table-layout: fixed'}],
                                style_cell_conditional=[
                                    {'if': {'column_id': 'Сервіси'},
                                     'textAlign': 'left',
                                     'whiteSpace': 'normal',   # дозволяє перенос рядка
                                     'height': 'auto'},
                                ],
                                style_as_list_view=True,
                                style_header={
                                    'backgroundColor': 'var(--color-accent)',
                                    'color': '#FFFFFF',
                                    'fontWeight': '600',
                                },
                                style_cell={
                                    'fontFamily': 'var(--font-body)',
                                    'padding': '8px 12px',
                                },
                                style_data_conditional=[
                                    # zebra-striping
                                    {'if': {'row_index': 'odd'},
                                     'backgroundColor': 'var(--color-bg)'},
                                    # Δ і Δ% зеленим при зростанні
                                    {'if': {'column_id': 'Δ', 'filter_query': '{Δ} contains "+"'},
                                     'color': 'var(--color-positive)', 'fontWeight': '600'},
                                    {'if': {'column_id': 'Δ %', 'filter_query': '{Δ %} contains "+"'},
                                     'color': 'var(--color-positive)', 'fontWeight': '600'},
                                    # Δ і Δ% теракотовим при спаді
                                    {'if': {'column_id': 'Δ', 'filter_query': '{Δ} contains "-"'},
                                     'color': 'var(--color-negative)', 'fontWeight': '600'},
                                    {'if': {'column_id': 'Δ %', 'filter_query': '{Δ %} contains "-"'},
                                     'color': 'var(--color-negative)', 'fontWeight': '600'},
                                ],
                            ),
                        ], xs=12, lg=7),
                    ]),
                ),
            ]),
        ], style={"maxWidth": "1150px", "margin": "0 auto"}, className="mt-4"),
], fluid=True )

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
    df_service = pd.read_parquet(FILE_SERVICE)
    df_all = pd.read_parquet(FILE_ALL)

    df_un_patient = pd.concat([df_service, df_all], axis=0, ignore_index=True)
    # 1. Перетворюємо датафрейм у словник для швидкого доступу за ключем (year, first_letter_code)
    # Це робиться за один прохід замість 10 окремих фільтрацій
    data_dict = {
        (row["year"], row["first_letter_code"]): row["count_un_patient"] # составний ключ наприклад ('2025', 'L')
        for _, row in df_un_patient.iterrows()
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
            formatted_values.append(f"{val:,d}".replace(",", " "))
            
    return tuple(formatted_values)

@callback(
    Output("bar-chart-patients", "figure"),    
    Input("radio-input", "value")
)
def update_output(selected_quarter):
    df_quarter = df_q_base 
    df_q = df_quarter[df_quarter["quarter"] == selected_quarter]
    
    letter_codes = list(CODE_NAMES.keys())
    
    # Фільтрація по роках з приведенням до стрічки
    df_2025 = df_q[df_q["year"].astype(str) == "2025"]
    df_2026 = df_q[df_q["year"].astype(str) == "2026"]
    
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
        go.Bar(name='2025 рік', x=x_labels_formatted, y=y_2025, marker_color='#0F6E6C'),   # --color-accent
        go.Bar(name='2026 рік', x=x_labels_formatted, y=y_2026, marker_color='#F2994A')    # --color-accent-light
    ])
    
    fig.update_layout(
        barmode='group',
        title=dict(
            text=f"Кількість унікальних пацієнтів за {CODE_Q.get(selected_quarter, "помилковий номер квартала")}",
            font=dict(size=14, color='#6B7280'),  # менш "кричущий" заголовок, --color-text-muted
        ),
        xaxis_title="Сервіси",
        yaxis_title="Кількість пацієнтів",
        font=dict(family="Inter, sans-serif", color='#1F2937'),  # той самий шрифт, що й на сторінці
        template="plotly_white",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#E5E7EB'),  # лише горизонтальні світло-сірі лінії
        margin=dict(l=20, r=20, t=50, b=50),
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="center", x=0.75)
    )

    return fig
               
@callback(
    Output("label_table", "children"), 
    Output("my-dash-table", "data"),     
    Output("my-dash-table", "columns"),  
    Input("radio-input", "value")
)
def service_q(selected_quarter):
    
    # 1. Робимо pivot
    df_pivoted = (
        df_q_base[df_q_base["quarter"] == selected_quarter]
        [["first_letter_code", "name_service", "year", "count_un_patient"]]
        .pivot(
            index=["first_letter_code", "name_service"],
            columns="year",
            values="count_un_patient"
        )
        .reset_index()
    )
    df_pivoted.columns.name = None

    # 2. Гарантуємо, що колонки "2025" та "2026" існують (якщо якоїсь немає — створюємо з null)
    existing_cols = df_pivoted.columns.tolist()

    for yr in ["2025", "2026"]:
        if yr in existing_cols:
            df_pivoted[yr] = df_pivoted[yr].fillna(0)
        else:
            df_pivoted[yr] = 0

    # 3. Продовжуємо обробку
    df_filter_q = (
        df_pivoted[["first_letter_code", "name_service", "2025", "2026"]]
        .sort_values("first_letter_code")
        [["name_service", "2025", "2026"]]
        .rename(columns={"name_service": "Сервіси"})
    )
    df_filter_q["2025"] = df_filter_q["2025"].astype(int)
    df_filter_q["2026"] = df_filter_q["2026"].astype(int)
    df_filter_q["diff"] = df_filter_q["2026"] - df_filter_q["2025"]
    df_filter_q["Δ"] = df_filter_q["diff"].apply(
        lambda d: f"{'+' if d > 0 else ''}{d}"
    )
    df_filter_q["Δ %"] = df_filter_q.apply(
        lambda r: (
            f"{'+' if r['diff'] > 0 else ''}{round((r['2026'] - r['2025']) / r['2025'] * 100, 1)}%"
            if r["2025"] != 0 else "N/A"
        ),
        axis=1
    )
    df_filter_q = df_filter_q.drop(columns=["diff"])

    # 4. Форматуємо числа з розділювачем тисяч (аналогічно до карток)
    rows = df_filter_q.to_dict("records")
    for row in rows:
        row["2025"] = f"{row['2025']:,}".replace(",", " ")
        row["2026"] = f"{row['2026']:,}".replace(",", " ")
        sign = "+" if row["Δ"].startswith("+") else ("-" if row["Δ"].startswith("-") else "")
        digits = row["Δ"].lstrip("+-")
        row["Δ"] = sign + f"{int(digits):,}".replace(",", " ")

    return (
           f"Дані за {CODE_Q.get(selected_quarter, "помилковий номер квартала")} (унікальні пацієнти)",
           rows, 
           [{"name": i, "id": i} for i in df_filter_q.columns]
    )
