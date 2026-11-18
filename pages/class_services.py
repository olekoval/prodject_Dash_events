import dash
from dash import html, dcc, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

dash.register_page(__name__,
                   path='/class_services',
                   title='Класи сервіса Консультування/лікування',
                   name='Консультування/лікування',
                   order=1)

BASE_PATH = Path(__file__).resolve().parents[1]
FILE_CLAS = BASE_PATH / "data" / "gr_class_month_25_26.parquet"
df = pd.read_parquet(FILE_CLAS)

def process_top_services(df: pd.DataFrame, 
                             year: str, 
                             month_range: list,
                             threshold: float = 0.01) -> pd.DataFrame:
    """
    Фільтрує дані за роком та кодом 'C', обчислює топ-позиції (>= threshold)
    та згруповує решту в категорію 'Інше'. 
    threshold - частка для визначення топ
    """
    # 1. Початкова фільтрація та групування за вказаний рік
    df_grouped = (
        df[
            (df["year"] == year) &
            (df["report_month"].between(month_range[0], month_range[1])) &
            (df["service_number"].str.upper().str.startswith("C"))
        ]
        .groupby(["service_number", "name_class"], as_index=False)
        .agg(count_pos=("count_posluha", "sum"))
    )
    
    total = df_grouped["count_pos"].sum()

    # 2. Відбір топ-позицій (>= threshold) та розрахунок суми кількості послуг по класам (< threshold) 
    df_share = df_grouped.copy()
    df_share['share'] = df_share['count_pos'] / total # визначаєм частку в total
    # топ-позицій
    top = (
            df_share[df_share['share'] >= threshold]
           .sort_values('share')
           .drop(columns='share')
           )
    # розрахунок суми кількості послуг по класам (< threshold)
    other_sum = (
        df_share[df_share['share'] < threshold]
        ['count_pos'].sum()
           )
    
    # 3. Якщо є позиції, що потрапили в "Інше", додаємо їх рядочком у кінець
    if other_sum is not None and other_sum > 0:
        other_df = pd.DataFrame({
            "service_number": ["Інше"],
            "name_class": ["Інше"],
            "count_pos": [other_sum]
        })
        
        return pd.concat([other_df, top], ignore_index=True)       
    return top

def truncate_labels(labels, max_len=16, show_tooltip=True):
    """
    Обрізає довгі рядки до max_len символів і додає '...'
    
    Args:
        labels: список рядків для обрізання
        max_len: максимальна довжина рядка (за замовчуванням 16)
        show_tooltip: якщо True, додає повну назву в hovertext (за замовчуванням True)
    """
    truncated = []
    for label in labels:
        if len(label) <= max_len:
            truncated.append(label)
        else:
            truncated.append(label[:max_len] + '...')
    return truncated

# -------------- Обробка даних до таблиці ---------------------------------
def data_table(df: pd.DataFrame, month_range: list) -> pd.DataFrame:
    df_filtered = df[
        (df["report_month"].between(month_range[0], month_range[1])) &
        (df["service_number"].str.upper().str.startswith("C"))
    ]

    df_pivot = (
            df_filtered.groupby(['year', 'name_class'])
            .agg(sum_count_posluha=('count_posluha', 'sum'))
            .reset_index()
            .pivot(index='name_class', columns='year', values='sum_count_posluha')
            .fillna(0)
            .reset_index()  
        )
        
    # Заповнюємо можливі NaN (якщо в якомусь році не було послуги) на 0
     # df_pivot = df_pivot.fillna(0)
# Додати розрахунок змін у значеннях по роках 
    # df_pivot = df_pivot.rename(columns={
    #     'name_class': 'Назва класу',
    #     '2025': '2025 рік',
    #     '2026': '2026 рік'
    # })

    return df_pivot
