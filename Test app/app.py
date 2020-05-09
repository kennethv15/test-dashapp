import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import datetime
from dash.dependencies import Input, Output, State
from datetime import date

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as pxs
import plotly.express as px

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE])

app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-166009061-1"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());

          gtag('config', 'UA-166009061-1');
        </script>
        
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""



server = app.server
app.title = "Covid-19 PAINEL RESENDE - UERJ"

#images
combined = 'https://raw.githubusercontent.com/kennethv15/test-dashapp/master/logo-all.jpg'

#Resende Data_Frame
df_resende = pd.DataFrame(pd.read_csv('Dataset/Pacientes_compilados_csv.csv', sep=';', encoding='latin', index_col=0))
df_resende_evolucao = pd.DataFrame(pd.read_csv('Dataset/Evolucao_dos_casos_csv.csv', sep=';', encoding='latin', index_col=0))
df_resende_curados = pd.DataFrame(pd.read_csv('Dataset/Pacientes_curados_csv.csv', sep=';', encoding='latin', index_col=0))
df_resende_teste_rapido = pd.DataFrame(pd.read_csv('Dataset/Resende_Teste_Rapido.csv', sep=';', encoding='latin', index_col=0))
df_resende.columns = df_resende.columns.str.strip()
df_coord_resende = pd.DataFrame(pd.read_csv('Dataset/coord.csv')).drop_duplicates()
df_resende = df_resende[df_resende['Cidade'] == 'Resende']
df_resende = df_resende.merge(df_coord_resende, on='Bairro', how='left')

#Resende Sexo
df_resende['Sexo'] = df_resende['Sexo'].str.strip()
df_sex = df_resende.groupby('Sexo').count()['Data de confirmação']
def_sex_death = df_resende.groupby('Sexo').count()['Morte']
df_resende_sex = pd.DataFrame({'Número de casos': df_sex, 'Número de mortes': def_sex_death})
df_resende_sex['Sexo'] = df_resende_sex.index
df_resende_sex.reset_index(drop=True, inplace=True)
df_resende_sex['Sexo'].replace(to_replace=['F', 'M'], value=["Mulher", 'Homem'], inplace=True)

#Resende Bairro - Confirmed/Dead
df_bairro_cases = df_resende.groupby('Bairro').count()['Data de confirmação']
df_bairro_death = df_resende.groupby('Bairro').count()['Morte']
df_resende_bairro = pd.DataFrame({'Número de casos': df_bairro_cases, 'Número de mortes': df_bairro_death})
df_resende_bairro['Bairro'] = df_resende_bairro.index
df_resende_bairro.reset_index(drop=True, inplace=True)
df_resende_bairro = df_resende_bairro.merge(df_coord_resende, how='left', on='Bairro')

#Time Series - Confirmed/Dead
df_resende_1 = pd.DataFrame(
    df_resende.groupby(
        pd.to_datetime(df_resende['Data de confirmação'],
                       dayfirst=True)).count()[['Data de confirmação',
                                                'Morte']]).sort_index()
df_resende_1['Data'] = df_resende_1.index
idx = pd.date_range(df_resende_1['Data'][0], date.today())
df_resende_1 = df_resende_1.reindex(idx, fill_value=0)
df_resende_1['Número de casos'] = 0
df_resende_1['Número de mortes'] = 0

for x in range(len(df_resende_1)):
    if x == 0:
        df_resende_1.iloc[x, 3] = df_resende_1.iloc[x, 0]
        df_resende_1.iloc[x, 4] = df_resende_1.iloc[x, 1]
    else:
        df_resende_1.iloc[x, 3] = df_resende_1.iloc[x, 0] + df_resende_1.iloc[x-1, 3]
        df_resende_1.iloc[x, 4] = df_resende_1.iloc[x, 1] + df_resende_1.iloc[x-1, 4]

#Resende - Cases and Deaths
resende_confirmado = int(df_resende_evolucao["Casos Confirmados"].iloc[-1])
resende_RTPCR = df_resende_bairro["Número de casos"].sum()
resende_teste_rapido = df_resende_teste_rapido["Classificacao"].dropna().count()
resende_deaths = df_resende_bairro["Número de mortes"].sum()
resende_sindrome_gripal = int(df_resende_evolucao["Casos de Sindrome Gripal "].iloc[-1])
resende_descartados = int(df_resende_evolucao["Casos Descartados"].iloc[-1])
resende_notificados = int(df_resende_evolucao["Casos Notificados"].iloc[-1])
resende_pendente_lab = int(df_resende_evolucao["Casos suspeitos aguardando resultado laboratorial"].iloc[-1])
resende_curados = df_resende_curados.groupby("CURA").count()["Data de confirmacao"].iloc[0]

