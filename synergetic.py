import os
import pathlib
import numpy as np
import datetime as dt
import dash
# import dash_core_components as dcc
from dash import dcc
# import dash_html_components as html
from dash import html
import pandas as pd
from scipy import stats

from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from scipy.stats import rayleigh
from db_query import get_24_hours_data
import time
import datetime as dt
import plotly.express as px
import plotly.graph_objs as go
# import dash_table
from dash import dash_table


GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 900000)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,compress=False)

server = app.server

app_color = {"graph_bg": "#fafafa", "graph_line": "#007ACE"}

def get_current_time():

    now = dt.datetime.now()
    now_seconds = time.mktime(now.timetuple())
    return now_seconds

app.layout = html.Div([

        # header
        html.Div(
            [
                html.Div([
                        html.A(
                            html.Img(
                                src='/assets/image.png',
                                className="four columns app__menu__img",
                            ),
                        ),
                    ], style={'width': '50%', 'display': 'inline-block', 'hight': '30%'},
                ),

                html.Div([

                        html.Div([html.Label('Товарная категория', style={'fontWeight': 'bold'}), 
                                    dcc.Dropdown(
                                            #options=[{'label': k, 'value': k} for k in products_dict.keys()],
                                            #value = products_dict.keys()[0],
                                            id = 'category_dropdown',
                                            #multi=True
                                        ),
                                    ],
                                    className="four columns",
                                ),

                        html.Div([html.Label('Приоритет товаров', style={'fontWeight': 'bold'}), 
                                        dcc.Dropdown(
                                            id = 'product_dropdown',
                                            style={
                                                        'height': '30px',
                                                        },
                                            #optionHeight=120,
                                        ),
                                    ], className="four columns",
                                ),

                        html.Div([html.Label('Приоритет search string', style={'fontWeight': 'bold'}), 
                                        dcc.Dropdown(
                                            id = 'priority_dropdown',
                                            #multi=True
                                        ),
                                    ], className="four columns",
                                ),
                            ], 
                        style={'width': '50%', 'display': 'inline-block', 'hight': '30%'},
                        className="graph__container first",
                        ),

            ],
            className="app__header",
        ),

        html.Br(),
        html.Div([
                html.Div([html.Label('Сводка', style={'fontWeight': 'bold', 'marginLeft': "3%"}), 
                    ], style={'width': '50%', 'display': 'inline-block', 'hight': '30%'},
                ),

                html.Div([html.Label('Выберете позицию товара', style={'fontWeight': 'bold'}), 
                          dcc.RangeSlider(0, 100, step=None,
                                     marks={0: '',
                                            6: '6',
                                            12: '12',
                                            36: '36',
                                            72: '72',
                                            100: ''
                                        },
                                     value=[0, 100],
                                     id='my-slider')], 
                          style={'width': '50%', 'display': 'inline-block', 'hight': '30%'},
                ),

            ],
            className="twelve columns",
        ),

        html.Div([
                html.Div([

                        # dcc.Graph(
                        #             id = 'indicator_delta'
                        #     ), 
                        html.Label(id='delta_moda', style={'textAlign': 'center', "fontSize": "30px"}),
                        html.Label('Мода позиции с дельтой изменений', style={'fontWeight': 'bold', 'textAlign': 'center'})], 
                        style={'width': '25%', 'display': 'inline-block', 'hight': '30%'}),

                html.Div([
                          # dcc.Graph(
                          #           id = 'indicator'
                          #   ), 
                          html.Label(id='percent_of_position', style={'textAlign': 'center', "fontSize": "30px"}),
                          html.Label('Товаров в диапазоне от 1 до 36', style={'fontWeight': 'bold', 'textAlign': 'center'})],
                          style={'width': '25%', 'display': 'inline-block', 'hight': '30%'},
                ),

            ],
            className="twelve columns",
        ),
        html.Br(),
        html.Br(),
        html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),
        html.Div([
                html.Div([
                        html.Label('Динамика изменения позиции', style={'fontWeight': 'bold', 'marginLeft': "3%"}), 
                        dcc.Graph(
                            id="wind-speed",
                            # figure=dict(
                            #    layout=go.Layout(margin={'t': 0, 'l': 0}
                            #    )
                            # ),
                        ),
                        dcc.Interval(
                            id="wind-speed-update",
                            interval=int(GRAPH_INTERVAL),
                            n_intervals=0,
                        ),
                        dcc.Store(id="stored", data={}),
                        # html.Div(id="status"),
                    ], style={'width': '50%', 'display': 'inline-block', 'hight': '30%'},
                ),

                html.Div([
                        html.Button("Отменить выбор товара", id="clear"),
                        html.Br(), html.Br(),
                        dash_table.DataTable(
                            id='table',
                            columns=[ 
                                    dict(name='Товар', id='name'),
                                    dict(name='itemId', id='id'),
                                    dict(name='Позиция t', id='position_last'),
                                    dict(name='Позиция t-1', id='position_prev'),
                                    dict(name='Дельта позиции', id='delta', type='numeric')],
                            page_action='none',
                            style_table={'height': '420px', 'overflowY': 'auto'},
                            style_data={
                                        'whiteSpace': 'normal',
                                        'height': 'auto',},
                            #filter_action='native',
                            style_cell={'textAlign': 'left', 'fontFamily':'Open Sans'},
                            style_header={'fontWeight': 'bold', 'textAlign': 'center', "fontSize": "15px",
                            'padding':'10px'},
                        )

                    ], style={'width': '50%', 'display': 'inline-block'},
                ),

            ],
            className="twelve columns",
        ),

        html.Div([
            html.Div([
                        dash_table.DataTable(
                            id='table_2',
                            columns=[ 
                            {'name': 'SKU', 'id': 'SKU'},
                            {'name': 'Приоритет SKU', 'id': 'Приоритет SKU'},
                            {'name': 'Title', 'id': 'Title'},
                            {'name': 'Avg. Position', 'id': 'Avg. Position'},
                            {'name': 'Avg. Position Delta', 'id': 'Avg. Position Delta'},
                            {'name': 'Потрачено в рекламе', 'id': 'Потрачено в рекламе'}],
                            page_action='none',
                            style_table={'height': '420px', 'overflowY': 'auto'},
                            style_data={'whiteSpace': 'normal',
                                        'height': 'auto',},
                            filter_action='native',
                            style_cell={'textAlign': 'left'},
                            style_header={'fontWeight': 'bold', 'textAlign': 'center',
                            'padding':'10px'},
                        )

                    ], style={'width': '100%', 'display': 'inline-block'},
                ),

            ],
            className="twelve columns",
        ),

    ],
    className="app__container",
)

