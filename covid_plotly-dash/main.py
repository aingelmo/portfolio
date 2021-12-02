from datetime import date
from logging import debug
from re import template
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash.html.Title import Title
import pandas as pd
from pandas.core.frame import DataFrame
import plotly.express as px
import pandas as pd
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor

# Deploy from github

# -------------------------------------------------------------------------------------------------
# Define key variables
url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# -------------------------------------------------------------------------------------------------
### Dash configuration
# Create dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# Create server variable with Flask server object for use with gunicorn
server = app.server

# -------------------------------------------------------------------------------------------------
### Data loading and cleaning
def get_data():
    global df, countries, countries_clean, available_indicators, dict_agg
    # Load COVID-19 database from Our World in Data
    df = pd.read_csv(url)
    # Remove continents group from dataset
    df = df[df['continent'].notnull()]
    # Fill missing values with zeroes
    df.fillna(0, inplace=True)
    # Remove dates where COVID wasn't measured
    df = df[df['date'] > '2020-02-23']
    # Get a year-month column for further analysis
    df['month'] = pd.to_datetime(df['date']).dt.to_period('M').astype('str')
    df['quarter'] = pd.PeriodIndex(pd.to_datetime(df['date']), freq='Q').astype('str')

    # Get a dataframe with the countries and its continent
    countries = df[['location', 'continent']]
    countries_clean = countries.drop_duplicates()
    countries_clean.reset_index(inplace=True, drop=True)

    # Retrieve all possible indicators
    available_indicators = df.columns.tolist()[4:-1]
    available_indicators.remove('tests_units')

    # Define dictionary for future aggregation
    # Retrieve all indicators that supports the condition
    ind_strings = [i for i in df.columns.tolist() if df.dtypes[i] == 'O']
    ind_sum = [i for i in df.columns.tolist() if i[:3] == 'new']
    ind_max = [i for i in available_indicators if (i[:3] != 'new') & (df.dtypes[i] != 'O')]
    # Set aggregations for different dictionaries
    dict_sum = {i: 'sum' for i in ind_sum}
    dict_max = {i: 'max' for i in ind_max}
    # Merge dictionaries
    dict_agg = dict_sum | dict_max

### Load the data into the app every 12 hours
def get_data_interval(period=43200):
    while True:
        get_data()
        time.sleep(period)

# -------------------------------------------------------------------------------------------------
### Run function first time to get data to begin
get_data()

# -------------------------------------------------------------------------------------------------
app.layout = html.Div([
    html.Div([
        

        html.Div([
            html.H5('Select variable for the x axis'),

            dcc.Dropdown(
                id="dropdown-xaxis",
                options=[{"label": i.replace('_', ' ').title(), "value": i} for i in available_indicators],
                value='total_cases',
            )
        ],
            style={'width': '49%', 'display': 'inline-block'}),

        
        html.Div([
            html.H5('Select variable for the y axis'),

            dcc.Dropdown(
                id="dropdown-yaxis",
                options=[{"label": i.replace('_', ' ').title(), "value": i} for i in available_indicators],
                value='total_deaths',
            )
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
    ], style={'padding': '10px 5px'}
    ),


    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-scatter',
            clickData={'points': [{'hovertext': 'Spain'}]}
        )
    ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),


    html.Div([
        dcc.Graph(id='x-time-series'),
        dcc.Graph(id='y-time-series')
    ], style={'display': 'inline-block', 'width': '49%'}),


    html.Div([
        html.Div([
            dcc.RadioItems(
                id='time-aggregation-selector',
                options=[{'label': 'Months', 'value': 'month'},
                         {'label': 'Quarters', 'value': 'quarter'},],
                value='month',
                labelStyle={'display': 'inline-block'}
            ) 
        ], style={'width': '10%', 'display': 'inline-block', 'padding': '0px 5px'}),


        html.Div([
            dcc.Slider(
                id='crossfilter-date-slider'
            )
        ], style={'width': '85%', 'float': 'right', 'display': 'inline-block', 'padding': '7.5px 5px'}),
    ]),
    dcc.Store(id='memory-output-main'),
    dcc.Store(id='memory-output-secondary')
])


# -------------------------------------------------------------------------------------------------
## Return a dataset and save it on memory to perform few calculations on the chart of the left.
@app.callback(
    dash.dependencies.Output('memory-output-main', 'data'),
    [dash.dependencies.Input('time-aggregation-selector', 'value'),
     dash.dependencies.Input('crossfilter-date-slider', 'value')])
def filtered_dataframe(date_agg, date_value):
    dataset = df.groupby(['location', date_agg]).agg(dict_agg).reset_index()
    dataset = dataset.merge(countries_clean, how='left', on='location')
    dataset = dataset[dataset[date_agg] == slider_options[date_value]]
    return dataset.to_dict('records')


# -------------------------------------------------------------------------------------------------
## Return a dataset and save it on memory to perform few calculations on the chart of the right.
@app.callback(
    dash.dependencies.Output('memory-output-secondary', 'data'),
    [dash.dependencies.Input('time-aggregation-selector', 'value'),
     dash.dependencies.Input('crossfilter-date-slider', 'value')])