#Resende - Age Groups
df_masculino=df_resende[df_resende['Sexo']=='M'].fillna(0)
df_feminino=df_resende[df_resende['Sexo']=='F'].fillna(0)

#Resende - Evolution
# evolucao = pd.read_csv(r'Dataset/Evolucao_dos_casos_csv.csv', sep=';')
# evolucao = evolucao.drop(evolucao[evolucao['Data'] == 'Total'].index)
# evolucao['Data'] = pd.to_datetime(evolucao['Data'], dayfirst=True)
# evolucao.sort_values('Data', inplace=True)
# evolucao.columns = evolucao.columns.str.strip()
# evolucao.reset_index(drop=True, inplace=True)
# evolucao['Not_ac'] = 0
# evolucao['Des_ac'] = 0
# evolucao['Conf_ac'] = 0
# evolucao['Susp_ac'] = 0
#
# for x in range(len(evolucao)):
#     if x == 0:
#         evolucao['Not_ac'][x] = evolucao.iloc[x, 1]
#         evolucao['Des_ac'][x] = evolucao.iloc[x, 2]
#         evolucao['Conf_ac'][x] = evolucao.iloc[x, 3]
#         evolucao['Susp_ac'][x] = evolucao.iloc[x, 4]
#     else:
#         evolucao['Not_ac'][x] = evolucao.iloc[x, 1] + evolucao['Not_ac'][x-1]
#         evolucao['Des_ac'][x] = evolucao.iloc[x, 2] + evolucao['Des_ac'][x-1]
#         evolucao['Conf_ac'][x] = evolucao.iloc[x, 3] + evolucao['Conf_ac'][x-1]
#         evolucao['Susp_ac'][x] = evolucao.iloc[x, 4] + evolucao['Susp_ac'][x-1]
#
# evolucao = evolucao.merge(df_resende_1, on='Data', how='left').fillna(0)

# for x in range(len(evolucao)):
#     if x == 0:
#         evolucao['Número de mortes'][x] = evolucao['Morte'][x]
#     else:
#         evolucao['Número de mortes'][x] = evolucao['Morte'][x] + evolucao['Número de mortes'][x-1]

def cont(df):
    limits= [(0, 10), (11, 20), (21, 30), (31, 40), (41, 50), (51, 60), (61, 70), (71, 80), (80, 110)]
    soma = 0
    tabela = []
    for a in range(len(limits)):
        lim = limits[a]
        for i in range(len(df)):
            if lim[0] <= df.iloc[i, 2] <= lim[1]:
                soma += 1
        tabela.append(soma)
        soma = 0
    return tabela

def contmorte(df):
    limits= [(0, 10), (11, 20), (21, 30), (31, 40), (41, 50), (51, 60), (61, 70), (71, 80), (80, 110)]
    soma = 0
    tabela = []
    for b in range(len(limits)):
        lim = limits[b]
        for i in range(len(df)):
            if lim[0] <= df.iloc[i, 2] <= lim[1] and df.iloc[i, 9] != 0:
                soma += 1
        tabela.append(soma)
        soma = 0
    return tabela

dado_homem = cont(df_masculino)
dado_mulher = cont(df_feminino)
dado_morte_homem = contmorte(df_masculino)
dado_morte_mulher = contmorte(df_feminino)

