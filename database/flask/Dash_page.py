import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
from plotly import graph_objs
import plotly.express as px
from jupyter_dash import JupyterDash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

#Pricing Data 
df = pd.read_csv("C:\Onramp\BFLabs(Cyrus CSV)\datafiles\Slider_data.csv", usecols = ['Date','TraditionalOnly', 'SP500Only', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6'])
df['Date'] = pd.to_datetime(df['Date'], unit = 'ms')
df = df.set_index('Date')

#Stats Data
df_stats = pd.read_csv("C:\Onramp\BFLabs(Cyrus CSV)\datafiles\Slider_data.csv", usecols = ['AnnReturn',	'AnnRisk','SharpeRatio','SortinoRatio','ReturnTraditional','ReturnSP500','RiskTraditional',	'RiskSP500','SharpeTraditional','SharpeSP500','SortinoTraditional',	'SortinoSP500'])
df_stats = df_stats.dropna()

#------------------------------------------------------------------SCATTER------------------------------------------------------------------------------------------------------------------
colors = ['#a90bfe', '#7540ee', '#3fb6dc'] 


app.layout = html.Div(children=[
    # All elements from the top of the page
    html.Div([
        html.H1(children='Onramp Research Dashboard', style = {'text-align': 'center'})
    ], className='row'),
    html.Br(),
    html.Div([
        html.Div([
        
        ], className='one columns'),
        html.Div([
            
            dcc.Graph(
                id='pie_chart'
            ),  
        ], className='three columns'),
        html.Div([
           

            dcc.Graph(
                id='line_chart'
            ),  
        ], className='four columns'),
        html.Div([
            dcc.Graph(
                id='scatter_plot'
            ),  
        ], className='three columns'),
    ], className='row'),
    # New Div for all elements in the new 'row' of the page
    html.Br(),
    html.Br(),
    html.Div([
        html.Div([
            html.H3(children='100% 60/40'),
        ], className='two columns'),
        
        html.Div([
            dcc.Slider(
            id = "slider_num",
            min = 0,
            max = 5,
            value = 0,
            step = 1
            )
        ], className='eight columns'),
        html.Div([
            html.H3(children='5% Bitcoin'),
        ], className='two columns'),
    ], className='row'),
    
    #html.Div(id='slider-output-container'),
    html.Div([
        html.Div([
            html.H3(children=''),
        ], className='two columns'),
        html.Div([
            
            dcc.Graph(
                id='bar_chart_rr'
            ),  
        ], className='four columns'),
        html.Div([
           

            dcc.Graph(
                id='bar_chart_ss'
            ),  
        ], className='four columns'),
        # html.Div([
           
        # ], className='two columns'),
    ], className='row'),
])

@app.callback(

    [dash.dependencies.Output('pie_chart', 'figure'),
     dash.dependencies.Output('line_chart', 'figure'),
     dash.dependencies.Output('scatter_plot', 'figure'),
     dash.dependencies.Output('bar_chart_rr', 'figure'),
     dash.dependencies.Output('bar_chart_ss', 'figure')],
    [dash.dependencies.Input('slider_num', 'drag_value')]
)
def update_graphs(value):
    
    #------------------------------------------------------------------------------Pie Chart ---------------------------------------------------------------------------

    percent_dict = {'60/40' : 1-float(value)/100, 'Bitoin': float(value)/100}

    def graph_pie(percent_dictionary):

        colors_pie = ['#a90bfe', '#f2a900'] #BTC Orange
        assets = list(percent_dictionary.keys())

        percents = list(percent_dictionary.values())
        #print(percents)
        
        fig = px.pie( values = percents, names = assets, color = assets,
                                color_discrete_sequence= colors_pie,
                                title="Portfolio Allocation",
                                width = 400, height = 400
                                )
        fig.update_traces(hovertemplate='%{value:.0%}')
        #print("plotly express hovertemplate:", fig.data[0].hovertemplate)
        fig.update_layout(
        title={
            'text': "<b>Portfolio Allocation<b>",
            'y':1,
            'x':0.49,
            'xanchor': 'center',
            'yanchor': 'top'},
        font = dict(
            family="Circular STD",
            color="black"
        ),
        legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-.2,
        xanchor="left",
        x=0.30))
        fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })
        fig.update_traces(marker=dict(line=dict(color='white', width=1.3)))
        fig.update_layout(titlefont=dict(size =24, color='black'))
        fig.update_layout(margin = dict(l=10, r=20, t=40, b=0))
        
        return fig


    #------------------------------------------------------------------------------Line Chart ---------------------------------------------------------------------------

    choice = 'd' + str(value + 1)
    def graph_line_chart(df, choice):

        df = df[['TraditionalOnly', 'SP500Only', choice]]
        df.columns = ['Traditional Only', 'SP500 Only', "Combined Portfolio"]
        color_dict = {}
        color_dict['Traditional Only'] = colors[0]
        color_dict['SP500 Only'] = colors[1]
        color_dict['Combined Portfolio'] = colors[2]
        
    
        fig = px.line(df, labels={
                                "value": "",
                                "Date": "",
                                "color" : "",
                                "variable": ""
                                },
                        title="Portfolio Performance",
                        color_discrete_map=color_dict,
                        template="simple_white",
                        width = 500, height = 450
                        )
        
        fig.update_yaxes( # the y-axis is in dollars
            tickprefix="$", showgrid=True
        )
        x = .82
        fig.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y= -.25,
            xanchor="right",
            x=.86
        ),
        font = dict(
            family="Circular STD",
            color="black"
        ),
        title={
                'text': "<b>Portfolio Performance<b>",
                'y':1,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'},)
        fig.update_yaxes(side = "right", nticks = 4)
        fig.update_layout(titlefont=dict(size =24, color='black'))
        fig.update_layout(margin = dict(l=10, r=20, t=20, b=0))
        return fig


    #------------------------------------------------------------------------------Scatter Plot ---------------------------------------------------------------------------
    risk_dic = {'60/40': float(df_stats.iloc[0][6])/100, 'S&P 500 Total Return': float(df_stats.iloc[0][7])/100, 'Combined Portfolio': float(df_stats.iloc[value][1])/100}
    return_dic = {'60/40': float(df_stats.iloc[0][4])/100, 'S&P 500 Total Return': float(df_stats.iloc[0][5])/100, 'Combined Portfolio': float(df_stats.iloc[value][0])/100}
    
    def graph_scatter_plot(risk_dic, return_dic):
        labels = list(risk_dic.keys())

        xaxis_vol = list(risk_dic.values())
        yaxis_return = list(return_dic.values())


        size_list = [3, 3, 3]
        symbols = [1, 2, 0] #this makes the symbols square diamond and circle in order
        fig = px.scatter( x= xaxis_vol, y= yaxis_return, size = size_list, color = labels, 
                                #color_discrete_sequence=['#A90BFE','#FF7052','#66F3EC', '#67F9AF'],
                                color_discrete_sequence= colors,
                                template = 'plotly_white',
                                labels={
                                "x": "Annual Risk",
                                "y": "Annual Return",
                                "color" : "",
                                "symbol": ""

                                },
                                title="Risk vs. Return",
                                width = 450, height = 450)
        fig.update_xaxes(showgrid = False)
        #print("plotly express hovertemplate:", fig.data[0].hovertemplate)
        fig.update_traces(hovertemplate='Annual Risk = %{x:.0%}<br>Annual Return = %{y:.0%}')

        fig.update_layout( 
        title={
            'text': "<b>Risk vs. Return<b>",
            'y':1,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        font = dict(
            family="Circular STD",
            color="black"
        ),
        legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-.3,
        xanchor="left",
        x=0.1
        ))
        fig.update_yaxes(side = "right")
        fig.update_layout({
        'plot_bgcolor': 'rgba(255, 255, 255, 0)',
        'paper_bgcolor': 'rgba(255, 255, 255, 0)',
        })
        fig.update_layout(yaxis_tickformat = '%')
        fig.update_layout(xaxis_tickformat = '%')
        fig.update_layout(titlefont=dict(size =24, color='black'))
        fig.update_xaxes( title_font = {"size": 20})
        fig.update_yaxes( title_font = {"size": 20})
        fig.update_layout(margin = dict(l=10, r=0, t=20, b=0))

        return fig
    
    #------------------------------------------------------------------------------Bar Chart ---------------------------------------------------------------------------

    x_axis_rr = ['Ann. Return', 'Ann. Risk']
    x_axis_ss = ['Sharpe', 'Sortino']
    
    y_combined_rr = [float(df_stats.iloc[value][0])/100, float(df_stats.iloc[value][1])/100]
    y_6040_rr = [float(df_stats.iloc[0][4])/100, float(df_stats.iloc[0][6])/100]
    y_spy_rr = [float(df_stats.iloc[0][5])/100, float(df_stats.iloc[0][7])/100]

    y_combined_ss = [float(df_stats.iloc[value][2])/100, float(df_stats.iloc[value][3])/100]
    y_6040_ss = [float(df_stats.iloc[0][8])/100, float(df_stats.iloc[0][10])/100]
    y_spy_ss = [float(df_stats.iloc[0][9])/100, float(df_stats.iloc[0][11])/100]

    def graph_barchart(x_axis_rr_ss, y_combined, y_6040, y_spy):
        

        if(x_axis_rr_ss[0] == 'Ann. Return'):
            title = "<b>Ann. Return & Risk<b>"
        else:
            title = "<b>Sharpe & Sortino Ratio<b>"

        x_axis_rr_ss *= 3
        y_vals = []
        y_vals += y_6040
        y_vals += y_spy
        y_vals += y_combined
    
        
        strat = ['60/40 Only', '60/40 Only', 'S&P 500 Total Return', 'S&P 500 Total Return', 'Combined Portfolio', 'Combined Portfolio']

        df = pd.DataFrame(list(zip(x_axis_rr_ss, y_vals, strat)),
                columns =['Type', 'Values', 'Strategy'])
        #print(df)

        fig = px.bar(df, x="Type", y="Values",
                color='Strategy', barmode='group',
                color_discrete_sequence = colors, template= 'plotly_white', 
                labels={
                    "Type": "",
                    "Values": "",
                    "Strategy" : ""
                    }, width= 500, height = 400)
        fig.update_traces(texttemplate='%{y:.2%}', textposition='outside')
        fig.update_layout(uniformtext_minsize=16, uniformtext_mode='hide')
        fig.update_traces(hovertemplate='%{y:.0%}')
        fig.update_yaxes(showticklabels = False)
        fig.update_layout( 
        title={
            'text': title,
            'y': 1,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        font = dict(
            family="Circular STD",
            color="black"
        ),
        legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-.3,
        xanchor="left",
        x=0.11
        ),
        barmode='group',
        bargap=0.15, # gap between bars of adjacent location coordinates.
        bargroupgap=0.1 # gap between bars of the same location coordinate.
        )
        fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        })
        fig.update_layout(xaxis_tickfont_size=19)
        fig.update_layout(titlefont=dict(size =24, color='black'))
        fig.update_layout(margin = dict(l=10, r=0, t=50, b=0))

        return fig



    pie_fig     = graph_pie(percent_dict)
    line_fig    = graph_line_chart(df, choice)
    scatter_fig = graph_scatter_plot(risk_dic, return_dic)
    bar_rr_fig  = graph_barchart(x_axis_rr, y_combined_rr, y_6040_rr, y_spy_rr)
    bar_ss_fig  = graph_barchart(x_axis_ss, y_combined_ss, y_6040_ss, y_spy_ss)
    return pie_fig, line_fig, scatter_fig, bar_rr_fig, bar_ss_fig

if __name__ == '__main__':
    app.run_server(debug=True)