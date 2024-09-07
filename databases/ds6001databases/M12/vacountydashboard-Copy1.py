import numpy as np
import pandas as pd
import requests
import json
import plotly.express as px
import plotly.figure_factory as ff
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Inititalize the dashborad
app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

# Populate the dashborad
app.layout = html.Div(
    [
        html.H1("Virginia County Cost and Standard Living Dashboard")
    ]    
)

# Run the dashboard
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)