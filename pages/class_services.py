import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

dash.register_page(__name__,
                   path='/class_services',
                   title='Класи сервісів',
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

    # 2. Відбір топ-позицій (>= threshold)
    top = (
        df_grouped
        .sort_values("count_pos", ascending=False)
        .assign(share=lambda d: d["count_pos"] / total)
        .loc[lambda d: d["share"] >= threshold, ["service_number", "name_class", "count_pos"]]
    )
    
    # 3. Обчислення суми для "Інше" (< threshold)
    other_sum = (
        df_grouped
        .loc[(df_grouped["count_pos"] / total) < threshold, "count_pos"]
        .sum()
    )
    
    # 4. Якщо є позиції, що потрапили в "Інше", додаємо їх рядочком у кінець
    if other_sum is not None and other_sum > 0:
        other_df = pd.DataFrame({
            "service_number": ["Інше"],
            "name_class": ["Інше"],
            "count_pos": [other_sum]
        })
        return pd.concat([top, other_df], ignore_index=True)
        
    return top
# -----------------------------------------------------------------
layout = dbc.Container([
    html.H3("Класи сервіси Консультування та лікування"),
    dbc.Card([
        dbc.CardHeader("abc"),
        dbc.CardBody(
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="bar-chart-h-25")
                ], xs=12, lg=6),
                dbc.Col([
                    dcc.Graph(id="bar-chart-h-26")
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
    top_2026 = process_top_services(df, year="2026")
 
    fig_25 = go.Figure(go.Bar(
        x=top_2025['count_pos'].tolist(),
        y=top_2025['name_class'].tolist(),
        orientation='h',
        # text=percents,
        # textposition='outside',
        ))
        
    fig_26 = go.Figure(go.Bar(
        x=top_2026['count_pos'].tolist(),
        y=top_2026['name_class'].tolist(),
        orientation='h',
        # text=percents,
        # textposition='outside',
        ))
    
    return fig_25, fig_26
