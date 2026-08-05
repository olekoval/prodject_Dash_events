import dash
from dash import html, dcc, callback, Input, Output
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

def process_top_services(df: pd.DataFrame, 
                             year: str, 
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
        max_len: максимальна довжина рядка (за замовчуванням 18)
        show_tooltip: якщо True, додає повну назву в hovertext (за замовчуванням True)
    """
    truncated = []
    for label in labels:
        if len(label) <= max_len:
            truncated.append(label)
        else:
            truncated.append(label[:max_len] + '...')
    return truncated
# -----------------------------------------------------------------
layout = dbc.Container([
    html.H3("Класи сервіса Консультування та лікування"),
    dbc.Card([
     #   dbc.CardHeader(""),
        dbc.CardBody(
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
        )
    ])
])

@callback(
    Output("bar-chart-h-25", "figure"),
    Output("bar-chart-h-26", "figure"),
    Input("bar-chart-h-25", "id")
)
def top_class(_):
    df = pd.read_parquet(FILE_CLAS)
    # --- Виклик функції для 2025 та 2026 років ---
    top_2025 = process_top_services(df, year="2025")
    total_2025 = top_2025['count_pos'].sum()
    percents_25 = (top_2025['count_pos'] / total_2025 * 100).round(1).astype(str) + '%'
    percent_values_25 = (top_2025['count_pos'] / total_2025).round(2)  # зберігаємо числові значення
    # Обрізаємо довгі назви
    labels_25 = truncate_labels(top_2025['name_class'].tolist())
    # Визначаємо позицію тексту для кожного стовпчика
    textposition_25 = ['inside' if val >= 0.1 else 'outside' for val in percent_values_25]
    # Визначення кольорів стовпців
    color_all = '#0F6E6C'
    color_last = '#F2994A'
    
    n_25 = top_2025.shape[0]
    color_list_25 = [color_last] + [color_all] * (n_25 - 1)
    
    top_2026 = process_top_services(df, year="2026")
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
    
    return fig_25, fig_26
