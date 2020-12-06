# ClimbingAnalysis application
# Written by Andrew Watkins
# watkins(dot)andrewb(at)gmail(dot)com
#
# This dash application gives a basic exploration
# of USA Climbings initial results for regional qualification
# for Virtual Qualifiers in the bouldering season of 2020

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go
import plotly.offline as pyo
import plotly.express as px
import pandas as pd
import numpy as np
import requests
import pdfplumber

from dash.dependencies import Input, Output, State, ClientsideFunction

def parseData(url):
#    response= requests.get(url)
    fname ='/home/ABWatkins/USACVirtualQEClimbingAnalysis/assets/current_results.pdf'
#    with open(fname, 'wb') as f:
#        f.write(response.content)
    lines = []
    with pdfplumber.open(fname) as pdf:
        for i in range(len(pdf.pages)):
            page = (pdf.pages[i])
            txt=page.extract_text()
            lines+=txt.split('\n')

    df = pd.DataFrame(columns=['Region','Category', 'FirstName', 'LastName', 'Score', 'Comp'])
    curRegion = 0
    curCat='MJR'
    for i in range(len(lines)):
        if lines[i][:6]=='Region' and lines[i][6]!='a':
            curRegion=int(lines[i][-2:])
        elif lines[i][0]=='M' or lines[i][0]=='F':
            curCat = lines[i]
        elif lines[i][0].isnumeric():
            climber = lines[i].split()
            lnameIndex = climber.index('USAC')-2 if 'USAC' in climber else climber.index('\"USAC')-2
            fname = climber[1]
            lname = climber[lnameIndex]
            if fname=='Genevieve' and climber[3]=='Dennis4400':
                lname = 'Dennis'
                lnameIndex = 3
                climber.insert(lnameIndex+1,4400)
            j = lnameIndex+1
            score = int(climber[j])
            comp = ' '.join(climber[(j+1):])
            row =[curRegion, curCat, fname, lname, score, comp]
            df = df.append(pd.Series(row,index=df.columns), ignore_index = True)

    df['Score']=pd.to_numeric(df['Score'])
    return df

defaultResultsPage = "http://www.usaclimbing.org/Assets/Regional+Ranking-Preliminary-201102.pdf"
#fname ='/home/ABWatkins/USACVirtualQEClimbingAnalysis/assets/current_results.csv'
fname ='assets/current_results.csv'
#df =parseData(defaultResultsPage)
df = pd.read_csv(fname)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#external_stylesheets=['https://github.com/plotly/dash-app-stylesheets/blob/master/dash-oil-and-gas.css']
#external_stylesheets=['https://github.com/plotly/dash-app-stylesheets/blob/master/dash-analytics-report.css']

