import pandas as pd
import numpy 
import requests
import datetime
import plotly.express as px
import plotly.graph_objs as go
import dash 
import dash_core_components as dcc
import dash_html_components as html


# getting names of top cryptocurrencies
url = requests.get('https://min-api.cryptocompare.com/data/top/mktcapfull?limit=50&tsym=USD')
data = url.json()

coininfo = [] # for extracting coininfo 
for item in data["Data"]:
    coininfo.append(item["CoinInfo"])  
    
    
names=[] # for extracting name 
for item in coininfo:
    names.append(item["Name"])  

app = dash.Dash()

df = pd.DataFrame() 
def get_data(crypto):
    l = []
    page = requests.get(f'https://min-api.cryptocompare.com/data/v2/histoday?fsym={crypto}&tsym=USD&allData=true')
    data = page.json()['Data']['Data']
    close_data = list(map(lambda x:x['close'],data))
    l.append(close_data)
    df[crypto] = l[0]

for i in names:
    get_data(i)
    
time = []
page = requests.get(f'https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&allData=true')
data = page.json()['Data']['Data']
timestamp = list(map(lambda x:x['time'],data))
time.append(timestamp)    

df['time'] = time[0]
df['time'] = [datetime.datetime.fromtimestamp(d) for d in df.time]

df.set_index('time',inplace=True) 
df.index = df.index.normalize()
   

feautures = df.columns   

from dash.dependencies import Input, Output, State

app = dash.Dash()

app.layout = html.Div([
    html.H1('Cryptocurrency Dashboard'),
    
    html.Div([html.H3('Enter a cryptocurrency:',style={'paddingRight':'30px'}),
             dcc.Dropdown(id = 'crypto_picker',
             options = [{'label':i,'value':i}for i in feautures],
              value='BTC',# set default value
              multi=True
              )],
             style={'display':'inline-block','verticalAlign':'top','width':'30%'}
             ),
    html.Div([html.H3('Select a start and end date:'),
              dcc.DatePickerRange(id='my_date_picker',
                                  min_date_allowed=df.index[0],
                                  max_date_allowed = df.index[-1],
                                  start_date = df.index[-1000],
                                  end_date = df.index[-1])],
             style={'display':'inline-block'}),
    html.Div([
        html.Button(id='submit-button',
                    n_clicks=0,
                    children = 'Submit',
                    style = {'fontSize':24, 'marginLeft':'30px'}),
        ], style = {'display':'inline-block'}),
    
    dcc.Graph(id = 'my_graph',
             figure= {'data':[
                 {'x':df.index,'y':df['BTC']}
                  
                  
                  
                  ],'layout':{'title':'Default Title'}}
             )
    
    
    ])

@app.callback(Output('my_graph','figure'),
              [Input('submit-button','n_clicks')],
              [State('crypto_picker','value'),
               State('my_date_picker','start_date'),
               State('my_date_picker','end_date')
               ])


def update_graph(n_clicks, crypto_ticker, start_date, end_date):
    start= start_date
    end= end_date
    
    traces = []
    for tic in crypto_ticker:
        data = df.loc[start:end,:]
        traces.append({'x':data.index,'y':data[tic],'name':tic})
        
    
    fig = {'data':traces,
           'layout':{'title':crypto_ticker}}
    
    return fig

if __name__ == '__main__':
    app.run_server()
    