# Cards
card_confirmados = [
    dbc.CardBody([
        dbc.Row(
            dbc.Col([
                html.H5(f"CASOS: {resende_RTPCR + resende_teste_rapido}", id="tooltip-target-1", className="card-text", style={"color":"#0582FF",
                                                                                                                  "font-weight":"bold"}),
                dbc.Tooltip(children=[html.P("Número de casos confirmados de SAR-CoV-2 em Resende, RJ e seus bairros durante a pandemia COVID-19",
                                             style={"text-align":"left"}
                                             )
                                      ],
                            target="tooltip-target-1",
                            hide_arrow=True,
                            )
            ]))
    ],
        style={"padding-top": 5,
               "padding-bottom": 5,
               "background-color": "lightgrey"}
    ),
    dbc.CardFooter([dbc.Row([
        dbc.Col([
            html.P(f"TESTE RT-PCR: {resende_RTPCR}", id="tooltip-target-2", className="card-text", style={"color":"#0582FF",
                                                                                                          "font-weight":"bold"}),
            dbc.Tooltip(children=[html.P("O teste COVID-19 RT-PCR (Reverse transcription polymerase chain reaction) "
                                         "é um teste em tempo real para a detecção qualitativa do SRA-CoV-2 em amostras "
                                         "respiratórias coletados de indivíduos suspeitos de COVID-19.",
                                         style={"text-align": "left"}
                                         )
                                  ],
                        target="tooltip-target-2",
                        hide_arrow=True,
                        )
        ],
            lg=5),
        dbc.Col([
            html.P(f"TESTE RÁPIDO: {resende_teste_rapido}", id="tooltip-target-3", className="card-text", style={"color":"#0582FF",
                                                                                                        "font-weight":"bold"}),
            dbc.Tooltip(children=[html.P("O teste rápido sorológico é um teste para detectar "
                                         "os níveis de anticorpos IgM e IgG na amostra de "
                                         "sangue do paciente ou em pessoas que tenham sido "
                                         "expostas ao vírus SRA-CoV-2. ",
                                         style={"text-align": "left"}
                                         )
                                  ],
                        target="tooltip-target-3",
                        hide_arrow=True,
                        )
        ], lg=7)],
    )],
        style={"padding-top": 5,
               "padding-bottom": 5,
               "background-color": "#DBDBDB"}
    )
]


card_obitos = [
    dbc.CardBody([
        html.H5(f"ÓBITOS: {resende_deaths}", className="card-text", style={"color":"#E81313",
                                                                           "font-weight":"bold"})],
        style={"padding-top": 5,
               "padding-bottom": 5,
               "background-color": "lightgrey"}
    )
]

card_3 = [
    dbc.CardBody([
        html.H5(f"CURADOS: 63", className="card-text", style={"color":"#278700",
                                                                   "font-weight":"bold"})],
        style={"padding-top": 5,
               "padding-bottom": 5,
               "background-color": "lightgrey"}
    ),
    dbc.CardFooter([
        dbc.Row([
            dbc.Col(
                html.P(f"EM ANÁLISE: {resende_pendente_lab}", className="card-text", style={"font-weight":"bold"}), lg=5),
            dbc.Col(
                html.P(f"SINDROME GRIPAIS: 1103", className="card-text", style={"font-weight":"bold"}),  lg=7)],
    )],
        style={"padding-top": 5,
               "padding-bottom": 5,
               "background-color": "#DBDBDB"}
    )
]

cards = dbc.CardGroup([
        dbc.Card(card_confirmados, color="light", inverse=False, outline=False),
        dbc.Card(card_obitos, color="light", inverse=False, outline=False),
        dbc.Card(card_3, color="light", inverse=False, outline=False)])

#Modal - Inside Column
left = dbc.Col(html.Div(["UERJ", html.Br(),
                         "- Dr. Vahid Nikoofard",html.Br(),
                         "- Dr. Bruno Fernando Inchausp Teixeira", html.Br(),
                         "- Dra. Luciana Ghussn", html.Br(),
                         "- Dr. Vinicius Seabra", html.Br(),
                         "- Prof. Phillipe Valente Cardoso", html.Br(),
                         "- Isabella Escobar dos Santos", html.Br(),
                         "- Kenneth John Vasquez", html.Br(),
                         "- Matheus Galhano Vieira Galvão", html.Br(),
                         "- Renan Santos Serpa", html.Br()
                         ]))
right = dbc.Col(html.Div(["Prefeitura de Resende", html.Br(),
                          "- Prefeito de Resende Diogo Balieiro Diniz",html.Br(),
                          "- Secretário de Saúde de Resende Alexandre Sérgio Alves Vieira", html.Br(),
                          "- Dra. Lúcia Helena Rocha de Albuquerque", html.Br(),
                          "- Carolina Bittencourt Castro Ferraz", html.Br(),
                          ]))

