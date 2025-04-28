import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from urllib.request import urlopen

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash

from datetime import datetime

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

app.title = 'Visualization of Employment in Malaysia'

server = app.server


def tabs():
    tabs_layout = html.Div(
        [
            dbc.Tabs(
                [
                    dbc.Tab(label="Data Visualization of Employment Over Time", tab_id="tab-1", style={"font-size": "24px", "padding": "15px"}),
                    dbc.Tab(label="Labour Force Participation Rate by State Over Time", tab_id="tab-2", style={"font-size": "24px", "padding": "15px"}),
                    # dbc.Tab(label="Map View", tab_id="tab-3", style={"font-size": "24px", "padding": "15px"}),
                ],
                id="tabs",
                active_tab="tab-1",
                style={"height": "50px"},  # Optional: Adjust overall tab height
            ),
            html.Div(
                id="tabs-content",
                className="contents",
                style={"text-align": "center", "margin": "auto"},
            )
        ]
    )
    return tabs_layout

current_date = datetime.now().strftime("%B %d, %Y")

navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand(
                html.Div(
                    [
                        html.Div("Visualization of Employment in Malaysia", style={"font-size": "36px", "font-weight": "bold"}),
                        html.Div("by Robin Huang", style={"font-size": "24px", "color": "grey"}),
                    ],
                    style={"text-align": "center"}
                ),
                className="mx-auto",
            ),
            dbc.NavItem(
                html.Div(
                    current_date,
                    style={"font-size": "18px", "color": "white", "position": "absolute", "right": "10px", "top": "-15px", "white-space": "nowrap",},
                ),
                style={"position": "relative"}
            ),
        ]
    ),
    style={"height": "100px"},
    color="lightskyblue",
    dark=True,
)


df_emp = pd.read_csv("data/employment.csv")
df_lab = pd.read_csv("data/labor.csv")
df_pop = pd.read_csv("data/population_state.csv")
df_flood = pd.read_excel("data/flood_data.xlsx", sheet_name='EMData')

df_emp1 = df_emp.copy()
df_lab1 = df_lab.copy()

# Malaysia employment data graph
fig1 = go.Figure()
fig1.add_trace(
    go.Scatter(
        x = df_emp1[df_emp1["State/Country"] == "Malaysia"]["Year"],  
        y = df_emp1[df_emp1["State/Country"] == "Malaysia"]["Employed"],
        mode = 'lines+markers',
        name = "Malaysia"
    )
)

fig1.update_layout(
    title=f"Employment in Malaysia Over Time",
    xaxis_title="Year",
    yaxis_title="Employment",
    template="plotly_white",
    hovermode="x unified"
)

# Malaysia labour rate graph
fig2 = go.Figure()
fig2.add_trace(
    go.Scatter(
        x = df_lab1[df_lab1["State/Country"] == "Malaysia"]["Year"],  
        y = df_lab1[df_lab1["State/Country"] == "Malaysia"]["  Labour Force Participation Rate (Percentage)  "],
        mode = 'lines+markers',
        name = "Malaysia"
    )
)

fig2.update_layout(
    title=f"Labour Force Participation Rate in Malaysia Over Time",
    xaxis_title="Year",
    yaxis_title="Employment",
    template="plotly_white",
    hovermode="x unified"
)

df_emp = df_emp[(df_emp["State/Country"] != "Malaysia")] # drop country data as it can be sum up by aggregating the years
df_lab = df_lab[(df_lab["State/Country"] != "Malaysia")] # drop country data as it can be sum up by aggregating the years

df_lab["Labour Force Participation Rate (Percentage)"] = df_lab["  Labour Force Participation Rate (Percentage)  "]

def tab1():

    layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("Employment data overview in Malaysia"),
                dcc.Graph(id="emp-line-mala",figure = fig1)
            ])
        ]),
        dbc.Row([
            dbc.Col([
                html.H3("Interactive Line Graph of Employment Data in Malaysia"),
                dcc.Dropdown(
                    id='dropdown-state-1',
                    options=[
                        {'label': state, 'value': state}
                        for state in df_emp["State/Country"].unique()
                    ],
                    placeholder="Select a state",
                    style={'margin-bottom': '20px',
                    "width": "400px",
                    "margin": "0 auto",
                    "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.2)",  # Shadow for depth
                    "fontSize": "16px",  # Larger font for visibility
                    "color": "#000",}
                ),
                dcc.Graph(
                    id='emp-line-graph'
                    )
            ], width=12)
        ])
    ], fluid=True)

    return layout

def tab2():

    layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("Labour Force Participation Rate Overview in Malaysia"),
                dcc.Graph(id="part-line-mala",figure = fig2)
            ])
        ]),
        dbc.Row([
            dbc.Col([
                html.H3("Interactive Line Graph of Labour Participation Rate in Malaysia"),
                dcc.Dropdown(
                    id='dropdown-state-2',
                    options=[
                        {'label': state, 'value': state}
                        for state in df_emp["State/Country"].unique()
                    ],
                    placeholder="Select a state",
                    style={'margin-bottom': '20px',
                    "width": "400px",
                    "margin": "0 auto",
                    "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.2)",  # Shadow for depth
                    "fontSize": "16px",  # Larger font for visibility
                    "color": "#000",}  # Text color
                ),
                dcc.Graph(id='part-line-graph')
            ], width=12)
        ]),
    ], fluid=True)

    return layout



app.layout = html.Div([
        dbc.Row([
            navbar,
            tabs(),
            # tabs(),
            # licensebar
        ])
])


# select tab
@app.callback(
    Output("tabs-content", "children"), [Input("tabs", "active_tab")]
)
def select_tab(active_tab):
    if active_tab == "tab-1":
        return tab1()
    elif active_tab == "tab-2":
        return tab2()
    # elif active_tab == "tab-2":
    #     return tab2()
    # elif active_tab == "tab-3":
    #     return tab3()

# select the drop down of employment
@app.callback(
    Output('emp-line-graph', 'figure'),
    [Input('dropdown-state-1', 'value')]
)

def employment_line(state):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x = df_emp[df_emp["State/Country"] == state]["Year"],  
            y = df_emp[df_emp["State/Country"] == state]["Employed"],
            mode = 'lines+markers',
            name = state
        )
    )

    fig.update_layout(
        title=f"Employment in {state} Over Time",
        xaxis_title="Year",
        yaxis_title="Employment",
        template="plotly_white",
        hovermode="x unified"
    )

    return fig

# select the drop down of participate
@app.callback(
    Output('part-line-graph', 'figure'),
    [Input('dropdown-state-2', 'value')]
)

def employment_part(state):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x = df_lab[df_lab["State/Country"] == state]["Year"],  
            y = df_lab[df_lab["State/Country"] == state]["Labour Force Participation Rate (Percentage)"],
            mode = 'lines+markers',
            name = state
        )
    )

    fig.update_layout(
        title=f"Labour Force Participation Rate in {state} Over Time",
        xaxis_title="Year",
        yaxis_title="Labour Force Participation Rate",
        template="plotly_white",
        hovermode="x unified"
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
