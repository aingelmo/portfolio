from logging import debug
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import pandas as pd
import numpy as np

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
# Load COVID-19 database from Our World in Data
df = pd.read_csv(url)
# Remove continents group from dataset
df = df[df['continent'].notnull()]
# Fill missing values with zeroes
df.fillna(0, inplace=True)
# Remove dates where COVID wasnt measured
df = df[df['date'] > '2020-02-23']
# Get a year-month column for further analysis
df['month'] = df['date'].str[:7]

# Get a daframe with the countries and its continent
countries = df[['location', 'continent']]
countries_clean = countries.drop_duplicates()
countries_clean.reset_index(inplace=True, drop=True)

# Retrieve all posible indicators
available_indicators = df.columns.tolist()[4:]

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

# Group data by months
df_months = df.groupby(['location', 'month']).agg(dict_agg).reset_index()
# Append continents list
df_months = df_months.merge(countries_clean, how='left', on='location')

# Create slider dictionary
slider_options = {d_key: d_val for d_key, d_val in enumerate(sorted(df['month'].unique()))}

# Create array of equally spaced out dates
x = np.linspace(min(slider_options.keys()), max(slider_options.keys()), 10, dtype=int)
x = x.round(0)

# -------------------------------------------------------------------------------------------------
app.layout = html.Div([
    html.Div([
        

        html.Div([
            html.H5('x-axis variable'),

            dcc.Dropdown(
                id="dropdown-xaxis",
                options=[{"label": i, "value": i} for i in available_indicators],
                value='total_cases',
            )
        ],
            style={'width': '49%', 'display': 'inline-block'}),

        

        html.Div([
            html.H5('y-axis variable'),

            dcc.Dropdown(
                id="dropdown-yaxis",
                options=[{"label": i, "value": i} for i in available_indicators],
                value='total_deaths',
            )
        ],
            style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
    ], style={'padding': '10px 5px'}
    ),

    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-scatter',
            hoverData={'points': [{'hovertext': 'Spain'}]}
        )
    ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
    html.Div([
        dcc.Graph(id='x-time-series'),
        dcc.Graph(id='y-time-series')
    ], style={'display': 'inline-block', 'width': '49%'}),

    html.Div(dcc.Slider(
        id='crossfilter-date-slider',
        min=min(slider_options.keys()),
        max=max(slider_options.keys()),
        value=max(slider_options.keys()),
        marks={i: slider_options[i] for i in slider_options},
        step=None
    ), style={'width': '95%', 'padding': '0px 20px 20px 20px'})
])


# -------------------------------------------------------------------------------------------------
@app.callback(
    dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),
    [dash.dependencies.Input('dropdown-xaxis', 'value'),
     dash.dependencies.Input('dropdown-yaxis', 'value'),
     dash.dependencies.Input('crossfilter-date-slider', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name, date_value):
    dff = df_months[df_months['month'] == slider_options[date_value]]


    fig = px.scatter(
        data_frame=dff,
        x=xaxis_column_name,
        y=yaxis_column_name,
        color='continent',
        hover_name='location'
    )

    fig.update_traces(customdata=dff['location'])

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    return fig


def create_time_series(dff, title):
    fig = px.scatter(dff, x='month', y=dff.columns[-1])

    fig.update_traces(mode='lines+markers')

    fig.update_xaxes(showgrid=False)

    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       text=title)

    fig.update_layout(height=225, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})

    return fig


@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
     dash.dependencies.Input('dropdown-xaxis', 'value')])
def update_y_timeseries(hoverData, xaxis_column_name):
    country_name = hoverData['points'][0]['hovertext']
    dff = df_months[df_months['location'] == country_name]
    dff = dff[['location', 'month', xaxis_column_name]]
    title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
    return create_time_series(dff, title)



@app.callback(
    dash.dependencies.Output('y-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
     dash.dependencies.Input('dropdown-yaxis', 'value')])
def update_x_timeseries(hoverData, yaxis_column_name):
    dff = df_months[df_months['location'] == hoverData['points'][0]['hovertext']]
    dff = dff[['location', 'month', yaxis_column_name]]
    return create_time_series(dff, yaxis_column_name)


if __name__ == '__main__':
    app.run_server(debug=True)