modal = html.Div([
    dbc.Button("INFO", id="sobre-o-projeto",
               style={
                   "padding-top":"7px",
                   "padding-bottom":"7px"
               }),
    dbc.Modal([
        dbc.ModalHeader("Bem Vindo"),
        dbc.ModalBody([
            html.P("O Projeto COVID-19/Resende é uma parceria realizada entre "
                   "a Prefeitura de Resende e a Universidade do Estado do Rio "
                   "de Janeiro (UERJ), representada pelo Campus de Resende, "
                   "localizado no km 298  da Rodovia Presidente Dutra e pelo "
                   "Campus de São Gonçalo, na Faculdade de Formação de "
                   "Professores (FFP). O Projeto tem por objetivo concentrar "
                   "as informações sobre o COVID-19 no município em um único "
                   "site, onde o cidadão poderá obter um boletim diário sobre "
                   "o coronavírus de forma transparente e detalhada."),
            html.P(html.B("O Projeto conta com a colaboração dos seguintes pesquisadores e alunos, "
                          "além dos membros das instituições públicas municipais resendenses:")),
            html.Div([dbc.Row([left, right])])
            ]),
        dbc.ModalFooter(dbc.Button("Close", id="close", className="ml-auto")),
        ],
        id="modal",
        size="lg",
    )]
)

# NavBar
navbar1 = html.Div(
    [dbc.Row(
        dbc.Navbar([
            dbc.Container(
                dbc.Row([
                    dbc.Col(html.Img(src=combined, height="55px")),
                    dbc.Col(html.B(children=(f'PAINEL RESENDE COVID-19',
                                             html.Br(),
                                             f'Ultima Atualização: 09/05/2020'), style={'color':'white'}))],
                    align="center",
                    justify="start",
                    no_gutters=False
                ),
                fluid=True
            ),
            dbc.NavItem([modal])],
            color="black",
            dark=True,
            style={"width":"100%"}
        ),
        justify="center",
        align="center")
    ]
)

footer = html.Div(
    id="footer",
    children=[
        html.Hr(style={"marginBottom": ".5%"},),
        html.P(
            style={"textAlign": "center", "margin": "auto"},
            children=[" | ",
                      html.A(
                          "Desenvolvido com Plotly - Dash",
                          href="https://plotly.com/dash/",
                      ),
                      " | ",
                      html.A(
                          "UERJ - FAT",
                          href="http://www.fat.uerj.br/",
                      ),
                      " | ",
            ]
        ),
        html.Br()
    ])
#Age Group - Figure
faixas=['Até 10 ',
        '11-20 ',
        '21-30 ',
        '31-40 ',
        '41-50 ',
        '51-60 ',
        '61-70 ',
        '71-80 ',
        '+80 ']

graficos1 = pxs.make_subplots(rows=1,
                              cols=2,
                              specs=[[{"type": "bar"},
                                      {"type": "bar"}]],
                              subplot_titles=['Número de casos', 'Número de mortes'])
graficos1.add_trace(go.Bar(y=faixas,
                           x=dado_mulher,
                           name='Mulher',
                           orientation='h',
                           marker=dict(color='rgba(232, 232, 232, 1)',
                                       line=dict(color='rgba(0, 0, 0, 1)',
                                                 width=0.5)),
                           text=dado_mulher,
                           showlegend=False,
                           textposition='auto',
                           textangle=0,
                           textfont=dict(size=15)),
                    row=1,
                    col=1)

graficos1.add_trace(go.Bar(y=faixas,
                           x=dado_homem,
                           name='Homem',
                           orientation='h',
                           marker=dict(color='rgba(0, 0, 0, 1)',
                                       line=dict(color='rgba(0, 0, 0, 1)',
                                                 width=1)),
                           showlegend=False,
                           text=dado_homem,
                           textposition='auto',
                           textangle=0,
                           textfont=dict(size=15)),
                    row=1,
                    col=1)

graficos1.add_trace(go.Bar(y=faixas,
                           x=dado_morte_mulher,
                           name='Mulher',
                           orientation='h',
                           marker=dict(color='rgba(232, 232, 232, 1)',
                                       line=dict(color='rgba(0, 0, 0, 1)',
                                                 width=1)),
                           showlegend=True,
                           text=dado_morte_mulher,
                           textposition='auto',
                           textangle=0,
                           textfont=dict(size=15)),
                    row=1,
                    col=2)

graficos1.add_trace(go.Bar(y=faixas,
                           x=dado_morte_homem,
                           name='Homem',
                           orientation='h',
                           marker=dict(color='rgba(0, 0, 0, 1)',
                                       line=dict(color='rgba(0, 0, 0, 1)',
                                                 width=1)),
                           showlegend=True,
                           text=dado_morte_homem,
                           textposition='auto',
                           textangle=0,
                           textfont=dict(size=15)),
                    row=1,
                    col=2)

