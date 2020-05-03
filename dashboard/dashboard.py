# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

df = pd.read_csv('data/rt_mcmc.csv', parse_dates = ['date'])

final_date = df.date.max()

app = dash.Dash("Rt dashboard")

pickable_dates = [final_date - pd.Timedelta(days = i) for i in[0,1,7]] #change to dropdown if too many here

app.layout = html.Div(children=[
    html.H1(children='This is work in progress'),

    html.Div(children='''
        An interactive dashboard for CoVid-19 Rt estimate.
    '''),

    dcc.Graph(
        id='rt-graph'
    ),
    html.Div(children = [
        dcc.RadioItems(id='order-picker',
            options = [
                {'label' : 'Country', 'value' : 'region'},
                {'label' : 'Transmission rate', 'value' : 'mean'}],
                value = 'mean',
                labelStyle = {'display': 'inline-block'}),
        dcc.RadioItems(id = 'date-picker',
                        options = [{'label' : d.date(), 'value' : d} for d in pickable_dates],
                        value = final_date.date(),
                        labelStyle = {'display': 'inline-block'})
        ], style={'width': '48%', 'display': 'inline-block'})
])

@app.callback(
    Output(component_id='rt-graph', component_property='figure'),
    [ Input(component_id='date-picker', component_property='value'),
        Input(component_id='order-picker', component_property='value')]
)
def rt_scatterplot(date, sort_col = 'region'):
    date = pd.to_datetime(date) #?? type is lost between components? fix this
    used_df = df[df.date == date].sort_values(by = sort_col)
    colors = ['rgb(204,0,0)' if v >= 1.0 else 'rgb(0,204,0)' for v in used_df['mean'].values]
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
            'title': f'Rt visualization for {date.date()}'
        }
    }
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
