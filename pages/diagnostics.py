import dash
from dash import html

dash.register_page(__name__,
                   path='/diagnostics',
                   title='Діагностика',
                   name='Діагностика',
                   order=2)

layout = html.Div([
    html.H1("Diagnostics Page"),

])
