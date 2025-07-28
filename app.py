import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import json
from datetime import datetime

# 数据加载和预处理
df_emp = pd.read_csv("data/employment.csv")
df_lab = pd.read_csv("data/labor.csv")
df_flood = pd.read_excel("data/flood_data.xlsx", sheet_name='EMData')

# 洪水数据处理
# 创建州名映射字典
state_mapping = {
    "Johor": "Johor", "Kedah": "Kedah", "Kelantan": "Kelantan", 
    "Melaka": "Melaka", "Negeri Sembilan": "Negeri Sembilan", 
    "Pahang": "Pahang", "Pulau Pinang": "Pulau Pinang", 
    "Perak": "Perak", "Perlis": "Perlis", "Selangor": "Selangor", 
    "Terengganu": "Terengganu", "Sabah": "Sabah", "Sarawak": "Sarawak",
    "W.P. Kuala Lumpur": "Kuala Lumpur", "W.P Labuan": "Labuan", 
    "W.P.Putrajaya": "Putrajaya"
}

# 反转映射字典用于反向查找
reverse_state_mapping = {v: k for k, v in state_mapping.items()}

# 解析Admin Units列并提取州名
def parse_admin_units(admin_str):
    try:
        units = json.loads(admin_str.replace("'", '"'))
        states = set()
        for unit in units:
            if 'adm1_name' in unit:
                state_name = unit['adm1_name']
                if state_name in reverse_state_mapping:
                    states.add(reverse_state_mapping[state_name])
            elif 'adm2_name' in unit:
                # 特殊处理县名到州名的映射
                county = unit['adm2_name']
                if county == "Kuala Lumpur":
                    states.add("W.P. Kuala Lumpur")
                elif county == "Labuan":
                    states.add("W.P Labuan")
                elif county == "Putrajaya":
                    states.add("W.P.Putrajaya")
                else:
                    # 通用县名处理 - 这里可以根据需要添加更多映射
                    if "Johor" in county:
                        states.add("Johor")
                    elif "Kedah" in county:
                        states.add("Kedah")
                    elif "Kelantan" in county:
                        states.add("Kelantan")
                    elif "Melaka" in county:
                        states.add("Melaka")
                    elif "Negeri Sembilan" in county:
                        states.add("Negeri Sembilan")
                    elif "Pahang" in county:
                        states.add("Pahang")
                    elif "Pulau Pinang" in county or "Penang" in county:
                        states.add("Pulau Pinang")
                    elif "Perak" in county:
                        states.add("Perak")
                    elif "Perlis" in county:
                        states.add("Perlis")
                    elif "Selangor" in county:
                        states.add("Selangor")
                    elif "Terengganu" in county:
                        states.add("Terengganu")
                    elif "Sabah" in county:
                        states.add("Sabah")
                    elif "Sarawak" in county:
                        states.add("Sarawak")
        return list(states)
    except:
        return []

# 应用解析函数
df_flood['Admin_States'] = df_flood['Admin Units'].apply(parse_admin_units)
df_flood['Start Year'] = df_flood['Start Year'].astype(int)

# 创建洪水事件数据
flood_events = []
for idx, row in df_flood.iterrows():
    year = row['Start Year']
    for state in row['Admin_States']:
        flood_events.append({
            'Year': year,
            'State/Country': state,
            'Disaster Type': row['Disaster Subtype'],
            'Total Affected': row['Total Affected'] if not pd.isna(row['Total Affected']) else 0
        })

df_flood_events = pd.DataFrame(flood_events)

# 准备就业和劳动力数据
df_emp1 = df_emp.copy()
df_lab1 = df_lab.copy()

# 马来西亚整体数据图表
fig1 = go.Figure()
fig1.add_trace(
    go.Scatter(
        x=df_emp1[df_emp1["State/Country"] == "Malaysia"]["Year"],
        y=df_emp1[df_emp1["State/Country"] == "Malaysia"]["Employed"],
        mode='lines+markers',
        name="Malaysia"
    )
)
fig1.update_layout(
    title="Employment in Malaysia Over Time",
    xaxis_title="Year",
    yaxis_title="Employment",
    template="plotly_white",
    hovermode="x unified"
)

fig2 = go.Figure()
fig2.add_trace(
    go.Scatter(
        x=df_lab1[df_lab1["State/Country"] == "Malaysia"]["Year"],
        y=df_lab1[df_lab1["State/Country"] == "Malaysia"]["  Labour Force Participation Rate (Percentage)  "],
        mode='lines+markers',
        name="Malaysia"
    )
)
fig2.update_layout(
    title="Labour Force Participation Rate in Malaysia Over Time",
    xaxis_title="Year",
    yaxis_title="Labour Force Participation Rate",
    template="plotly_white",
    hovermode="x unified"
)