# -----------------------------------------------------------------
layout = dbc.Container([
    html.H3("Класи сервіса Консультування та лікування"),
   dbc.Card([
    dbc.CardHeader([html.H5("Виберіть діапазон місяців")]),
    dbc.CardBody([
        dcc.RangeSlider(
            min=1, 
            max=12, 
            step=1, 
            marks={
                1: 'Січ',
                2: 'Лют',
                3: 'Бер',
                4: 'Квіт',
                5: 'Трав',
                6: 'Черв',
                7: 'Лип',
                8: 'Серп',
                9: 'Вер',
                10: 'Жовт',
                11: 'Лист',
                12: 'Груд'
            }, 
            value=[1, 3], 
            allowCross=False, 
            className='mb-4',
            id='month-range'
        )
    ])
], className='mb-4'),
    dbc.Card([
     #   dbc.CardHeader(""),
        dbc.CardBody([          
            dbc.Row([
                
                dbc.Col([
                    dcc.Graph(id="bar-chart-h-25",
                             style={'width': '100%', 'height': '550px'})
                ], xs=12, lg=6),
                
                dbc.Col([
                    dcc.Graph(id="bar-chart-h-26",
                             style={'width': '100%', 'height': '550px'})
                ], xs=12, lg=6),
                
            ])
        ])
    ])
])

@callback(
    Output("bar-chart-h-25", "figure"),
    Output("bar-chart-h-26", "figure"),
    Input("month-range", "value")
)
def top_class(month_range):
    # Визначення кольорів стовпців
    color_all = '#0F6E6C'
    color_last = '#F2994A'

    # --- Виклик функції process_top_services для 2025 ---
    top_2025 = process_top_services(df, year="2025", month_range=month_range)
    total_2025 = top_2025['count_pos'].sum()
    percents_25 = (top_2025['count_pos'] / total_2025 * 100).round(1).astype(str) + '%'
    percent_values_25 = (top_2025['count_pos'] / total_2025).round(2)  # зберігаємо числові значення
    # Обрізаємо довгі назви
    labels_25 = truncate_labels(top_2025['name_class'].tolist())
    # Визначаємо позицію тексту для кожного стовпчика
    textposition_25 = ['inside' if val >= 0.1 else 'outside' for val in percent_values_25]   
    n_25 = top_2025.shape[0]
    color_list_25 = [color_last] + [color_all] * (n_25 - 1)

    # --- Виклик функції process_top_services для 2026 ---
    top_2026 = process_top_services(df, year="2026", month_range=month_range)
    total_2026 = top_2026['count_pos'].sum()
    percents_26 = (top_2026['count_pos'] / total_2026 * 100).round(1).astype(str) + '%'
    percent_values_26 = (top_2026['count_pos'] / total_2026).round(2)
    # Обрізаємо довгі назви
    labels_26 = truncate_labels(top_2026['name_class'].tolist())
    # Визначаємо позицію тексту для кожного стовпчика
    textposition_26 = ['inside' if val >= 0.1 else 'outside' for val in percent_values_26]
    n_26 = top_2026.shape[0]
    color_list_26 = [color_last] + [color_all] * (n_26 - 1)
 
    fig_25 = go.Figure(go.Bar(
        x=top_2025['count_pos'].tolist(),
        y=labels_25,
        orientation='h',
        text=percents_25,
        textposition=textposition_25,
        marker=dict(color=color_list_25)
        ))
        
    fig_26 = go.Figure(go.Bar(
        x=top_2026['count_pos'].tolist(),
        y=labels_26,
        orientation='h',
        text=percents_26,
        textposition=textposition_26,
        marker=dict(color=color_list_26)
        ))

     # Налаштування відступів та масштабування
    fig_25.update_layout(
        title="2025 рік", title_x=0.5,
        margin=dict(l=150, r=30, t=30, b=50),
        xaxis=dict(
            autorange=True,
            automargin=True,  # автоматичний відступ для підписів
            tickformat='_d',  # форматування чисел
        ),
        yaxis=dict(
            automargin=True,  # автоматичний відступ для підписів
        ),
        bargap=0.1,  # трохи зменшуємо проміжок між стовпчиками
    )
    
    fig_26.update_layout(
        title="2026 рік", title_x=0.5,
        margin=dict(l=150, r=30, t=30, b=50),
        xaxis=dict(
            autorange=True,
            automargin=True,
            tickformat='_d',
        ),
        yaxis=dict(
            automargin=True,
        ),
        bargap=0.1,
    )

    # ----------- код для створення таблиці --------------------

    
    
    return fig_25, fig_26
