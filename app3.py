
# IMPORT THE REQUIRED LIBRARIES :

import os
import pickle
import copy
import datetime as dt

import pandas as pd
from flask import Flask
from flask_cors import CORS
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

#IMPORTING THE DATA AND CLEANING TE DATA ACCORDING TO USAGE :

data=pd.read_csv("WorldCups.csv")

matches=pd.read_csv("WorldCupMatches.csv")
matches = matches.drop_duplicates(subset="MatchID",keep="first")
matches = matches[matches["Year"].notnull()]
att = matches.groupby("Year")["Attendance"].sum().reset_index()
att["Year"] = att["Year"].astype(int)
att = matches.groupby("Year")["Attendance"].sum().reset_index()
att["Year"] = att["Year"].astype(int)


cups     = pd.read_csv(r"WorldCups.csv")
cups["Winner"]=cups["Winner"].replace("Germany FR","Germany")
cups["Runners-Up"]=cups["Runners-Up"].replace("Germany FR","Germany")
cups["Year1"] = cups["Year"].astype(str)
c1  = cups.groupby("Winner")["Year1"].apply(" , ".join).reset_index()
c2  = cups.groupby("Winner")['Year'].count().reset_index()
c12 = c1.merge(c2,left_on="Winner",right_on="Winner",how="left")
c12 = c12.sort_values(by = "Year",ascending =False)


tt_gl_h = matches.groupby("Home Team Name")["Home Team Goals"].sum().reset_index()
tt_gl_h.columns = ["team","goals"]
tt_gl_a = matches.groupby("Away Team Name")["Away Team Goals"].sum().reset_index()
tt_gl_a.columns = ["team","goals"]
total_goals = pd.concat([tt_gl_h,tt_gl_a],axis=0)
total_goals = total_goals.groupby("team")["goals"].sum().reset_index()
total_goals = total_goals.sort_values(by="goals",ascending =False)
total_goals["goals"] = total_goals["goals"].astype(int)


cou = cups["Winner"].value_counts().reset_index()
cou_w = cou.copy()
cou_w.columns = ["country","count"]
cou_w["type"] = "WINNER"
cou_r = cups["Runners-Up"].value_counts().reset_index()
cou_r.columns = ["country","count"]
cou_r["type"] = "RUNNER - Up"
cou_t = pd.concat([cou_w,cou_r],axis=0)



# CREATING A DEFAULT LAYOUT FOR THE PAGE :

app = dash.Dash(__name__)
app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})  # noqa: E501
server = app.server
CORS(server)

if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'  # noqa: E501
    })



# CREATE THE HTML TEMPLATE :

mapbox_access_token = 'pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w'  # noqa: E501

layout = dict(
    autosize=True,
    height=500,
    font=dict(color='#CCCCCC'),
    titlefont=dict(color='#CCCCCC', size='14'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor="#191A1A",
    paper_bgcolor="#020202",
    legend=dict(font=dict(size=10), orientation='h'),
    title='Satellite Overview',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="dark",
        center=dict(
            lon=-78.05,
            lat=42.54
        ),
        zoom=7,
    )
)