def find_mode(x):
    return stats.mode(x)[0]

# обновление дропдауна категорий
@app.callback(
    [Output('category_dropdown', 'options'),
    Output('category_dropdown', 'value')],
    [
     Input('wind-speed-update', 'n_intervals'),
     Input("stored", "data")])

def set_category_value(_, data):
    df = pd.DataFrame(data)
    products_dict = {}
    products_groupby = df.groupby('products_category').agg({'name': 'unique'}).reset_index()
    for i in products_groupby.index:
        value = products_groupby.loc[i, 'name']
        key = products_groupby.loc[i, 'products_category']
        products_dict[key] = list(value)

    options = [{'label': i, 'value': i} for i in products_dict.keys()]
    return options, \
           options[0]['value']

# обновление дропдауна приоритета
@app.callback(
    [Output('product_dropdown', 'options'),
    Output('product_dropdown', 'value')],
    [Input('category_dropdown', 'value'),
     Input('wind-speed-update', 'n_intervals'),
     Input("stored", "data")])

def set_product_value(selected_category, _, data):

    df = pd.DataFrame(data)
    df = df[["products_category", "products_priority"]]
    df = df.dropna()
    df = df.groupby(['products_category','products_priority']).size().reset_index().rename(columns={0:'count'})
    products_dict = {}
    products_groupby = df.groupby('products_category').agg({'products_priority': 'unique'}).reset_index()
    for i in products_groupby.index:
        value = products_groupby.loc[i, 'products_priority']
        key = products_groupby.loc[i, 'products_category']
        products_dict[key] = list(value)

    options = [{'label': i, 'value': i} for i in products_dict[selected_category]]
    return options, \
           options[0]['value']