app = dash.Dash(__name__)#, external_stylesheets=external_stylesheets)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>USAC Virutal QE Climbing Analysis</title>
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
</html>
'''
rlist = [ x for x in range(10,100) if x%10==1 or x%10==2]
catList=['FJR', 'MJR', 'FYA', 'MYA', 'FYB', 'MYB', 'FYC', 'MYC', 'FYD', 'MYD']
catColors ={'FJR':"#ffa822", 'MJR':"#b36b00",
            'FYA':"#134e6f", 'MYA':"#071e2c",
            'FYB':"#ff6150", 'MYB':"#ff1a00",
            'FYC':"#1ac0c6", 'MYC': "#128387",
            'FYD':"#b6bbc8", 'MYD': "#8b93a7"}
bgcolor = '#f2f2f2'

def genericScatter(df, compScore=0, compCat=None):
    if compCat != None:
        df = df[df['Category'].isin(compCat)]
    fig = px.scatter(df, x="Region", y="Score", color="Category",
                hover_data=['Score'],
                color_discrete_map=catColors,
                category_orders ={'Region':rlist, 'Category':catList},# if compCat == None else [compCat]},
                title="Regional QE Scores by Region and Category",
                #template="seaborn"
                )
    if compScore>0:
        fig.add_hline(y=compScore, annotation_text = 'Your Climber\'s Score',annotation_position='top left',
                    line_dash='dash')
    fig.update_xaxes(type='category')
    fig.update_layout(paper_bgcolor=bgcolor)
    return fig

def avgScatter(df, compScore =0, compCat = None):
    gf = df.groupby(['Region', 'Category'], as_index=False)['Score'].mean()
    fig = px.scatter(gf if compCat == None else gf[gf['Category'].isin(compCat)], x="Region", y="Score", color="Category",
                     hover_data=['Score'],
                     color_discrete_map=catColors,
                    category_orders ={'Region':rlist, 'Category':catList},
                    labels=dict(Score='Average Score'),
                    title='Average QE Score by Region and Category')
    fig.update_xaxes(type='category')
    if compScore>0:
        fig.add_hline(compScore, annotation_text = 'Your Climber\'s Score', annotation_position='top left',
                        line_dash='dash')
    fig.update_layout(paper_bgcolor=bgcolor)
    return fig

def catHistogram(df, compScore = 0, compCat = None):
    fig = px.histogram(df if compCat == None else df[df['Category'].isin(compCat)], x="Score", color='Category',
                        color_discrete_map=catColors,
                       category_orders ={'Region':rlist, 'Category':catList},
                       title="Histogram of Scores by Climbing Category (200 point bins)")
    if compScore>0:
        fig.add_vline(compScore, annotation_text = 'Your Climber\'s Score',
                        annotation_position="top left",
                        line_dash='dash')
    fig.update_layout(paper_bgcolor=bgcolor)
    return fig

def allHistogram(df, compScore = 0, compCat = None):
    fig=px.histogram(df,x='Score', title='Histogram of QE Scores (200 point bins)')
    if compScore>0:
        fig.add_vline(compScore, annotation_text = 'Your Climber\'s Score',
                        annotation_position="top left",
                        line_dash = 'dash')
    fig.update_layout(paper_bgcolor=bgcolor)
    return fig

def findPlace(df, testScore=0, testRegions=None, testCats = None):
    retdf = pd.DataFrame(columns=['Region','Category', 'Place', 'Number of Climbers'])
    if(testScore<=0):
        return retdf
    if testRegions==None:
        testRegions = [ x for x in range(10,100) if x%10==1 or x%10==2]
    if testCats == None:
        testCats = ['FJR', 'MJR', 'FYA', 'MYA', 'FYB', 'MYB', 'FYC', 'MYC', 'FYD', 'MYD']
    for reg in testRegions:
        for cat in testCats:
            tf = df[df['Region']==reg]
            tf = tf[tf['Category']==cat]
            totalClimbers = len(tf)
            tf = tf[tf['Score']>testScore]
            place = len(tf)+1
            if totalClimbers>0:
                row = [reg,cat,place,totalClimbers]
                retdf = retdf.append(pd.Series(row,index=retdf.columns), ignore_index = True)
    return retdf

region_drop = html.Div([
    dcc.Markdown('''**Choose one or more regions** (or leave blank for all) '''),
    dcc.Dropdown(
        id='dropdown-reg',
        options=[{'label':i,'value':i} for i in rlist],
        multi=True,
        placeholder='Select one or more regions',
        #value=None,
        #style={"text-align":"center", "width":"25%"}
        #style={'width':'100%'},
        #className="three columns"# offset-by-three columns"
        ),])
cat_drop = html.Div([
    dcc.Markdown('''**Choose your climber's category**'''),
    dcc.Dropdown(
        id='dropdown-cat',
        options =[{'label':i,'value':i} for i in catList],
        multi=True,
        #value=None,
        placeholder='Select one or more categories',
    ),], className='nine columns')
score_input = html.Div([
    dcc.Markdown('''**Enter your climber's score**'''),
    dcc.Input(id='inputScore', type='number', min=0, step=50, placeholder='2000', value=2000),
], className = 'two columns')

table_results = html.Div([
    html.Div(id='score-output-container'),
    dcc.Markdown('''your climber would have placed as follows in the selected categories '''),
    dash_table.DataTable(id='compTable',
        style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': bgcolor#'rgb(248, 248, 248)'
            }
            ]
        )
    ], className =' three columns')

