# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_treeview_antd
import dash.dependencies
import plotly.graph_objects as go
import numpy as np
import flask
import pandas as pd
import sys

import mivesfreqlines as mf

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

from sys import getsizeof

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)
app.title = 'MIVES - Resultado de padrões métricos em obras literárias'


def init_data(numlivro):
    global titulo
    global frases
    global escan
    if numlivro is not None:
        livro = numlivro
        titulo = mylivros['titulo'][livro]
        frases, escan = mf.load_sentencas(livro, janela)
        # print('frases size:{}'.format(getsizeof(frases)))
        # print('escan size:{}'.format(getsizeof(escan)))
    else:
        numlivro = -1
        titulo = ''
        frases = pd.DataFrame()
        escan = {}
    return


# inicialização de dados
janela = 200
passo = 20
mylivros = mf.get_listalivros()
titulo = None
frases = None
escan = None
init_data(None)


def get_linechart():
    # print(frases.dtypes)

    linhasrem = frases.index[np.arange(len(frases['freqj'])) % passo == 0] - 1  # index = linha - 1
    freqjp = frases['freqj'].iloc[linhasrem]  # seleciona valores de 20 em 20
    linhasp = frases['linha'].iloc[linhasrem]  # seleciona valores de 20 em 20
    inifim = list(zip(frases['sent_ini_freq'].iloc[linhasrem], frases['sent_fim_freq'].iloc[linhasrem]))

    fig = {
        "data": [{
            "type": "scatter",
            "x": linhasp,
            "y": freqjp,
            "customdata": inifim,
            "mode": "lines+markers",
            "marker": {"symbol": "square"},
            "hovertemplate": "Sentença de Referência: %{x}<br>Qtd. métricas(200 anteriores):%{y} <extra></extra>",
            "hoverlabel": {"bgcolor": "white"},
            "line": {"color": "black"}
        }],
        "layout": {
            "title": {
                "text": 'Distribuição das frequências absolutas das estruturas métricas a cada 200 sentenças<br>'
                        + titulo,
                "xanchor": "center",
                "x": 0.5,
                "font_color": "black"
            },
            "plot_bgcolor": "white",
            "xaxis": {"title": {"text": "sentenças", "font_color": "black"}, "gridcolor": "lightgrey"},
            "yaxis": {"title": {"text": "frequência", "font_color": "black"}, "gridcolor": "lightgrey"}
        }
    }

    return fig


def get_treeview():
    fig = dash_treeview_antd.TreeView(
        id='tree_sentencas',
        multiple=False,
        checkable=False,
        checked=[],
        selected=[],
        expanded=['0'],
        data={}

        # {
        #     'title': 'Sentenças no intervalo',
        #     'key': '0',
        #     'children':[
        #         {
        #             'title': '1 - s1',
        #             'key': '0-1'
        #         },
        #         {
        #             'title': '2 - s2',
        #             'key': '0-2'
        #         }
        #      ]
        # }# data virá de create_treedata no callback inicial
    )

    return fig


def create_tree_escansoes(index, linha):
    children = []

    df = escan[(escan['linha'] == linha) & (escan['metro'] != -1)]
    lista = ["{} :: {}".format(row['metro'], row['escansao']) for index, row in df.iterrows()]

    if not lista:  # empty
        lista.append("(escansão não encontrada)")
        print("Escansão não encontrada! linha ", linha, file=sys.stderr)

    treekey = 1
    for item in lista:
        children.append({
            'title': item,
            'key': '0-{}-{}'.format(index, treekey)
        })
        treekey += 1

    # [{'title': 'escansão da sentença 1 com 10 sílabas /#', 'key': '0-{}-1'.format(index)},
    # {'title': 'escansão da sentença 1 com 11 sílabas /#', 'key': '0-{}-2'.format(index)},
    # {'title': 'escansão da sentença 1 com 12 sílabas /#', 'key': '0-{}-3'.format(index)}]

    return children


def create_treedata(numsentenca, freq):
    intervalo = frases.loc[
        (
                (numsentenca[0] <= frases['linha'])
                & (frases['linha'] <= numsentenca[1])
                & (frases['metrico?'] == 1)
        ),
        ['linha', 'sentenca']
    ]
    d = []
    for index, row in intervalo.iterrows():
        d.append({
            'title': '{} - {}'.format(row['linha'], row['sentenca']),
            'key': '0-{}'.format(index),
            'children': create_tree_escansoes(index, row['linha'])
        })
    # print(d)
    return {'title': '{} sentenças'.format(freq), 'key': '0', 'children': d}


