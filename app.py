import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np


def read_clean_dataset(data_filename):
    """Read file from directory and perform some cleaning tasks

    Args:
        data_filename : path to data file (at the moment, only accepts excel files)

    Returns:
        main_df : cleaned dataframe

    """

    # Read data from excel file. We previously downloaded the table from Wyscout.com
    main_df = pd.read_excel(data_filename)
    # Drop players with no Team
    main_df = main_df.dropna(subset=["Team"], inplace=False)
    # Fill NaN with zeros to avoid errors in the visualisation
    main_df = main_df.fillna(0)
    # Filter players with at least 800 min played (at least 9 matches)
    main_df = main_df[main_df['Minutes played'] > 800].reset_index()

    return main_df


def dropdown_options(main_df):
    """Creates list of dropdown options (dictionaries {'label':<value>, 'value':<value>)

    Args:
        main_df : pandas dataframe

    Returns:
        3 lists : list_teams, list_players, list_metrics containing dictionaries
    """
    # Teams
    list_teams = []
    for team in np.sort(main_df['Team'].unique()):
        list_teams.append({'label': team, 'value': team})
    # Players
    list_players = []
    for team in np.sort(main_df['Team'].unique())[0:2]:
        for player in main_df[main_df['Team'] == team]['Player']:
            list_players.append({'label': player, 'value': player})
    # Metrics
    list_metrics = []
    for metric in np.sort(main_df.columns):
        list_metrics.append({'label': metric, 'value': metric})

    return list_teams, list_players, list_metrics


def default_dropdown_options(list_players, list_metrics):
    """Returns lists with the set of teams, players and metric values in the dataset

    Args:
        list_teams, list_players, list_metrics : lists of dictionaries

    Returns:
        default_players : list of dictionaries  of two first players in the selected teams
        default_metrics : list of dictionaries of two first metrics available

    """
    default_players = [list_players[0]['value'], list_players[1]['value']]
    default_metrics = [list_metrics[0]['value'], list_metrics[1]['value']]

    return default_players, default_metrics


def create_figure_players_comparison(main_df, players, metrics):
    """Creates radar chart based on players and columns selected by the user

    Args:
        main_df : pandas dataframe
        players : list with players names
        metrics : list with metrics to compare

    Return:
        plotly figure

    """

    # Create the figure
    fig = go.Figure()

    # Loop to create one trace for each player
    for player in players:

        # Initialise empty lists
        norm_values_list = []  # Normalised values from 0 to 1, for each metric.
        actual_values_list = []  # Actual values to display when hovering over the point

        # For each player, loop through each selected column
        for metric in metrics:
            norm_values_list.append(main_df[main_df['Player'] == player][metric].iloc[0] / main_df[
                metric].max())  # Divide by max value in the whole dataset to normalise metric
            actual_values_list.append(main_df[main_df['Player'] == player][metric].iloc[0])

        # Add trace to the figure
        fig.add_trace(go.Scatterpolar(
            r=norm_values_list,
            theta=metrics,
            hovertext=actual_values_list,
            hovertemplate='%{hovertext}',  # Show actual value when hovering
            fill='toself',
            name=player
        ))

    fig.update_layout(

        polar=dict(
            bgcolor="rgb(223, 223, 223)",
            radialaxis=dict(
                visible=True,
                range=[0, 1],  # We are plotting the normnalised values to be able to compare different metrics
                showticklabels=False
            )),
        showlegend=True,
        autosize=True,
        font=dict(family='Helvetica',
                  #size=18,
                  color='black')
    )

    return fig


### 1. READ AND CLEAN DATA
main_df = read_clean_dataset(data_filename='./assets/data.xlsx')


### 2. GET VALUES FOR DROPDOWNS AND CREATE DEFAULT FIGURE
# Get all possible values for players and metrics
list_teams, list_players, list_metrics = dropdown_options(main_df)
# Select default dropdown values
default_teams = ['Barcelona', 'Juventus']
default_players = ['L. Messi', 'Cristiano Ronaldo']
default_metrics = ['Non-penalty goals per 90','xG per 90','Shots per 90','Shots on target %','xA per 90','Dribbles succ. %', 'Off duels won %','Touches in box per 90']
# Create Figure
fig_default = create_figure_players_comparison(main_df=main_df,
                                               players=default_players,
                                               metrics=default_metrics)