def filtered_dataframe(date_agg, date_value):
    dataset = df.groupby(['location', date_agg]).agg(dict_agg).reset_index()
    dataset = dataset.merge(countries_clean, how='left', on='location')
    dataset = dataset[dataset[date_agg] <= slider_options[date_value]]
    return dataset.to_dict('records')


# -------------------------------------------------------------------------------------------------
@app.callback(
    [dash.dependencies.Output('crossfilter-date-slider', 'min'),
     dash.dependencies.Output('crossfilter-date-slider', 'max'),
     dash.dependencies.Output('crossfilter-date-slider', 'value'),
     dash.dependencies.Output('crossfilter-date-slider', 'marks')],
    [dash.dependencies.Input('time-aggregation-selector', 'value')])
def update_slider(date_agg):
    # Create a global dictionary from all the different months/quarters and its position
    global slider_options
    slider_options = {d_key: d_val for d_key, d_val in enumerate(sorted(df[date_agg].unique()))}
    # Transform to list to access the keys
    keys_list = list(slider_options)
    # Set the minimum and maximum key value
    min = keys_list[0]
    max = keys_list[-1]
    # Set the default value
    value=max
    # Set the marks in the slider
    marks={i: slider_options[i] for i in slider_options}

    return min, max, value, marks


# -------------------------------------------------------------------------------------------------
@app.callback(
    dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),
    [dash.dependencies.Input('memory-output-main', 'data'),
     dash.dependencies.Input('dropdown-xaxis', 'value'),
     dash.dependencies.Input('dropdown-yaxis', 'value')])
def update_graph(data, xaxis_column_name, yaxis_column_name):
    # Load the dataframe from memory output
    dff = pd.DataFrame(data)

    # Scatter plot the graph
    fig = px.scatter(
        data_frame=dff,
        x=xaxis_column_name,
        y=yaxis_column_name,
        color='continent',
        hover_name='location',
        template='plotly_white')
    # Markers style
    fig.update_traces(customdata=dff['location'], marker={'size': 12, 'opacity': 0.6, 'line': {'width': 2, 'color': 'DarkSlateGrey'}})
    # Update labels retrieved from hovermode
    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
    # Update axis titles
    fig.update_xaxes(title=xaxis_column_name.replace('_', ' ').title())
    fig.update_yaxes(title=yaxis_column_name.replace('_', ' ').title())

    return fig


def create_time_series(dff, date_agg, title):
    # Scatter plot the graph with the date always on the x-axis and the variable selected on the y
    fig = px.scatter(dff, x=date_agg, y=dff.columns[-1], template='plotly_white')
    # Markers style
    fig.update_traces(mode='lines+markers')
    # Hide grid on the x-axis
    fig.update_xaxes(showgrid=False)
    # Add title to the chart
    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       text=title.replace('_', ' ').title(), bgcolor='rgba(255, 255, 255, 0.5)')
    # Set height and hide axis titles
    fig.update_layout(height=225, margin={'l': 20, 'b': 30, 'r': 10, 't': 10}, yaxis_title=None, xaxis_title=None)

    return fig

# -------------------------------------------------------------------------------------------------
@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('memory-output-secondary', 'data'),
     dash.dependencies.Input('crossfilter-indicator-scatter', 'clickData'),
     dash.dependencies.Input('dropdown-xaxis', 'value'),
     dash.dependencies.Input('time-aggregation-selector', 'value')])
def update_y_timeseries(data, clickData, xaxis_column_name, date_agg):
    # Load the dataframe from memory output
    dff = pd.DataFrame(data)
    # Retrieve country name from the data gathered my clicking with the mouse
    country_name = clickData['points'][0]['hovertext']
    # Filter the dataset by the country needed
    dff = dff[dff['location'] == country_name][['location', date_agg, xaxis_column_name]]
    # Set a title    
    title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
    
    return create_time_series(dff, date_agg, title)


# -------------------------------------------------------------------------------------------------
@app.callback(
    dash.dependencies.Output('y-time-series', 'figure'),
    [dash.dependencies.Input('memory-output-secondary', 'data'),
     dash.dependencies.Input('crossfilter-indicator-scatter', 'clickData'),
     dash.dependencies.Input('dropdown-yaxis', 'value'),
     dash.dependencies.Input('time-aggregation-selector', 'value')])
def update_x_timeseries(data, clickData, yaxis_column_name, date_agg):
    # Load the dataframe from memory output
    dff = pd.DataFrame(data)
    # Retrieve country name from the data gathered my hover the mouse
    country_name = clickData['points'][0]['hovertext']
    # Filter the dataset by the country needed
    dff = dff[dff['location'] == country_name][['location', date_agg, yaxis_column_name]]

    return create_time_series(dff, date_agg, yaxis_column_name)

# -------------------------------------------------------------------------------------------------
executor = ThreadPoolExecutor(max_workers=1)
executor.submit(get_data_interval)

# -------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
