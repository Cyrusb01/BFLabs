#%%


from re import template
from numpy.lib.shape_base import _replace_zero_by_x_arrays
import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go
import plotly.express as px
import json
import datetime
import bt 
from plotly.graph_objs import *






colors = ['#a90bfe', '#7540ee', '#3fb6dc'] 
#----------------------------------------------------------PIE CHART ----------------------------------------------------------------------------
dic = {'60/40' : .95, 'Bitoin': .05}

def graph_pie(percent_dictionary):

    
    assets = list(percent_dictionary.keys())

    percents = list(percent_dictionary.values())
    #print(percents)
    
    fig = px.pie( values = percents, names = assets, color = assets,
                            color_discrete_sequence= colors,
                            title="Portfolio Allocation",
                            )
    fig.update_traces(hovertemplate='%{value:.0%}')
    #print("plotly express hovertemplate:", fig.data[0].hovertemplate)
    fig.update_layout(
    title={
        'text': "<b>Portfolio Allocation<b>",
        'y':0.87,
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
    x=0.36))
    fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })
    fig.update_traces(marker=dict(line=dict(color='white', width=1.3)))
    fig.update_layout(titlefont=dict(size =24, color='black'))
    
    #fig.show()
    graphs=[
        {
            'data': fig,
        }
    ]
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    return ids, graphJSON
    return fig

fig = graph_pie(dic)
#fig.show()

#----------------------------------------------------------SCATTER PLOT ----------------------------------------------------------------------------

risk_dic = {'60/40': .07, 'S&P 500 Total Return': .13, 'Combined Portfolio': .09}
return_dic = {'60/40': .10, 'S&P 500 Total Return': .14, 'Combined Portfolio': .20}

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
                            title="Risk vs. Return")
    fig.update_xaxes(showgrid = False)
    #print("plotly express hovertemplate:", fig.data[0].hovertemplate)
    fig.update_traces(hovertemplate='Annual Risk = %{x:.0%}<br>Annual Return = %{y:.0%}')

    fig.update_layout( 
    title={
        'text': "<b>Risk vs. Return<b>",
        'y':0.9,
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

    return fig

fig = graph_scatter_plot(risk_dic, return_dic)
#fig.show()

#------------------------------------------------------BAR CHART--------------------------------------
x_axis_rr_ss = ['Ann. Return', 'Ann. Risk']
y_combined = [.0996, .076]
y_6040 = [.099, .076]
y_spy = [.13, .12]

def graph_barchart(x_axis_rr_ss, y_combined, y_6040, y_spy):
    #animals=['giraffes', 'orangutans', 'monkeys']

    if(x_axis_rr_ss[0] == 'Ann. Return'):
        title = "<b>Ann. Return & Risk<b>"
    else:
        title = "Sharpe & Sortino Ratio"

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
             height=700, color_discrete_sequence = colors, template= 'plotly_white', 
             labels={
                "Type": "",
                "Values": "",
                "Strategy" : ""
                })
    fig.update_traces(texttemplate='%{y:.2%}', textposition='outside')
    fig.update_layout(uniformtext_minsize=16, uniformtext_mode='hide')
    fig.update_traces(hovertemplate='%{y:.0%}')
    fig.update_yaxes(showticklabels = False)
    fig.update_layout( 
    title={
        'text': title,
        'y':.95,
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
    y=-.1,
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

    

   
    
    return fig

fig = graph_barchart(x_axis_rr_ss, y_combined, y_6040, y_spy)
#fig.show()

#----------------------------------------------------------LINE CHART ----------------------------------------------------------------------------





# def graph_line_chart(results_list):
#     color_dict = {}
#     result_final = pd.DataFrame()
#     for i in range(len(results_list)):

#         temp = results_list[i]._get_series(None).rebase()
#         result_final = pd.concat([result_final, temp], axis = 1) #result dataframe
#         color_dict[result_final.columns[i]] = colors[i] #colors

#     fig = px.line(result_final, labels=dict(index="Click Legend Icons to Toggle Viewing", value="", variable=""),
#                     title="Portfolio Performance",
#                     color_discrete_map=color_dict,
#                     template="simple_white"
#                     )
    
#     fig.update_yaxes( # the y-axis is in dollars
#         tickprefix="$", showgrid=True
#     )
#     x = .82
#     fig.update_layout(legend=dict(
#         orientation="h",
#         yanchor="bottom",
#         y= -.25,
#         xanchor="right",
#         x=.82
#     ),
#     title={
#             'text': "Portfolio Performance",
#             'y':.99,
#             'x':0.5,
#             'xanchor': 'center',
#             'yanchor': 'top'},)
#     #fig.update_layout(height = 500)
#     fig.update_layout(margin = dict(l=0, r=0, t=20, b=10))
#     return fig