@app.callback(
   [Output('priority_dropdown', 'options'),
   Output('priority_dropdown', 'value')],
   Input('category_dropdown', 'value'),
   Input('product_dropdown', 'value'),
   Input('wind-speed-update', 'n_intervals'),
   Input("stored", "data"))

def set_priority_value(selected_category, selected_product_priority, _, data):
    df = pd.DataFrame(data)
    df = df[['products_category', "products_priority", "keywords_priority"]]
    df = df.dropna()
    df = df.groupby(['products_category', 'products_priority','keywords_priority']).size().reset_index().rename(columns={0:'count'})
    priority_keywords_by_products = df.groupby(['products_category', 'products_priority']).agg({'keywords_priority': 'unique'}).reset_index()
    priority_keywords_by_products_dict = {}
    for i in priority_keywords_by_products.index:
        key_first = priority_keywords_by_products.loc[i, 'products_category']
        key_second = priority_keywords_by_products.loc[i, 'products_priority']
        value = priority_keywords_by_products.loc[i, 'keywords_priority']
        priority_keywords_by_products_dict.setdefault(key_first, {})
        priority_keywords_by_products_dict[key_first][key_second] = list(value)
    options = [{'label': i, 'value': i} for i in priority_keywords_by_products_dict[selected_category][selected_product_priority]]
    return options, \
            options[0]['value']


@app.callback(Output("stored", "data"),
              Input("wind-speed-update","n_intervals")
)
def get_df(n):

    now_seconds = get_current_time()
    df = get_24_hours_data(now_seconds - 87300, now_seconds)

    return df.to_dict('records')