visuals = html.Div([
    html.Div([
    dcc.Markdown('''Hover over the graphs to see more information about each data point
    '''),
    dcc.Graph(
        id='genScat',
#        figure=genSFig
    ),
    dcc.Graph(
        id='avgScat',
#        figure = avgSFig
    ),
    dcc.Graph(
        id='catHist',
#        figure = catHFig
    ),
#    dcc.Graph(
#        id='allHist',
#        figure=allHFig
#    )
    ],className='nine columns',),
#], className='row'),
])


app.layout = html.Div(children=[
    html.Div([
    html.H2(children='Virtual Bouldering Regional Qualifier Events Across USAC Regions', style={"text-align": "center"}),
    dcc.Markdown(children='''Based off of file: <http://www.usaclimbing.org/Assets/Regional+Ranking-Preliminary-201116a.pdf>''', style={"text-align": "center"}),
    html.P(style={"text-align": "center"},children='Use this tool to compare a climber\'s score to others or to see general trends among climbers at QEs across the country'),
    html.Br(),
    ],),

    #html.Div([
    html.Div([ #region_drop,
    score_input, cat_drop,], className='row'),
    html.Div([table_results
    , visuals,
        ],className="row"),
    #),
    #visulizations,
   html.Div([
    dcc.Markdown(children='''Source code can be found on github: <https://github.com/ABWatkins/USACVirtualQEClimbingAnalysis>''', style={"text-align": "center"}),]),
])

@app.callback(
    Output('compTable', 'data'),
    Output('compTable', 'columns'),
#    Output('dreg-output-container','children'),
#    Output('dcat-output-container','children'),
   Output('score-output-container', 'children'),
    #Input('dropdown-reg', 'value'),
    Input('dropdown-cat', 'value'),
    Input('inputScore', 'value')
)
def getDataTable(compCat = None, compScore = 0):
    if compCat == []:
        compCat = None
    if compScore == None:
        compScore = 0
    compDF=findPlace(df, testScore= compScore, testRegions=None, testCats=compCat)
    data=compDF.to_dict('records')
    columns=[{'id': c, 'name': c} for c in compDF.columns]
    return data,columns, 'With a score of {}'.format(compScore)#,'You have selected {}'.format(compRegion), 'You have selected {}'.format(compCat),'You entered {}'.format(compScore)

@app.callback(
    Output('genScat', 'figure'),
    #Input('dropdown-reg', 'value'),
    Input('dropdown-cat', 'value'),
    Input('inputScore', 'value'))
def getGenScat(compCat = None, compScore = 0):
    if compCat == []:
        compCat = None
    if compScore == None:
        compScore = 0
    return genericScatter(df, compScore,compCat)

@app.callback(
    Output('avgScat', 'figure'),
    #Input('dropdown-reg', 'value'),
    Input('dropdown-cat', 'value'),
    Input('inputScore', 'value'))
def getAvgScat(compCat = None, compScore = 0):
    if compCat == []:
        compCat = None
    if compScore == None:
        compScore = 0
    return avgScatter(df, compScore,compCat)

@app.callback(
    Output('catHist', 'figure'),
    #Input('dropdown-reg', 'value'),
    Input('dropdown-cat', 'value'),
    Input('inputScore', 'value'))
def getCatHist(compCat = None, compScore = 0):
    if compCat == []:
        compCat = None
    if compScore == None:
        compScore = 0
    return catHistogram(df, compScore,compCat)

# @app.callback(
#     Output('allHist', 'figure'),
#     #Input('dropdown-reg', 'value'),
#     Input('dropdown-cat', 'value'),
#     Input('inputScore', 'value'))
# def getAllHist(compCat = None, compScore = 0):
#     if compCat == []:
#         compCat = None
#     if compScore == None:
#         compScore = 0
#     return allHistogram(df, compScore,compCat)


if __name__ == '__main__':
    app.run_server(debug=True,host='127.0.0.1')
    #app.run_server(debug=True)
