#%%


import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go
import plotly.express as px
import json
import datetime
import bt 





dic = {'btc' : .05, 'spy': .95}


def graph_pie(percent_dictionary):

    pie_colors = ['#00eead', '#ff7052', '#a90bfe'] 
    assets = list(percent_dictionary.keys())

    percents = list(percent_dictionary.values())
    print(percents)
    
    fig = px.pie( values = percents, names = assets, color = assets,
                            color_discrete_sequence= pie_colors,
                            title="Portfolio Allocation",
                            )
    fig.update_traces(hovertemplate='%{value:.0%}')
    print("plotly express hovertemplate:", fig.data[0].hovertemplate)
    fig.update_layout(
    title={
        'text': "Portfolio Allocation",
        'y':0.87,
        'x':0.49,
        'xanchor': 'center',
        'yanchor': 'top'},
    legend=dict(
    orientation="h",
    yanchor="bottom",
    y=-.2,
    xanchor="left",
    x=0.39))
    
    fig.update_traces(marker=dict(line=dict(color='white', width=1.3)))
    

    return fig

fig = graph_pie(dic)

fig.show()



def graph_line_chart(results_list):
    color_dict = {}
    result_final = pd.DataFrame()
    for i in range(len(results_list)):

        temp = results_list[i]._get_series(None).rebase()
        result_final = pd.concat([result_final, temp], axis = 1) #result dataframe
        color_dict[result_final.columns[i]] = colors[i] #colors

    fig = px.line(result_final, labels=dict(index="Click Legend Icons to Toggle Viewing", value="", variable=""),
                    title="Portfolio Performance",
                    color_discrete_map=color_dict,
                    template="simple_white"
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
        x=.82
    ),
    title={
            'text': "Portfolio Performance",
            'y':.99,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},)
    #fig.update_layout(height = 500)
    fig.update_layout(margin = dict(l=0, r=0, t=20, b=10))
    return fig

# def scatter_plot(results_df):
    # xaxis_vol = []
    # yaxis_return = []
    # for x in results_df: #fill in two lists with the vol and return %s 
    #     xaxis_vol.append(float(x.iloc[30][1].replace('%', '')))
    #     yaxis_return.append(float(x.iloc[29][1].replace('%', '')))
    
    # size_list =[]
    # for i in range(len(xaxis_vol)): #getting errors on the number of sizes
    #     size_list.append(4)
    
    # labels = []
    # for i in results_df:
    #     labels.append(i.iloc[0][1])
    
    # fig = px.scatter( x= xaxis_vol, y= yaxis_return, size = size_list, color = labels,
    #                         #color_discrete_sequence=['#A90BFE','#FF7052','#66F3EC', '#67F9AF'],
    #                         color_discrete_sequence= colors,
    #                         labels={
    #                         "x": "Monthly Vol (ann.) %",
    #                         "y": "Monthly Mean (ann.) %",
    #                         "color" : ""
    #                         },
    #                         title="Risk Vs. Return")
    # fig.update_layout(
    # title={
    #     'text': "Risk Vs. Return",
    #     'y':0.9,
    #     'x':0.5,
    #     'xanchor': 'center',
    #     'yanchor': 'top'},
    # legend=dict(
    # orientation="h",
    # yanchor="bottom",
    # y=-.3,
    # xanchor="left",
    # x=0.1
    
    # ))
    # fig.update_layout(margin = dict(l=30, r=0, t=70, b=80))



    # return fig