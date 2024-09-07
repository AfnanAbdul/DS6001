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

# data + data cleaning
gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

markdown_text = '''
The article [Gender Pay Gap Statistics In 2024](https://www.forbes.com/advisor/business/gender-pay-gap-statistics/) from Forbes discusses the persistent disparity in earnings between men and women. Despite efforts to close the gap, women continue to earn significantly less than men, with the average woman making 16% less than a man. The pay gap is even more pronounced for women of color, with Latinas and Black women facing the largest disparities. The article also highlights how this gap varies by industry, job title, location, and demographic factors, impacting women's long-term financial stability, including retirement savings compared to their mal counterpart.

The [General Social Survey](https://gss.norc.org) (GSS) is a comprehensive sociological survey that has been conducted since 1972, capturing a wide array of data on American society. Managed by NORC at the University of Chicago, the GSS includes demographic information, attitudes, and behaviors related to topics like politics, religion, and social issues. The survey also collects detailed data on employment, income, education, and occupational prestige, which are crucial features for investigating the gender wage gap, allowing us to analyze how factors such as education and job prestige contribute to income disparities between men and women.
'''

gss_clean['sex'] = gss_clean['sex'].replace({'male': 'Male', 'female': 'Female'})

# generating tables and plots
gss_table1 = gss_clean.groupby('sex'). agg({'income': 'mean',
                                            'job_prestige': 'mean',
                                            'socioeconomic_index': 'mean',
                                            'education': 'mean'}).round(2).reset_index()
gss_table1.columns = ['Sex', 'Mean Income', 'Mean Occupational Prestige', 
                         'Mean Socioeconomic Index', 'Mean Years of Education']
table1 = ff.create_table(gss_table1)

gss_bar = gss_clean.groupby(['male_breadwinner', 'sex']).size().reset_index()
gss_bar = gss_bar.rename({0: 'count'}, axis=1)
fig_bar = px.bar(gss_bar, x = 'male_breadwinner', y= 'count', color = 'sex',
                 labels = {'count': 'Number of Respondents',
                           'male_breadwinner': 'Level of Agreement',
                           'sex': 'Sex'},
                 barmode = 'group')

fig_scatter = px.scatter(gss_clean, x='job_prestige', y='income',
                         color = 'sex',
                         trendline = 'ols',
                         height=600, width=600,
                         labels = {'job_prestige': 'Occupational Prestige Score',
                                   'income': 'Income', 'sex': 'Sex'},
                         hover_data = ['education', 'socioeconomic_index'])

fig1 = px.box(gss_clean, y='sex', x='income', color='sex',
              labels = {'income': 'Income'})
fig1.update_layout(showlegend=False)
fig1.update_yaxes(title_text='')  # Remove the y-axis label for 'sex'

fig2 = px.box(gss_clean, y='sex', x='job_prestige', color='sex',
              labels = {'job_prestige': 'Occupational Prestige Score'})
fig2.update_layout(showlegend=False)
fig2.update_yaxes(title_text='')  # Remove the y-axis label for 'sex'

new_df = gss_clean.loc[:,['income', 'sex', 'job_prestige']]
bins = pd.cut(new_df['job_prestige'], bins=6, labels=["Very Low", "Low", "Medium-Low", "Medium-High", "High", "Very High"])
new_df['job_prestige_category'] = bins
new_df = new_df.dropna()

fig = px.box(new_df, y='sex', x='income', color='sex',
             facet_col='job_prestige_category', facet_col_wrap = 2,
             color_discrete_map = {'Male':'blue', 'Female':'red'},
             labels = {'income': 'Income'})
fig.update_layout(showlegend=False)
# Loop through each x-axis and remove the category title
for axis in fig.layout.annotations:
    axis.text = axis.text.split('=')[1]  # Keeps only the category name, removes the "job_prestige_category=" part
fig.update_yaxes(title_text='')  # Remove the y-axis label for 'sex'

# Inititalize the dashborad
app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

# Populate the dashboard
app.layout = html.Div(
    [
        html.H1("Exploring the 2019 General Social Survey"),
        dcc.Markdown(children=markdown_text),

        html.Div([
            html.H2("Comparison of Mean Income, Occupational Prestige, Socioeconomic Index, and Education by Gender"),
            dcc.Graph(figure=table1, style={'width': '50%', 'float': 'left'}),
            html.Div(style={'clear': 'both'})
        ]),

        html.Div([
            html.H2("Differences in Agreement with the Male Breadwinner Role by Gender"),
            dcc.Graph(figure=fig_bar, style={'width': '60%', 'float': 'left'}),
            html.Div(style={'clear': 'both'})
        ]),

        html.Div([
            html.H2("Income vs. Job Prestige by Gender with Insights"),
            dcc.Graph(figure=fig_scatter)
        ]),

        html.Div([
            html.Div([
                html.H2("Income Distribution by Gender"),
                dcc.Graph(figure=fig1)
            ], style={'width': '48%', 'float': 'left'}),

            html.Div([
                html.H2("Job Prestige Distribution by Gender"),
                dcc.Graph(figure=fig2)
            ], style={'width': '48%', 'float': 'right'})
        ]),

        html.Div([
            html.H2("Income Distribution Across Job Prestige Categories by Gender"),
            dcc.Graph(figure=fig, style={'width': '70%', 'float': 'left'}),
            html.Div(style={'clear': 'both'})
        ])
    ]
)

# Run the dashboard
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)