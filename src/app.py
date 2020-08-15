import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np

# This code creates a Dash App to visualise football players stats.
# I've used a database with random values for each player because I don't have the actual ones.
# The app is deployed on Heroku following this tutorial: https://dash.plotly.com/deployment


# First, we define some help functions
def read_dataset(data_filename):
    """Read file from directory <data_filename>.

    Args:
        data_filename : path to data file (at the moment, only accepts excel files)

    Returns:
        main_df : pandas dataframe

    """

    # Read data from excel file. 
    main_df = pd.read_excel(data_filename)

    return main_df

def dropdown_options_leagues_metrics(main_df, leagues_df):
    """Creates list of dropdown options (dictionaries {'label':<value>, 'value':<value>)
    for leagues and metrics dropdowns. The other dropdowns (teams and players) are created via Callbacks.

    Args:
        main_df : pandas dataframe with the full dataset for every player
        leagues_df : pandas dataframe with lookup table for teams and leagues.

    Returns:
        2 lists : list_leagues, list_metrics containing dictionaries for the dropdown options
    """

    # Leagues
    list_leagues=[]
    for league in list(leagues_df['league'].unique()):
        list_leagues.append({'label': league, 'value': league}) # This dictionary format is specified by the Dash documentation

    # Metrics
    list_metrics = []
    for metric in np.sort(main_df.columns): # Sort to get the metrics in alphabetical order

        if metric not in ['Team','Player', 'index']:
            list_metrics.append({'label': metric, 'value': metric})

    return list_leagues, list_metrics

def create_figure_radar(main_df, players, metrics):
    """Creates radar chart based on players and metrics selected by the user.

    Args:
        main_df : pandas dataframe with the full dataset for every player
        players : list with players names
        metrics : list with metrics to compare in the radar chart

    Returns:
        plotly radar chart figure

    """

    # Create the figure
    fig = go.Figure()

    # Loop to create one trace for each player
    for player in players:

        # Initialise empty lists
        norm_values_list = []  # Normalised values from 0 to 1, for each metric.
        actual_values_list = []  # Actual values to display when hovering over the point

        # For each player, loop through each metric
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
        autosize=True, # Allows chart to be responsive
        font=dict(family='Helvetica',
                  color='black')
    )

    return fig


# Main code
### 1. READ DATA
main_df = read_dataset(data_filename='./assets/data.xlsx')

### 2. GET DEFAULT DROPDOWN VALUES, DROPDOWN OPTIONS AND CREATE DEFAULT FIGURE
# Get all possible values
leagues_df = pd.read_csv('./assets/leagues_teams.csv')
list_leagues, list_metrics = dropdown_options_leagues_metrics(main_df, leagues_df)
# Select default dropdown values
default_leagues_values = ['La Liga', 'Serie A']
default_teams_values = ['Barcelona', 'Juventus']
default_players_values = ['L. Messi', 'Cristiano Ronaldo']
default_metrics_values = ['Interceptions / 90 min','Non-penalty goals / 90 min','Assists / 90 min',
                   'Crosses / 90 min','Dribbles / 90 min','Passes / 90 min']
# Create Figure
fig_default = create_figure_radar(main_df=main_df,
                                players=default_players_values,
                                metrics=default_metrics_values)