graficos1.update_traces(textfont_size=20, hoverinfo='x+name')
graficos1.update_layout(plot_bgcolor='rgba(105, 105, 105, 0)',
                        paper_bgcolor='dimgrey',
                        margin=dict(b=0, t=50, r=30, l=80),
                        legend_orientation="h",
                        legend=dict(x=0,
                                    y=-.09,
                                    font=dict(color='white',
                                              size=15)),
                        annotations=[{'showarrow': False,
                                      'y':1.1,
                                      "font": {"color":'white', 'size': 20}}],
                        barmode='stack',
                        height=260
                        )

graficos1.update_xaxes(color='white')
graficos1.update_yaxes(color='white',
                       row=1,
                       col=1,
                       title='Idade')
graficos1.update_yaxes(color='white',
                       visible=False,
                       row=1,
                       col=2)

#Pie - SEXO Figure
graph_sexo = pxs.make_subplots(rows=1,
                               cols=2,
                               specs=[[{"type": "domain"},
                                       {"type": "domain"}]],
                               subplot_titles=('Número de casos',
                                               'Número de mortes'),
                               )
graph_sexo.add_trace(go.Pie(labels=df_resende_sex['Sexo'],
                            values=df_resende_sex['Número de casos'],
                            hoverinfo='label+value',
                            textposition='inside',
                            textinfo='percent+label',
                            hole=.2),
                     row=1,
                     col=1)

graph_sexo.add_trace(go.Pie(labels=df_resende_sex['Sexo'],
                            values=df_resende_sex['Número de mortes'],
                            hoverinfo='label+value',
                            textposition='inside',
                            textinfo='percent+label',
                            hole=.2),
                     row=1,
                     col=2)

graph_sexo.update_traces(textfont_size=10,
                         marker=dict(colors=['White', 'Black'],
                                     line=dict(color='#000000', width=2)))

graph_sexo.update_layout(paper_bgcolor='dimgrey',
                         showlegend=False,
                         legend=dict(x=.4,
                                     y=-1,
                                     font=dict(color='white', size=15)),
                         annotations=[{'showarrow': False,
                                       'y':1.09,
                                       "font": {"color":'white', 'size': 20}}],
                         margin=dict(l=10,r=10,b=20,t=50),
                         height=260
                         )
#Time Series - Figure
# fig1 = go.Figure()
# fig1.add_trace(go.Scatter(x=df_resende_1.index,
#                           y=df_resende_1['Número de casos'],
#                           name='Casos - TESTE RT-PCR',
#                           hovertemplate='%{y}',
#                           line=dict(color="#0582FF")))
# fig1.add_trace(go.Scatter(x=df_resende_1.index,
#                           y=df_resende_1['Número de mortes'],
#                           name='Óbitos',
#                           hovertemplate='%{y}',
#                           line=dict(color="#E81313")))
# fig1.update_layout(margin=dict(b=40, t=40, r=20, l=60),
#                    title='Acompanhamento diário',
#                    hovermode='closest',
#                    yaxis_title= 'Número de casos / mortes',
#                    paper_bgcolor='lightgrey',
#                    plot_bgcolor='rgba(250, 250, 250, 0.3)',
#                    legend=dict(x=0,
#                                y=1,
#                                traceorder="normal",
#                                font=dict(size=12,
#                                          color="black"),
#                                bgcolor="white",
#                                bordercolor="lightgrey"),
#                    height=260
#                    )
# fig1.update(layout=dict(title=dict(x=0.5,y=0.95)))