# CREATING APP LAYOUT AND PLOTTING THE GRAPHS :
app.layout = html.Div(
    [
        html.Div(
            [
                html.H2(
                    'FIFA WORLD CUP DATA (1930-2014) VISUALIZATION',
                    className='eight columns',
                ),
                html.Img(
                    #src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe.png",
                    className='one columns',
                    style={
                        'height': '100',
                        'width': '225',
                        'float': 'right',
                        'position': 'relative',
                    },
                ),
            ],
            className='row'
        ),
        html.Div(
            [
                html.H5(
                    'TOTAL GOALS',
                    id='well_text',
                    className='two columns'
                ),
                html.H5(
                    '',
                    id='production_text',
                    className='eight columns',
                    style={'text-align': 'center'}
                ),
                html.H5(
                    '',
                    id='year_text',
                    className='two columns',
                    style={'text-align': 'right'}
                ),
            ],
            className='row'
        ),
        html.Div(
            [
                html.H4('FILTER BY YEARS:'), 
                dcc.RangeSlider(
                    id='year_slider',
                    min=1930,
                    max=2014,
                    value=[1970, 2010]
                ),
            ],
            style={'margin-top': '20'}
        ),
       
                        
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='goals_scored1',
                            figure={
                                'data': [
                                    go.Scatter(
                                        x= data['Year'],
                                        y= data['GoalsScored'],
                                        mode= 'markers+lines',
                                        marker= dict(size= 14,line= dict(width=1),color= data['GoalsScored'],opacity= 0.8)
                                    )
                                ],
                                'layout': go.Layout(
                                    title= 'Total GoalsScored in an Year',
                                    hovermode= 'closest',
                                    
                                    xaxis= dict(title= 'Year',ticklen= 5,zeroline= False,gridwidth= 2,),
                                    
                                    yaxis=dict(title= 'GoalsScored',ticklen= 5,gridwidth= 2,),
                                    showlegend= False
                                )
                            }
                        )
                    ], 
                    className="eight columns",
                    style={'margin-top': '10'}
                ),

                html.Div(
                    [
                        dcc.Graph(id='number of cups',
                            figure={
                                'data': [
                                    go.Bar(
                                        x=c12['Winner'],
                                        y=c12['Year'],
                                        marker=dict(color=c12['Year'])
                                    )
                                ], 

                                'layout': go.Layout(
                                    title= 'Teams With Most number of WorldCup Victory',
                                    hovermode= 'closest',
                                    xaxis= dict(title= 'Teams',ticklen= 5,zeroline= False,gridwidth= 2,),
                                   
                                    yaxis=dict(title= 'Number of Victories',ticklen= 5,gridwidth= 2,),
                                    showlegend= False
                                )
                            }    
                        )
                    ],
                    className='four columns',
                    style={'margin-top': '20'}
                ),
            ],
            className='row'
        ),


        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='count_graph',
                                figure={
                                    'data': [
                                        go.Scatter(
                                            x=total_goals['team'],
                                            y=total_goals['goals'],
                                            mode='markers+lines',
                                            marker=dict(color=total_goals['goals'])
                                        )
                                    ],    

                                    'layout': go.Layout(
                                        title= 'Total Goals Scored by Each Country',
                                        hovermode= 'closest',
                                        xaxis= dict(title= 'Countries',ticklen= 5,zeroline= False,gridwidth= 2,showgrid=False,showticklabels=False,ticks=''),
                                        
                                        yaxis=dict(title= 'Number of Goals',ticklen= 5,gridwidth= 2,),
                                        showlegend= False
                                    )
                                }    
                            )
                    ],
                    className='four columns',
                    style={'margin-top': '10'}
                ),



                html.Div(
                    [
                        dcc.Graph(id='attendance',
                            figure={
                                'data': [
                                        go.Bar(
                                            x=att['Year'],
                                            y=att['Attendance'],
                                            marker=dict(color=att['Year'])
                                        )
                                ],
                                'layout': go.Layout(
                                    title= 'Attendance of Crowd In a particular Year',
                                    hovermode= 'closest',
                                    xaxis= dict(title= 'Year',ticklen= 5,zeroline= False,gridwidth= 2,),

                                    yaxis=dict(title= 'Attendance in Millions',ticklen= 5,gridwidth= 2,),
                                    showlegend= False
                                )
                            }
                        )
                    ],
                    className="four columns",
                    style={'margin-top': '10'}
                ),




                html.Div(
                    [
                        dcc.Graph(id='goals_scored',
                            figure={
                                'data': [
                                        {
                                            'x':cou_w['country'],
                                            'y':cou_w['count'],
                                            'type':'bar',
                                            'name':'Winner',
                                            'marker':dict(color='brickred')
                                        },

                                        {
                                            'x':cou_r['country'],
                                            'y':cou_r['count'],
                                            'type':'bar',
                                            'name':'Runner-up',
                                            'marker':dict(color='Seablue')
                                        }    
                                ],

                                'layout': go.Layout(
                                        title='Most number of Runner Ups',
                                        xaxis= dict(title= 'Teams',ticklen= 5,zeroline= False,gridwidth= 2,),
                                        
                                        yaxis=dict(title= 'Wins/Runner-ups',ticklen= 5,gridwidth= 2,),
                                        barmode='group'
                                )
                            }
                            
                        )
                    ], 
                    className="four columns",
                    style={'margin-top': '10'}
                ),

        ],
        className='row'
        ),
    ],
    className='ten columns offset-by-one'
)

# CALLBACK - FUNCTIONS:
# SLIDER - YEAR TEXT :

@app.callback(Output('year_text', 'children'),
              [Input('year_slider', 'value')])
def update_year_text(year_slider):
    return "{} | {}".format(year_slider[0], year_slider[1])

# SLIDER - TOTAL GOALS TEXT :

@app.callback(Output('well_text', 'children'),
              [Input('year_slider', 'value')])
def update_year_text(year_slider):
    sel = (data['Year']>=year_slider[0]) & (data['Year']<=year_slider[1])
    goals = data[sel]["GoalsScored"].sum()
    return "TOTAL GOALS : {}".format(goals)


# MAIN :

if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
