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

# Our data
vacounties = pd.read_csv('vacounties.csv')
url = 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json'
r = requests.get(url)
counties = json.loads(r.text) # geo json
vacounties['county'] = [x.endswith('County') for x in vacounties['Jurisdiction']]
replace_map = {True: 'Counties',
              False: 'Cities'}
vacounties['county'] = vacounties['county'].replace(replace_map)

# Inititalize the dashborad
app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

# Populate the dashborad
app.layout = html.Div(
    [
        html.H1("Virginia County Cost and Standard Living Dashboard"),
        dcc.Tabs(
            [dcc.Tab(label = 'Statewide Data', children = [
                # Statewid graphs here
                dcc.Markdown('Please select a variable:'),
                dcc.Dropdown(id ='varselect',
                             options = vacounties.columns,
                             value = 'Average Annual Pay'), # Step 1: user input
                html.Div([
                    dcc.Graph(id='map'), # Step 5: display the output
                    dcc.Graph(id='box')
                ], style = {'width': '68%', 'float': 'right'}),
                html.Div([
                    dcc.Graph(id='toptable')
                ], style = {'width': '28%', 'float': 'left'}),
            ]),
            dcc.Tab(label = 'Data Relationships', children = [
                # scatterplot here
                html.Div([
                    html.Div([
                    dcc.Markdown('Select a variable for the x-axis'),
                    dcc.Dropdown(id = 'varselectx',
                                 options = vacounties.columns,
                                 value = 'Average Annual Pay')
                ], style={'width': '48%', 'float': 'left'}), # dropdown 1
                html.Div([
                    dcc.Markdown('Select a variable for the y-axis'),
                    dcc.Dropdown(id = 'varselecty',
                                 options = vacounties.columns,
                                 value = 'Cost of living')
                ], style={'width': '48%', 'float': 'right'}), # dropdown 2
                ]),
                html.Div([
                    dcc.Graph(id='scatter') # figure
                ], style={'width': '100%', 'float': 'left'})
            ]),
            dcc.Tab(label = 'Data for One Locality', children = [
                # one county data here
            ])]
        )
    ]    
)

@app.callback(Output(component_id='map', component_property='figure'), # Step4: choose an id name for the returned output
              [Input(component_id='varselect', component_property='value')]) # Step2: pass the input ot this calback

def makemap(col): # Step3: pass the input to a function to generate the output
    fig =  px.choropleth(vacounties,
                         geojson = counties,
                         color = col,
                         scope = 'usa',
                         locations = 'FIPS',
                         hover_name = 'Jurisdiction',
                         color_continuous_scale = 'reds',
                         hover_data = ['Total Population',
                                       'Average Annual Pay',
                                       'Cost of living',
                                       'Years of Potential Life Lost Rate',
                                       'Food Environment Index'])
    fig.update_geos(fitbounds='locations')
    return fig

@app.callback(Output(component_id = 'toptable', component_property = 'figure'), 
              [Input(component_id = 'varselect', component_property = 'value')])

def maketable(col):
    dispdata = vacounties.sort_values(col, ascending=False)
    dispdata['Rank'] = list(range(1,dispdata.shape[0]+1))
    dispdata[col] = dispdata[col].astype('int')
    dispdata = dispdata[['Rank','Jurisdiction', col]]
    return ff.create_table(dispdata.head(15))

@app.callback(Output(component_id = 'box', component_property = 'figure'), 
              [Input(component_id = 'varselect', component_property = 'value')])

def boxplot(col):
    fig = px.box(vacounties,
                 x = col,
                 y = 'county',
                 hover_name = 'Jurisdiction',
                 color = 'county')
    fig.update_layout(showlegend=False)
    fig.update_yaxes(title='')
    return fig

@app.callback(Output(component_id = 'scatter', component_property = 'figure'), 
              [Input(component_id = 'varselectx', component_property = 'value'),
               Input(component_id = 'varselecty', component_property = 'value')])

def scatter(col1, col2):
    fig = px.scatter(vacounties,
          y = col2,
          x = col1,
          color = 'Total Population',
          hover_name = 'Jurisdiction',
          trendline = 'ols')
    return fig

# Run the dashboard
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)