###################################### IMPORT RELEVANT LIBRARIES #####################################

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import numpy
import os
import plotly.graph_objects as go
from dash import html, dcc, Input, Output, Dash
import warnings
import hide

warnings.filterwarnings('ignore')
import requests
import json

##################################### CREATE THE APP OBJECT ############################################

app = Dash(external_stylesheets=[dbc.themes.SOLAR])
server = app.server

###################################### FUNCTION TO RETURN THE NEXT DATE #################################

def date_plus_one(date_extraction):
    yy = int(date_extraction.split('-')[0])
    mm = int(date_extraction.split('-')[1])
    dd = int(date_extraction.split('-')[2])

    # no need to check if the year is leap year - next leap year is 2024 and historical data is only upto 14 days

    if dd == 31:
        if mm == 12:
            n_dd = str('01')
            n_mm = str('01')
            n_yy = str(yy + 1)

        if mm in [1, 3, 5, 7, 8, 10]:
            n_dd = '01'
            n_mm = '0' + str(mm + 1) if mm + 1 < 10 else str(mm + 1)
            n_yy = str(yy)


    elif dd == 30:
        if mm in [4, 6, 9, 11]:
            n_mm = '0' + str(mm + 1) if mm + 1 < 10 else str(mm + 1)
            n_yy = str(yy)
            n_dd = '01'

    elif dd == 28:
        if mm == 2:
            n_dd = '01'
            n_mm = '03'
            n_yy = str(yy)

    else:
        n_dd = '0' + str(dd + 1) if dd + 1 < 10 else str(dd + 1)
        n_mm = '0' + str(mm) if mm + 1 < 10 else str(mm)
        n_yy = str(yy)

    next_date = '-'.join([n_yy, n_mm, n_dd])
    return next_date


################################## DATA FRAME NONE - PLOT IT WHEN NO DATA #######################################

df_none = pd.DataFrame(dict(
    x=[0],
    y=[0]
))

df_none.rename(columns={'x': 'Time',
                        'y': 'Temperature and Humidity'}, inplace=True)

################################# LAYOUT OF THE DASH APP ###########################################################