#Accumulation - Bar
# fig2= go.Figure()
#
# fig2.add_trace(go.Bar(x=evolucao['Data'],
#                       y=evolucao['Número de mortes'],
#                       name='Número de mortes',
#                       hovertemplate='<br>Número de morte do dia: %{customdata}<br>Número acumulado: %{y}',
#                       text=evolucao["Número de mortes"],
#                       textposition='outside',
#                       textfont={'size':11},
#                       customdata=evolucao['Morte'],
#                       marker_color="#E81313")
#                )
#
# # fig2.add_trace(go.Bar(x=evolucao['Data'],
# #                       y=evolucao['Susp_ac'],
# #                       name='Casos em análise',
# #                       hovertemplate='<br>Número de casos em análise do dia: %{customdata}<br>Número acumulado: %{y}',
# #                       text=evolucao['Susp_ac'],
# #                       textposition='outside',
# #                       textfont={'size':11},
# #                       customdata=evolucao['Casos suspeitos aguardando resultado laboratorial'])
# #                )
#
# fig2.add_trace(go.Bar(x=evolucao['Data'],
#                       y=evolucao['Conf_ac'],
#                       name='Casos confirmados',
#                       hovertemplate='<br>Número de casos confirmados do dia: %{customdata}<br>Número acumulado: %{y}',
#                       text=evolucao['Conf_ac'],
#                       textposition='outside',
#                       textfont={'size':11},
#                       customdata=evolucao['Casos Confirmados'],
#                       marker_color="#0582FF")
#                )
#
# fig2.update_xaxes(rangeslider_visible=False)
#
# fig2.update_layout(height=260,
#                    updatemenus=[
#                        dict(
#                            type="buttons",
#                            direction="up",
#                            active=0,
#                            x=-0.1,
#                            buttons=list([
#                                dict(label="Todos casos",
#                                     method="update",
#                                     execute=True,
#                                     args=[{"visible": [True, True]},
#                                           {"title": "Casos cumulativos"}]),
#                                # dict(label="Casos em Análise",
#                                #      method="update",
#                                #      args=[{"visible": [False, True, False]},
#                                #            {"title": "Número acumulado de Casos em Análise"}]
#                                #      ),
#                                dict(label="Casos Confirmados",
#                                     method="update",
#                                     args=[{"visible": [False, True]},
#                                           {"title": "Número acumulado de Casos Confirmados"}]
#                                     ),
#                                dict(label="Mortes",
#                                     method="update",
#                                     args=[{"visible": [True, False]},
#                                           {"title": "Número acumulado de Mortes"}]
#                                     )
#                            ])
#                        )
#                    ])
#
# fig2.update_layout(title_text="Casos cumulativos",
#                    showlegend=False,
#                    barmode='stack',
#                    margin=dict(b=50, t=50, r=20, l=40),
#                    paper_bgcolor='lightgrey',
#                    hovermode='x unified',
#                    plot_bgcolor='rgba(250, 250, 250, 0.3)')
#
# fig2.update(layout=dict(title=dict(x=0.5)))

#Bar-Graph 3
fig3 = go.Figure()
fig3.add_trace(go.Bar(x=df_resende_1.index,
                      y=df_resende_1['Número de mortes'],
                      name='Número de acumulado mortes',
                      hovertemplate='%{y}<br>Número de morte do dia: %{customdata}',
                      text=df_resende_1['Número de mortes'],
                      textposition='outside',
                      customdata=df_resende_1['Morte'],
                      marker_color="#E81313"
                      )
               )

fig3.add_trace(go.Bar(x=df_resende_1.index,
                      y=df_resende_1['Número de casos'],
                      name='Número acumulado de casos - RT-PCR',
                      hovertemplate='%{y}<br>Número de confirmados do dia: %{customdata}',
                      text=df_resende_1['Número de casos'],
                      textposition='outside',
                      customdata=df_resende_1['Data de confirmação'],
                      marker_color="#0582FF"
                      )
               )

fig3.update_xaxes(rangeslider_visible=False)

fig3.update_layout(height=260+25,
                   updatemenus=[
                       dict(
                           type="buttons",
                           direction="right",
                           active=0,
                           x=0.5,
                           y=-0.4,
                           yanchor="middle",
                           xanchor="center",
                           buttons=list([
                               dict(label="Casos confirmados / Mortes",
                                    method="update",
                                    args=[{"visible": [True, True]},
                                          {"title": "Casos cumulativos - Teste RT-PCR"}]),
                               dict(label="Mortes",
                                    method="update",
                                    args=[{"visible": [True, False]},
                                          {"title": "Número acumulado de Mortes"}]),
                               dict(label="Casos confirmados",
                                    method="update",
                                    args=[{"visible": [False, True]},
                                          {"title": "Número acumulado de Casos - RT-PCR"}])
                           ])
                       )
                   ])

fig3.update_layout(margin=dict(b=50, t=40, r=20, l=30),
                   title='Casos cumulativos',
                   paper_bgcolor='lightgrey',
                   barmode='stack',
                   plot_bgcolor='rgba(250, 250, 250, 0.3)',
                   showlegend=False,
                   hovermode='x unified')