# 移除国家层面的数据，保留州数据
df_emp = df_emp[df_emp["State/Country"] != "Malaysia"]
df_lab = df_lab[df_lab["State/Country"] != "Malaysia"]
df_lab["Labour Force Participation Rate (Percentage)"] = df_lab["  Labour Force Participation Rate (Percentage)  "]

# 创建Dash应用
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)
app.title = 'Visualization of Employment in Malaysia'
server = app.server

current_date = datetime.now().strftime("%B %d, %Y")

navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand(
                html.Div(
                    [
                        html.Div("Employment and Flood Impact Analysis in Malaysia", 
                                style={"font-size": "36px", "font-weight": "bold"}),
                        html.Div("by Robin Huang", style={"font-size": "24px", "color": "grey"}),
                    ],
                    style={"text-align": "center"}
                ),
                className="mx-auto",
            ),
            dbc.NavItem(
                html.Div(
                    current_date,
                    style={"font-size": "18px", "color": "white", "position": "absolute", 
                          "right": "10px", "top": "-15px", "white-space": "nowrap"}
                ),
                style={"position": "relative"}
            ),
        ]
    ),
    style={"height": "100px"},
    color="primary",
    dark=True,
)

def tabs():
    return html.Div(
        [
            dbc.Tabs(
                [
                    dbc.Tab(label="Employment Data with Flood Events", tab_id="tab-1", 
                           style={"font-size": "24px", "padding": "15px"}),
                    dbc.Tab(label="Labour Participation with Flood Events", tab_id="tab-2", 
                           style={"font-size": "24px", "padding": "15px"}),
                    dbc.Tab(label="Flood Impact Analysis", tab_id="tab-3", 
                           style={"font-size": "24px", "padding": "15px"}),
                ],
                id="tabs",
                active_tab="tab-1",
            ),
            html.Div(id="tabs-content", className="p-4")
        ]
    )

def tab1():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("Employment in Malaysia Over Time", className="text-center mb-4"),
                dcc.Graph(id="emp-line-mala", figure=fig1)
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.H3("State-level Employment with Flood Events", className="text-center mb-4"),
                dcc.Dropdown(
                    id='dropdown-state-1',
                    options=[{'label': state, 'value': state} 
                            for state in sorted(df_emp["State/Country"].unique())],
                    value="Johor",
                    style={'margin-bottom': '20px'}
                ),
                dcc.Graph(id='emp-line-graph')
            ], width=12)
        ])
    ], fluid=True)

def tab2():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("Labour Force Participation Rate in Malaysia", className="text-center mb-4"),
                dcc.Graph(id="part-line-mala", figure=fig2)
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.H3("State-level Participation Rate with Flood Events", className="text-center mb-4"),
                dcc.Dropdown(
                    id='dropdown-state-2',
                    options=[{'label': state, 'value': state} 
                            for state in sorted(df_lab["State/Country"].unique())],
                    value="Johor",
                    style={'margin-bottom': '20px'}
                ),
                dcc.Graph(id='part-line-graph')
            ], width=12)
        ]),
    ], fluid=True)

def tab3():
    # 准备洪水影响数据
    flood_impact = df_flood_events.groupby(['State/Country', 'Year']).agg(
        Flood_Count=('Disaster Type', 'count'),
        Total_Affected=('Total Affected', 'sum')
    ).reset_index()
    
    # 合并就业数据
    flood_impact = pd.merge(flood_impact, df_emp, 
                           on=['State/Country', 'Year'], 
                           how='left')
    
    # 创建洪水影响图表
    fig_flood = px.scatter(
        flood_impact,
        x='Year',
        y='Employed',
        size='Total_Affected',
        color='State/Country',
        hover_name='State/Country',
        hover_data=['Flood_Count', 'Total_Affected'],
        title='Employment vs Flood Impact by State and Year',
        labels={'Employed': 'Employment', 'Total_Affected': 'Total Affected by Floods'}
    )
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("Flood Impact on Employment", className="text-center mb-4"),
                dcc.Graph(figure=fig_flood)
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.H4("Flood Events Summary", className="text-center mt-4"),
                html.Div(id='flood-summary-table', className="mt-3")
            ], width=12)
        ])
    ], fluid=True)

app.layout = html.Div([
    navbar,
    tabs()
])