### 3. DASH APP
# Import css stylesheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# Create App
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Players comparison"
server = app.server
# Create Layout
app.layout = html.Div(children=[

    html.Div(children=[
                    html.Img(src=app.get_asset_url('logo1.jpg'),
                             style = {
                                      'height': '50px',
                                      'width': 'auto',
                                      'margin-bottom': '10px'
                                      },
                             ),

                    html.H1(id='main_header',
                            children=html.Div(['Player comparator ',
                                               html.Span("I've used a database with random values for each player because I don't have the actual ones.", style={'color': 'rgb(176, 176, 176)',
                                                                       'font-size':20}),
                                                ]),
                            style={
                                'textAlign': 'left',
                                'color': 'rgb(51, 63, 80)',
                                'font-size': 40,
                                'font-family': 'Helvetica',
                                'line-height': 55,
                                'margin-bottom': '5px'

                            },
                            ),

                        ]

    ),

    html.Div(children=['Looking for my first job as a Data Analyst. Contact me on ',
                       html.A('LinkedIn', href='https://www.linkedin.com/in/david-fernandez-11a715170/', target="_blank"),
                       '. Download my ',
                       html.A('CV', href='https://drive.google.com/uc?export=download&id=15VHG_EazFeaOA3Iqd-9kN043SuHIw4PE',target="_blank"),
                       '. Find the code on my ',
                       html.A('Github', href='https://github.com/davidferg/players-comparison', target="_blank"),
                       '.'],
             style={'margin-bottom': '20px'}),

    html.P(children=['Select leagues'],
               style={'fontSize': '100%',
                      'font-family': 'Helvetica'
                      }
               ),

    dcc.Dropdown(
            id='leagues_dropdown',
            options = list_leagues,
            multi=True,
            value=default_leagues_values,
            placeholder="Select leagues",
            optionHeight=20,
            style={'margin-bottom': '10px'}

        ),

    html.P(children=['Select teams'],
           style={'fontSize': '100%',
                  'font-family': 'Helvetica'
                  }
           ),

    dcc.Dropdown(
        id='teams_dropdown',
        multi=True,
        value=default_teams_values,
        placeholder="Select teams",
        optionHeight=20,
        style={'margin-bottom': '10px'}

    ),

    html.P(children=['Select players'],
           style={'fontSize': '100%',
                  'font-family': 'Helvetica'
                  }
           ),

    dcc.Dropdown(
        id='players_dropdown',
        multi=True,
        value=default_players_values,
        placeholder="Select players to compare",
        optionHeight=20,
        style={'margin-bottom': '10px'}
    ),

    html.P(children=['Select metrics'],
           style={'fontSize': '100%',
                  'font-family': 'Helvetica'
                  }
           ),

    dcc.Dropdown(
        id='metrics_dropdown',
        options=list_metrics,
        multi=True,
        value=default_metrics_values,
        placeholder="What do you want to compare?",
        optionHeight=20,
        style={'margin-bottom': '2px'}
    ),

    dcc.Graph(
        id='main_graph',
        figure=fig_default,
        config={'displayModeBar': False}
    ),

    html.P(children=['Notes: Only players from the Top 5 EU leagues.'],
               style={'fontSize': '5',
                      'color': 'rgb(176, 176, 176)',
                      'font-family': 'Helvetica'
                      }
               ),

    html.Div(children=["This is just a learning project made by a football fan ⚽ Looking forward to working in an Analytics company! davidfergui10@gmail.com"],
                 style={'fontSize': '5'}),
])


# 4. CALLBACKS

# Updates Figure
@app.callback(Output(component_id='main_graph', component_property='figure'),
              [Input(component_id='players_dropdown', component_property='value'),
               Input(component_id='metrics_dropdown', component_property='value')]
              )
def update_figure(input1, input2):
    """Runs when values change in players or metrics dropdown and updates radar figure"""
    fig = create_figure_radar(main_df=main_df,
                                           players=input1,
                                           metrics=input2)

    return fig

# Updates Teams dropdown options
@app.callback(Output(component_id='teams_dropdown', component_property='options'),
              [Input(component_id='leagues_dropdown', component_property='value')]
              )
def update_dropdown(input3):
    """Runs when values change in leagues dropdown and updates teams dropdown options"""
    new_list_teams = []
    for team in leagues_df[leagues_df['league'].isin(input3)]['team'].sort_values().to_list():
        new_list_teams.append({'label': team, 'value': team})

    return new_list_teams

# Updates Players dropdown options
@app.callback(Output(component_id='players_dropdown', component_property='options'),
              [Input(component_id='teams_dropdown', component_property='value')]
              )
def update_dropdown(input4):
    """Runs when values change in teams dropdown and updates players dropdown options"""
    new_list_players = []
    for team in main_df[main_df['Team'].isin(input4)]['Player'].sort_values().to_list():
        new_list_players.append({'label': team, 'value': team})

    return new_list_players




if __name__ == '__main__':
    app.run_server(debug=False)