fig3.update(layout=dict(title=dict(x=0.5, y=0.95),
                        yaxis=dict(range=[0,80],
                                   title="Numero de casos"),
                        xaxis=dict(range=["19/03/2020","07/05/2020"])
                        )
            )

#Tab 1
# graph_tab_1 = dcc.Tabs(
#     value="tab-1-1",
#     children=[
#         dcc.Tab(label="CASOS", value='tab-1-1', children=[dcc.Graph(figure=fig2)],
#                 style={"height": "50%",
#                        "padding": "8px",
#                        "color": "white"},
#                 selected_style={"height": "50%",
#                                 "padding": "8px",
#                                 "background-color":"#D3D3D3"}
#                 ),
#         dcc.Tab(label="CONFIRMADOS E ÓBITOS", value='tab-1-2', children=[dcc.Graph(figure=fig1)],
#                 style={"height":"50%",
#                        "padding":"8px",
#                        "color":"white"},
#                 selected_style={"height":"50%",
#                                 "padding":"8px",
#                                 "background-color":"#D3D3D3"}),
#
#     ],
#     colors={
#         "border":"#D3D3D3",
#         "primary":"dimgrey",
#         "background":"black",
#         "font":{"color":'white', 'size': 17},
#     },
# )

#Tab 2
graph_tab_2 = dcc.Tabs(
    value="tab-2-1",
    children=[
        dcc.Tab(label="POR SEXO", value='tab-2-1', children=[dcc.Graph(figure=graph_sexo)],
                style={"height":"50%",
                       "padding":"8px",
                       "color":"white"},
                selected_style={"height":"50%",
                                "padding":"8px",
                                "background-color":"#696969",
                                "color":"white"}),
        dcc.Tab(label="POR FAIXA ETÁRIA", value='tab-2-2', children=[dcc.Graph(figure=graficos1)],
                style={"height": "50%",
                       "padding": "8px",
                       "color":"white"},
                selected_style={"height":"50%",
                                "padding":"8px",
                                "background-color":"#696969",
                                "color":"white"}
                )
    ],
    colors={
        "border":"dimgrey",
        "primary":"dimgrey",
        "background":"black",
        "font":{"color":'white', 'size': 17},
    },
)

#Resende Bubble Map
resende_bubble = px.scatter_mapbox(df_resende_bairro,
                                   lat='lat',
                                   lon='long',
                                   hover_data=['Número de casos', 'Número de mortes'],
                                   hover_name='Bairro',
                                   zoom=12.2,
                                   size='Número de casos',
                                   height=559+25,
                                   size_max=30,
                                   center=dict(lat=-22.470, lon=-44.46)
                                   )

resende_bubble.update_layout(mapbox_style='dark',
                             mapbox_accesstoken='pk.eyJ1IjoibWF0aGV1c2dhbGhhbm8iLCJhIjoiY2s5YWozZmZyMjQyazNkcGdqZXlzajFraSJ9.mQwhayrKhADgig-Y1MKwSA',
                             margin={"r":0,"t":0,"l":0,"b":0},
                             coloraxis_showscale=False)

#Layout
app.layout = dbc.Container([navbar1,
                            html.Div(
                                children=[
                                    dbc.Row([
                                        dbc.Col(html.Div(cards),
                                                lg=12,
                                                align="center"
                                                )],
                                        no_gutters=True,
                                        align="center",
                                        justify="center")],
                                style={'height': '30%',
                                       'width': '100%',
                                       "padding-top": "5px",
                                       "padding-bottom": "5px"
                                       }),
                            html.Div([
                                dbc.Row([
                                    dbc.Col([
                                        html.Div(dcc.Graph(figure=resende_bubble))],
                                        width={"order": "first"},
                                        style={"padding-left": "10px",
                                               "padding-right": "10px",
                                               "padding-top": "10px"},
                                        lg=7
                                    ),
                                    dbc.Col([
                                        html.Div([
                                            html.Div(graph_tab_2),
                                            html.Div(dcc.Graph(figure=fig3))
                                        ])
                                    ],
                                        width={"order": "last"},
                                        style={"padding-left": "10px",
                                               "padding-right": "10px",
                                               "padding-top": "10px"},
                                        lg=5
                                    )
                                ],
                                justify='center',
                                no_gutters=True)
                            ]),
                            footer
                            ],
                           fluid=True,
                           style={'height':'400'}
                           )
#Modal Control
@app.callback(
    Output("modal", "is_open"),
    [Input("sobre-o-projeto", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)