def carrega_pagina():
    return html.Div(className='container', children=[
        html.H1(
            children='MIVES Dashboard de Resultados',
            style={'textAlign': 'center'}
        ),

        html.Div(
            [
                dcc.Dropdown(
                    id='dropdownlivros',
                    options=[{'label': liv, 'value': i} for i, liv in enumerate(mylivros['titulo'])],
                    # value='0',
                    # clearable=False,
                    placeholder="Selecione um livro..."
                ),
            ],
            style={'width': '100%', 'display': 'inline-block'}),

        dcc.Loading(id="loading-icon1",
                    children=[
                        html.Div(
                            dcc.Graph(
                                id='graficofreq',
                                figure={}  # go.Figure(get_linechart())
                            )
                        ),
                        html.Div(
                            id='instrucao',
                            children='',
                            style={'textAlign': 'center'}
                        ),
                    ], type="default"),

        dcc.Loading(id="loading-icon2",
                    children=[
                        html.Div([
                            html.H6(
                                id='titulo_inferior',
                                children='Sentenças métricas',
                                style={'textAlign': 'center'}
                            ),

                            # html.Div([
                            #     dcc.Markdown(d("""
                            #             **Click Data**
                            #
                            #             Click on points in the graph.
                            #         """)),
                            #     html.Pre(id='click-data', style=styles['pre']),
                            # ], className='three columns'),

                            html.Div(
                                children=[
                                    html.Hr(),
                                    get_treeview(),
                                    html.Hr()
                                ])
                        ])

                    ], type="default")
    ])


#
# load layout before callbacks to avoid dash.exceptions.LayoutIsNotDefined
app.layout = carrega_pagina()


@app.callback(
    dash.dependencies.Output('graficofreq', 'figure'),
    [dash.dependencies.Input('dropdownlivros', 'value')])
def update_graph(value):
    if value is not None:
        init_data(value)
        return get_linechart()
    else:
        return {
            "data": [{
                "type": "scatter",
                "x": [],
                "y": [],
                "customdata": [],
                "mode": "lines+markers",
                "marker": {"symbol": "square"},
                "hovertemplate": "Sentença de Referência: %{x}<br>Qtd. métricas(200 anteriores):%{y} <extra></extra>",
                "hoverlabel": {"bgcolor": "white"},
                "line": {"color": "black"}
            }],
            "layout": {
                "title": {
                    "text": 'Distribuição das frequências absolutas das estruturas métricas a cada 200 sentenças<br>',
                    "xanchor": "center",
                    "x": 0.5,
                    "font_color": "black"
                },
                "plot_bgcolor": "white",
                "xaxis": {"title": {"text": "sentenças", "font_color": "black"}, "gridcolor": "lightgrey"},
                "yaxis": {"title": {"text": "frequência", "font_color": "black"}, "gridcolor": "lightgrey"}
            }
        }



@app.callback(
    dash.dependencies.Output('tree_sentencas', 'data'),
    [dash.dependencies.Input('graficofreq', 'clickData'),
     dash.dependencies.Input('dropdownlivros', 'value')]
)
def update_tree(click_data, value):
    ctx = dash.callback_context
    if not ctx.triggered:
        comp_id = None
    else:
        comp_id = ctx.triggered[0]['prop_id'].split('.')[0]  # comp.prop

    empty_tree = {
        'title': '',
        'key': '0',
        'children': []
        # 'title': '(vazio)',
        # 'key': '0',
        # 'children': [{
        #     'title': '(vazio)',
        #     'key': '0-0',
        #     'children': [
        #         {'title': '(vazio)', 'key': '0-0-1'},
        #         {'title': '(vazio)', 'key': '0-0-2'},
        #         {'title': '(vazio)', 'key': '0-0-3'},
        #     ]   }]
    }

    if (comp_id is not None):
        if (comp_id == 'graficofreq') and (click_data is not None) and (value is not None):
            numsent = click_data['points'][0]['customdata']
            return create_treedata(numsent, click_data['points'][0]['y'])
        else:
            return empty_tree
    else:
        return empty_tree


@app.callback(
    dash.dependencies.Output('titulo_inferior', 'children'),
    [dash.dependencies.Input('graficofreq', 'clickData'),
     dash.dependencies.Input('dropdownlivros', 'value')]
)
def update_tituloinferior(click_data, value):
    ctx = dash.callback_context
    if not ctx.triggered:
        comp_id = None
    else:
        comp_id = ctx.triggered[0]['prop_id'].split('.')[0] # comp.prop

    if (comp_id is not None):
        if (comp_id == 'graficofreq') and (click_data is not None) and (value is not None):
            numsent = click_data['points'][0]['customdata']
            retstr = 'Sentenças métricas entre {} e {}'.format(numsent[0], numsent[1])
        else:
            if value is not None:
                retstr = 'Sentenças métricas'
            else:
                retstr = 'Sentenças métricas'
    else:
        retstr = 'Sentenças métricas (?)'
    return retstr

@app.callback(
    dash.dependencies.Output('instrucao', 'children'),
    [dash.dependencies.Input('dropdownlivros', 'value')]
)
def update_instrucao(value):
    retstr = ''
    
    if value is not None:
        retstr = '(clique em um ponto para visualizar sentenças métricas abaixo)'
    else:
        retstr = '(selecione um livro)'

    return retstr


# @app.callback(
#     dash.dependencies.Output('click-data', 'children'),
#     [dash.dependencies.Input('graficofreq', 'clickData')])
# def display_click_data(clickData):
#     return json.dumps(clickData, indent=2)


if __name__ == '__main__':
    app.run_server(debug=True)