@app.callback(
    [Output("wind-speed", "figure"),
    Output("table", "data"),
    Output('table', 'style_data_conditional'),
    Output('percent_of_position', 'children'),
    Output('delta_moda', 'children')], [
                                     Input("stored", "data"),
                                     Input('category_dropdown', 'value'),
                                     Input('my-slider', 'value'),
                                     Input('priority_dropdown', 'value'),
                                     Input('product_dropdown', 'value'),
                                     Input('table', 'active_cell')]
)
def dynamics(data, selected_category, slider_value, keywords_priority, products_priority, active_cell):
    df = pd.DataFrame(data)

    time_max = df['time'].max()
    time_prev = sorted(df['time'].unique())[-2]
    if not keywords_priority:
        print('ha')
    else:
        df = df.query('keywords_priority == @keywords_priority')
    df_query = df.query('time == @time_max & products_category == @selected_category & products_priority == @products_priority')
    if slider_value[1] == 100:
        slider_value[1] = df['position'].max()
    df_with_slider_query = df_query.query('@slider_value[0] <= position <= @slider_value[1]')
    df_id = df_with_slider_query['id'].unique()
    df_mode = df.query('id in @df_id & products_category == @selected_category & products_priority == @products_priority').groupby('time').agg({'position': find_mode}).reset_index()

    position_previous = [np.nan] + [x for x in df_mode['position'][:-1]]
    df_mode['position_previous'] = position_previous

    if active_cell is not None:
        row = active_cell["row_id"]
        col = active_cell["column_id"]
        df_query_cell = df.query('id == @row')
        df_query_cell = df_query_cell.sort_values(by='time').groupby('time').agg({'position': find_mode}).reset_index()

        position_previous = [np.nan] + [x for x in df_query_cell['position'][:-1]]
        df_query_cell['position_previous'] = position_previous
        df_graph = df_query_cell
    else:
        df_graph = df_mode

    fig = go.Figure(go.Candlestick(x=df_graph['time'],
                open=df_graph['position'],
                high=df_graph['position'],
                low=df_graph['position_previous'],
                close=df_graph['position_previous']))

    layout = dict(margin=go.layout.Margin(
        l=20, #left margin
        t=0, #top margin
        r=20, #top margin
        ),
        #plot_bgcolor=app_color["graph_bg"],
        #paper_bgcolor=app_color["graph_bg"],
        #font={"color": "#fff"},
        height=500,
        xaxis_rangeslider_visible=False,
        # paper_bgcolor="#F4F4F8",
        # plot_bgcolor="#F4F4F8",
    )
    fig.update_layout(layout)
    
    percent_in_first_page = round((df_with_slider_query.query('1 <= position <= 36')['name'].nunique() / df_with_slider_query['name'].nunique())*100, 2)
    percent_in_first_page_text = str(percent_in_first_page) + '%'
    df_query_prev = df.query('time == @time_prev & products_category == @selected_category & products_priority == @products_priority')
    percent_in_first_page_prev = (df_query_prev.query('1 <= position <= 36')['name'].nunique() / df_query_prev['name'].nunique())*100

    # заполнение data table 
    # Здесь условие if, потому что у категорий ПММ и Стирка для одного приоритета search string может быть два ключевых слова, поэтому надо брать моду
    if len(df_with_slider_query) != 0:
        df_query = df_with_slider_query[['name', 'id', 'position']].drop_duplicates().groupby(['name', 'id']).agg({'position': find_mode}).reset_index()
        df_query_prev_with_slider = df_query_prev.query('@slider_value[0] <= position <= @slider_value[1]')[['name', 'id', 'position']].drop_duplicates().groupby(['name', 'id']).agg({'position': find_mode}).reset_index()
        df_data_table = df_query.merge(df_query_prev_with_slider, on=['id', 'name'], suffixes=('_last', '_prev'))
        df_data_table['delta'] = df_data_table['position_last'] - df_data_table['position_prev']
    else:
        df_query = df_with_slider_query[['name', 'id', 'position']].drop_duplicates()
        df_query_prev_with_slider = df_query_prev.query('@slider_value[0] <= position <= @slider_value[1]')[['name', 'id', 'position']].drop_duplicates()
        df_data_table = df_query.merge(df_query_prev_with_slider, on=['id', 'name'], suffixes=('_last', '_prev'))
        df_data_table['delta'] = df_data_table['position_last'] - df_data_table['position_prev']
        #df_data_table['delta'] = df_data_table['delta'].apply(lambda x: -x if x > 0 else abs(x))

    moda_value_last = str(df_graph.query('time == @time_max')['position'].values[0])
    indicator_delta = df_graph.query('time == @time_max')['position'].values[0] - df_graph.query('time == @time_prev')['position'].values[0]
    if indicator_delta > 0:
        indicator_delta = '+' + str(indicator_delta)
    indicator_delta_value = f'{moda_value_last} ({indicator_delta})'

    style_data_conditional = [
                            {
                                'if': {
                                    'filter_query': '{delta} >= 1',
                                    'column_id': 'delta'
                                },
                                'backgroundColor': 'tomato',
                                'color': 'white'
                            },
                            {
                                'if': {
                                    'filter_query': '{delta} <= -1',
                                    'column_id': 'delta'
                                },
                                'backgroundColor': '#4da35d',
                                'color': 'white'
                            }] + [
                            {
                            'if': {'column_id': c},
                            'textAlign': 'center'
                            } for c in ['id', 'position_last', 'position_prev', 'delta']]

    return fig, \
           df_data_table.to_dict('records'), \
           style_data_conditional, \
           percent_in_first_page_text, \
           indicator_delta_value


@app.callback(
    Output("table", "selected_cells"),
    Output("table", "active_cell"),
    Input("clear", "n_clicks"),    
)
def clear(n_clicks):
    return [], None

# @app.callback(
#     [Output("wind-speed", "figure")], 
#     [Input('table', 'active_cell'),
#     Input('priority_dropdown', 'value')])

# def active_tabel(active_cell, key_priority):
#     if active_cell is None:
#         return no_update
#     row = active_cell["row_id"]
#     print(f"row id: {row}")

if __name__ == "__main__":
    app.run_server(debug=True)