app.layout = html.Div([

    html.Div([
        dbc.Row([
            dbc.Col([html.H1(id='city_name')],
                    style={'textAlign': 'left', 'fontFamily': 'fantasy', 'margin-left': '1%', 'margin-top': '1%'}),
            dbc.Col([html.H1(id='weather_description')],
                    style={'textAlign': 'right', 'fontFamily': 'fantasy', 'margin-right': '2%', 'margin-top': '1%'})
        ])
    ], style={'margin-bottom': '0%'}),

    html.H1("The Weather App", style={'color': 'Cyan', 'textAlign': 'center'}),
    html.Br(),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                html.H4("TEMPERATURE"),
                html.P(id='temp_city')],
                style={'textAlign': 'center', 'height': '10vh', 'fontSize': 20, 'fontFamily': 'fantasy',
                       'alignItems': 'center'})
        ]),

        dbc.Col([
            dbc.Card([
                html.H4("VISIBILITY"),
                html.P(id='visibility_city')],
                style={'textAlign': 'center', 'height': '10vh', 'fontSize': 20, 'fontFamily': 'fantasy',
                       'alignItems': 'center'})
        ]),
        dbc.Col([
            dbc.Card([
                html.H4("WIND SPEED"),
                html.P(id='wind_speed_city')],
                style={'textAlign': 'center', 'height': '10vh', 'fontSize': 20, 'fontFamily': 'fantasy',
                       'alignItems': 'center'})
        ]),
        dbc.Col([
            dbc.Card([
                html.H4("PRECIPITATION"),
                html.P(id='precipitation_city')],
                style={'textAlign': 'center', 'height': '10vh', 'fontSize': 20, 'fontFamily': 'fantasy',
                       'alignItems': 'center'})
        ]),
        dbc.Col([
            dbc.Card([
                html.H4("HUMIDITY"),
                html.P(id='humidity_city')],
                style={'textAlign': 'center', 'height': '10vh', 'fontSize': 20, 'fontFamily': 'fantasy',
                       'alignItems': 'center'})
        ])
    ]),

    html.Br(),

    dbc.Row([

        dbc.Col([
            dcc.Graph(id='line_graph', style={'height': 430, 'backgroundColor': 'cyan'})
        ], width=9),

        dbc.Col([
            dbc.Row([

                dbc.Input(id='input_location', placeholder='Enter a City name ex. New Delhi', type='text',
                          debounce=True),
                html.Br()
            ]),

            html.Br(),
            dbc.Row([
                dbc.Card([
                    html.H4("CLOUD COVER"),
                    html.P(id='cloud_cover_city')],
                    style={'textAlign': 'center', 'height': '10vh', 'fontSize': 20, 'fontFamily': 'fantasy',
                           'alignItems': 'center'})
            ]),

            html.Br(),
            dbc.Row([
                dbc.Card([
                    html.H4("FEELS LIKE"),
                    html.P(id='feels_like_city')],
                    style={'textAlign': 'center', 'height': '10vh', 'fontSize': 20, 'fontFamily': 'fantasy',
                           'alignItems': 'center'})
            ]),

            html.Br(),
            dbc.Row([
                dbc.Card([
                    html.H4("UV INDEX"),
                    html.P(id='uv_index_city')],
                    style={'textAlign': 'center', 'height': '10vh', 'fontSize': 20, 'fontFamily': 'fantasy',
                           'alignItems': 'center'})
            ]),

            html.Br(),
            dbc.Row([
                dbc.Card([
                    html.H4("LOCAL TIME"),
                    html.P(id='local_time_city')],
                    style={'textAlign': 'center', 'height': '10vh', 'fontSize': 20, 'fontFamily': 'fantasy',
                           'alignItems': 'center'})
            ]),

        ])

    ])
])


########################################## DECORATOR ###############################################################


@app.callback(
    Output('temp_city', 'children'),
    Output('visibility_city', 'children'),
    Output('wind_speed_city', 'children'),
    Output('precipitation_city', 'children'),
    Output('humidity_city', 'children'),
    Output('cloud_cover_city', 'children'),
    Output('feels_like_city', 'children'),
    Output('uv_index_city', 'children'),
    Output('local_time_city', 'children'),
    Output('line_graph', 'figure'),
    Output('city_name', 'children'),
    Output('weather_description', 'children'),
    Input('input_location', 'value'),
)
###################################### FUNCTION TO COMPUTE / DISPLAY THE INFORMATION ################################