@app.callback(
    Output("tabs-content", "children"),
    [Input("tabs", "active_tab")]
)
def select_tab(active_tab):
    if active_tab == "tab-1":
        return tab1()
    elif active_tab == "tab-2":
        return tab2()
    elif active_tab == "tab-3":
        return tab3()

@app.callback(
    Output('emp-line-graph', 'figure'),
    [Input('dropdown-state-1', 'value')]
)
def employment_line(state):
    state_data = df_emp[df_emp["State/Country"] == state]
    flood_years = df_flood_events[
        (df_flood_events["State/Country"] == state) & 
        (df_flood_events["Year"].between(state_data['Year'].min(), state_data['Year'].max()))
    ]['Year'].unique()
    
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=state_data["Year"],
            y=state_data["Employed"],
            mode='lines+markers',
            name=state,
            line=dict(color='royalblue', width=3)
        )
    )
    
    # 添加洪水事件标记
    for year in flood_years:
        flood_data = df_flood_events[(df_flood_events["State/Country"] == state) & (df_flood_events["Year"] == year)]
        for _, event in flood_data.iterrows():
            fig.add_vline(
                x=year, 
                line=dict(color='red', width=2, dash='dash'),
                annotation_text=f"Flood: {event['Disaster Type']}",
                annotation_position="top right",
                annotation_textangle = 60
            )
    
    fig.update_layout(
        title=f"Employment in {state} with Flood Events",
        xaxis_title="Year",
        yaxis_title="Employment",
        template="plotly_white",
        hovermode="x unified",
        showlegend=False
    )
    
    return fig

@app.callback(
    Output('part-line-graph', 'figure'),
    [Input('dropdown-state-2', 'value')]
)
def employment_part(state):
    state_data = df_lab[df_lab["State/Country"] == state]
    flood_years = df_flood_events[
        (df_flood_events["State/Country"] == state) & 
        (df_flood_events["Year"].between(state_data['Year'].min(), state_data['Year'].max()))
    ]['Year'].unique()
    
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=state_data["Year"],
            y=state_data["Labour Force Participation Rate (Percentage)"],
            mode='lines+markers',
            name=state,
            line=dict(color='green', width=3)
        )
    )
    
    # 添加洪水事件标记
    for year in flood_years:
        flood_data = df_flood_events[(df_flood_events["State/Country"] == state) & (df_flood_events["Year"] == year)]
        for _, event in flood_data.iterrows():
            fig.add_vline(
                x=year, 
                line=dict(color='red', width=2, dash='dash'),
                annotation_text=f"Flood: {event['Disaster Type']}",
                annotation_position="top right",
                annotation_textangle = 60
            )
    
    fig.update_layout(
        title=f"Labour Force Participation Rate in {state} with Flood Events",
        xaxis_title="Year",
        yaxis_title="Labour Force Participation Rate",
        template="plotly_white",
        hovermode="x unified",
        showlegend=False
    )
    
    return fig

@app.callback(
    Output('flood-summary-table', 'children'),
    [Input('tabs', 'active_tab')]
)
def update_flood_summary(active_tab):
    if active_tab != "tab-3":
        return dash.no_update
    
    # 获取受洪水影响最严重的5个州
    top_states = df_flood_events.groupby('State/Country')['Total Affected'].sum().nlargest(5).reset_index()
    
    # 获取洪水事件最多的5个年份
    top_years = df_flood_events.groupby('Year')['Total Affected'].sum().nlargest(5).reset_index()
    
    # 创建表格
    states_table = dbc.Table(
        [
            html.Thead(html.Tr([html.Th("State"), html.Th("Total Affected")])),
            html.Tbody([
                html.Tr([html.Td(state), html.Td(f"{affected:,.0f}")])
                for _, (state, affected) in top_states.iterrows()
            ])
        ],
        bordered=True,
        hover=True,
        responsive=True,
        className="mt-3"
    )
    
    years_table = dbc.Table(
        [
            html.Thead(html.Tr([html.Th("Year"), html.Th("Total Affected")])),
            html.Tbody([
                html.Tr([html.Td(year), html.Td(f"{affected:,.0f}")])
                for _, (year, affected) in top_years.iterrows()
            ])
        ],
        bordered=True,
        hover=True,
        responsive=True,
        className="mt-3"
    )
    
    return html.Div([
        html.H5("Top 5 Most Affected States", className="mt-4"),
        states_table,
        html.H5("Top 5 Most Affected Years", className="mt-4"),
        years_table
    ])

if __name__ == '__main__':
    app.run_server(debug=True)