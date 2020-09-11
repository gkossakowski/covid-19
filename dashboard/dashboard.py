# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import math
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
df = pd.read_csv('data/rt_mcmc.csv', parse_dates = ['date'])

final_date = df.date.max()

app = dash.Dash("Rt dashboard",external_stylesheets=external_stylesheets, meta_tags = [{
      'name': 'viewport',
      'content': 'width=device-width, initial-scale=1.0'
    }])

pickable_dates = [final_date - pd.Timedelta(days = i) for i in[0,1,7]] #change to dropdown if too many here

def color_splitting_line(df):
    return np.minimum(np.maximum(df['lower_90'], 1.0), df['upper_90'])

RED = 'rgb(184,97,97,0.3)'
GREEN = 'rgb(97,184,97,0.3)'
def upper_bound_plot(df):
    return { 'x' : df['date'].dt.date,
             'y' : df['upper_90'],
             'type' : 'scatter',
             'mode' : 'lines',
             'name' : '90% confidence upper bound',
             'fill' : 'tonexty',
             'fillcolor' : RED,
             'showlegend' : False,
             'line' : {'width' : 0} # the upper bound does not need extra line
            }

def fake_1_line(df):
    return { 'x' : df['date'].dt.date,
             'y' : color_splitting_line(df),
             'type' : 'scatter',
             'mode' : 'lines',
             'fill' : 'tonexty',
             'fillcolor' : GREEN,
             'showlegend' : False,
             'line' : {'width' : 0} # the upper bound does not need extra line
            }

def lower_bound_plot(df):
    return { 'x' : df['date'].dt.date,
             'y' : df['lower_90'],
             'type' : 'scatter',
             'mode' : 'lines',
             'name' : '90% confidence lower bound',
             'showlegend' : False,
             'line' : {'width' : 0} # the upper bound does not need extra line
            }

def rt_plot(df):
    return { 'x' : df['date'].dt.date,
             'y' : df['mean'],
             'type' : 'scatter',
             'name' : 'rt estimate',
             'mode' : 'lines',
             'line' : {'color' : 'rgb(31, 119, 180)'}
            }

def rt_region_plot(region):
    # returns time series of Rt estimates figure for the given region
    region_df = df[df.region ==  region]
    return [lower_bound_plot(region_df), fake_1_line(region_df), upper_bound_plot(region_df), rt_plot(region_df)]

# figure for regions
all_regions = list(df['region'].unique())
num_regions = len(all_regions)
N_COLS = 3
N_ROWS = math.ceil(num_regions / N_COLS)
regions_fig = make_subplots(rows = N_ROWS, cols = N_COLS, subplot_titles = all_regions)
for region_number, region in enumerate(all_regions):
    row_number = region_number // N_COLS + 1 #subplots numbers plots starting from 1,1
    col_number = region_number % N_COLS + 1 #subplots numbers plots starting from 1,1
    for trace in rt_region_plot(region):
        regions_fig.add_trace(trace, row = row_number, col = col_number)
    regions_fig.update_yaxes(title = 'reproduction rate (Rt)', range=[0,2.0], row = row_number, col = col_number)
    regions_fig.update_xaxes(title = 'date', row = row_number, col = col_number)
regions_fig.update_layout(title_text="Evolution of Rt in time per country", height=400 * N_ROWS, showlegend=False)

app.layout = html.Div(children=[
    html.H1(children='Covid-19 reproduction rate'),

    html.Div(children='''
        An interactive dashboard for presenting the reproduction rate (R_t) for Covid-19 Pandemic.
    '''),

    dcc.Graph(
        id='rt-graph'
    ),
    html.Div(children = [
        dcc.RadioItems(id='order-picker',
            options = [
                {'label' : 'Country', 'value' : 'region'},
                {'label' : 'Reproduction rate', 'value' : 'mean'}],
                value = 'mean',
                labelStyle = {'display': 'inline-block'}),
        dcc.RadioItems(id = 'date-picker',
                        options = [{'label' : d.date(), 'value' : d} for d in pickable_dates],
                        value = final_date.date(),
                        labelStyle = {'display': 'inline-block'})
        ], style={'width': '48%', 'display': 'inline-block'}),
    dcc.Graph(id = f'rt-{region}-graph', figure = regions_fig)
        ])

@app.callback(
    Output(component_id='rt-graph', component_property='figure'),
    [ Input(component_id='date-picker', component_property='value'),
        Input(component_id='order-picker', component_property='value')]
)
def rt_barplot(date, sort_col = 'region'):
    date = pd.to_datetime(date) #?? type is lost between components? fix this
    used_df = df[df.date == date].sort_values(by = sort_col)
    colors = [RED if v >= 1.0 else GREEN for v in used_df['mean'].values]
    figure={
        'data': [
            {'x': used_df.region,
            'y': used_df['mean'],
            'type': 'bar',
            'name': 'Rt estimate',
            'marker' : {'color' : colors},
            'error_y' : {'type':'data',
                            'symmetric' : False,
                            'array' : used_df['upper_90'] -used_df['mean'],
                            'arrayminus' : used_df['mean'] - used_df['lower_90']}
            }
        ],
        'layout': {
            'title': f'R_t visualization for {date.date()}'
        }
    }
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