def update_values(entered_location):
    ################################# IF NO LOCATION IS ENTERED ##############################################

    if entered_location is None:
        fig = px.line(df_none, x="Time", y="Temperature and Humidity", title=" No Data ")
        fig.update_layout(template='plotly_dark')

        return '0', '0', '0', '0', '0', '0', '0', '0', '0', fig, 'City Name', 'Weather Description'

    ############################### GET CURRENT WEATHER DATA #############################################

    params = {
        'access_key': hide.api,
        'query': entered_location,
    }
    api_result = requests.get('https://api.weatherstack.com/current', params)
    api_response = api_result.json()

    ############################ CHECK IF THE LOCATION IS VALID / DATA AVAILABLE OR NOT #########################

    if list(api_response.items())[0][0] == 'success' and list(api_response.items())[0][1] == False:
        fig = px.line(df_none, x="Time", y="Temperature and Humidity", title=" No Data ")
        fig.update_layout(template='plotly_dark')

        return '0', '0', '0', '0', '0', '0', '0', '0', '0', fig, 'Data Not Available for the Location', 'Weather Description'

    ############################ GET THE CURRENT WEATHER PARAMETERS ###############################################

    temperature_v = api_response['current']['temperature']
    visibility_v = api_response['current']['visibility']
    feels_like_v = api_response['current']['feelslike']
    visibility_v = api_response['current']['visibility']
    windspeed_v = api_response['current']['wind_speed']
    precipitation_v = api_response['current']['precip']
    humidity_v = api_response['current']['humidity']
    uv_index_v = api_response['current']['uv_index']
    local_time_v = api_response['location']['localtime']
    cloud_cover_v = api_response['current']['cloudcover']
    weather_now_v = api_response['current']['weather_descriptions'][0]

    date_extraction = local_time_v.split(' ')[0]

    ####################################### GET DATA FOR THE WHOLE DAY - FOR GRAPH #################################

    params_hist = {

        'access_key': hide.api,
        'query': entered_location,
        'historical_date_start': date_extraction,
        'historical_date_end': date_plus_one(date_extraction),
        'hourly': 1,
        'interval': 1
    }

    api_result_hist = requests.get('https://api.weatherstack.com/historical', params_hist)
    api_response_hist = api_result_hist.json()

    ##################################### CHECK IF COMPLETE DATA FOR THE DAY IS AVAILABLE OR NOT #########################

    if list(api_response_hist.items())[0][0] == 'success' and list(api_response_hist.items())[0][1] == False:
        fig = px.line(df_none, x="Time", y="Temperature and Humidity",
                      title=" Not Enough Data Available to plot the graph for whole day")
        fig.update_layout(template='plotly_dark')

        return (str(temperature_v) + "°C"), (str(visibility_v) + ' km'), (str(windspeed_v) + " kmph"), (
                    str(precipitation_v) + " mm"), (str(humidity_v) + ' %'), (str(cloud_cover_v) + ' %'), (
                           str(feels_like_v) + "°C"), str(uv_index_v), str(
            local_time_v), fig, entered_location.title(), weather_now_v.title()

    ##################################### IF DATA FOR THE WHOLE DAY IS PRESENT -> PROCEED ##############################

    length = len(api_response_hist['historical'][date_extraction]['hourly'])
    ex = (api_response_hist['historical'][date_extraction]['hourly'])

    y_data_temp = []
    x_data_times = ['12:00 AM', '1:00 AM', '2:00 AM', '3:00 AM', '4:00 AM', '5:00 AM', '6:00 AM', '7:00 AM', '8:00 AM',
              '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM',
              '6:00 PM', '7:00 PM', '8:00 PM', '9:00 PM', '10:00 PM', '11:00 PM']
    y_data_humidity = []
    x_data = []
    for i in range(0, length):
        y_data_temp.append(ex[i]['temperature'])
        x_data.append(x_data_times[i])
        # x_data.append(ex[i]['time']) [NOT IN USE]
        y_data_humidity.append((ex[i]['humidity']))

    df = pd.DataFrame(dict(
        x=x_data,
        y=y_data_temp,
        humidity_data=y_data_humidity,
    ))

    df.rename(columns={'x': 'Time',
                       'y': 'Temperature in °C',
                       'humidity_data': 'Humidity in %',
                       }, inplace=True)
    fig = px.line(df, x="Time", y=["Temperature in °C", 'Humidity in %'],
                  title="Temperature and Humidity variation throughout the day",
                  labels={'value': 'Temperature and Humidity'})
    fig.update_layout(template='plotly_dark')
    fig.update_layout(hoverlabel=dict(
        bgcolor="white",
        font_size=10,
        font_family="Rockwell"
    )
    )

    return (str(temperature_v) + "°C"), (str(visibility_v) + ' km'), (str(windspeed_v) + " kmph"), (
                str(precipitation_v) + " mm"), (str(humidity_v) + ' %'), (str(cloud_cover_v) + ' %'), (
                       str(feels_like_v) + "°C"), str(uv_index_v), str(
        local_time_v), fig, entered_location.title(), weather_now_v.title()


if __name__ == '__main__':
    app.run_server(debug = True)