### 3. DASH APP
# Import css stylesheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# Create App
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
# Create Layout
app.layout = html.Div(children=[


    html.Div(children=[
                    html.Img(src=app.get_asset_url('logo1.jpg'),
                             style = {
                                      'height': "50px",
                                      'width': "auto",
                                      },
                             #className = 'one columns'
                             ),

                    html.H1(id='main_header',
                            children='Player comparison',
                            style={
                                'textAlign': 'left',
                                'color': 'rgb(51, 63, 80)',
                                'fontSize': '40',
                                'font-family': 'Helvetica',
                                'line-height': 55

                            },
                            # className = 'three columns'
                            ),

                        ]

            #,style = {'borderStyle': 'solid',
            #        'borderColor': 'green'}

            #,className = 'row'
    ),

    html.Div(children=["Looking for my first job as Data Analyst, ",
                       html.A('follow me on LinkedIn', href='https://www.linkedin.com/in/david-fernandez-11a715170/', target="_blank")],
             style={'margin-bottom': '25px'}),


    html.P(children=['Select teams'],
           style={'fontSize': '100%',
                  'font-family': 'Helvetica'
                  }
           ),


    dcc.Dropdown(
        id='teams_dropdown',
        options=list_teams
        ,
        multi=True,
        value=default_teams,
        placeholder="Select teams",
        optionHeight=20,
        style={'margin-bottom': '25px'}

    ),

    html.P(children=['Select players'],
           style={'fontSize': '100%',
                  'font-family': 'Helvetica'
                  }
           ),


    dcc.Dropdown(
        id='players_dropdown',
        options=list_players
        ,
        multi=True,
        value=default_players,
        placeholder="Select players to compare",
        optionHeight=20,
        style={'margin-bottom': '25px'}
    ),

    html.P(children=['Select metrics'],
           style={'fontSize': '100%',
                  'font-family': 'Helvetica'
                  }
           ),

    dcc.Dropdown(
        id='variables_dropdown',
        options=list_metrics
        ,
        multi=True,
        value=default_metrics,
        placeholder="What do you want to compare?",
        optionHeight=20,
        style={'margin-bottom': '25px'}
    ),

    dcc.Graph(
        id='main_graph',
        figure=fig_default,
        config={'displaylogo': 'False'}
    ),

    html.P(children=['Notes: Only players from the Top 5 EU leagues and with more than 800 minutes played.'],
               style={'fontSize': '6',
                      'color': 'rgb(176, 176, 176)',
                      'font-family': 'Helvetica'
                      }
               ),

    html.Div(children=["All data from  ",
                           html.A('Wyscout.com', href='https://wyscout.com/', target="_blank"),
                        ". This is just a learning project made by a football fan ⚽ Looking forward to working in an Analytics company!"],
                 style={'margin-bottom': '7px'}),
])


# 4. CALLBACKS

# Updates Figure
@app.callback(Output(component_id='main_graph', component_property='figure'),
              [Input(component_id='players_dropdown', component_property='value'),
               Input(component_id='variables_dropdown', component_property='value')]
              )
def update_figure(input1, input2):
    fig = create_figure_players_comparison(main_df=main_df,
                                           players=input1,
                                           metrics=input2)

    #fig.layout.height = 500

    return fig

# Updates Players dropdown options
@app.callback(Output(component_id='players_dropdown', component_property='options'),
              [Input(component_id='teams_dropdown', component_property='value')]
              )
def update_figure(input3):
    new_list_players = []
    for team in input3:
        for player in main_df[main_df['Team'] == team]['Player']:
            new_list_players.append({'label': player, 'value': player})

    return new_list_players


if __name__ == '__main__':
    app.run_server(debug=False)