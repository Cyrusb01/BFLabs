from dash import Dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objs as go
import numpy as np

# Internal logic
last_back = 0
last_next = 0

df = pd.read_csv("static/data/divswap_implied_cum_growth_curve.csv")

xlist = list(df["x"].dropna())
ylist = list(df["y"].dropna())

del df["x"]
del df["y"]

zlist = []
for row in df.iterrows():
    index, data = row
    zlist.append(data.tolist())

UPS = {
    0: dict(x=0, y=0, z=1),
    1: dict(x=0, y=0, z=1),
    2: dict(x=0, y=0, z=1),
    3: dict(x=0, y=0, z=1),
    4: dict(x=0, y=0, z=1),
    5: dict(x=0, y=0, z=1),
}

# CENTERS: the center of the graph when you rotate.
CENTERS = {
    0: dict(x=0, y=0, z=0),
    1: dict(x=0, y=0, z=0),
    2: dict(x=0, y=0, z=0),
    3: dict(x=0, y=0, z=0),
    4: dict(x=0, y=0, z=0),
    5: dict(x=0, y=0, z=0),
}

# EYES: the angle you look at the graph.
# x: big => zoom out on x axis; small => zoom in on x axis; negative: inverse x axis
# y: big => zoom out on y axis; small => zoom in on y axis; negative: inverse y axis
# z: big => zoom out on z axis (look down on the graph); small => zoom in on z axis (look up to the graph); negative: inverse z axis
EYES = {
    0: dict(x=4, y=3, z=0.5),
    1: dict(x=0, y=4.5, z=0),
    2: dict(x=4, y=-2.8, z=-0.8),
    3: dict(x=4, y=2.8, z=-0.8),
    4: dict(x=4, y=0, z=0),
    5: dict(x=0, y=0, z=8)
}

TEXTS = {
    0: '''
    #### Dividend swap growth curve 101
    The Dividend Swap growth curve shows the implied growth of forward dividend derivatives, revealing the relationship between long-
    and short-term expectations for growth in dividends per share of the S&P 500.
    >>
    It is, inherently, a market forecast for what dividends will do in the future —
    how much inflation there will be, for example, and how healthy growth will
    be over the years ahead — all embodied price of dividend derivatives today,
    tomorrow and many years from now. This isn't exactly the whole story, as many
    dealers and market participants are naturally long dividends and use the 
    dividend market as a way to reduce their exposure.  This can at times present
    opportunities for those looking to participate in the purely in the growth of 
    dividends over time without the inherent risk that stocks may be over valued.
    '''.replace('  ', ''),
    1: '''
    #### Where we stand
    Recently, the dividend market is pricing little to no dividend
    growth over the next 10 years.  This has only happened a few times in 
    recent history.  One might argue that it has more to do with fears of 
    a recession on the horizon. While there have been many recessions,
    historically, the S&P dividends are farily resilient having only 
    declined three calendar years over the past 45 years, so investors
    should pay attention.  This could be an attractive entry point.
    >>
    The dividend curve today is fairly flat, which is a sign that investors expect
    mediocre growth in the years ahead.
    '''.replace('  ', ''),
    2: '''
    #### Deep in the valley
    In response to the last recession, the Federal Reserve has kept short-term
    rates very low — near zero — since 2008. (Lower interest rates stimulate
    the economy, by making it cheaper for people to borrow money, but also
    spark inflation.)
    >>
    Now, the Fed is getting ready to raise rates again, possibly as early as
    June.
    '''.replace('  ', ''),
    3: '''
    #### Last time, a puzzle
    The last time the Fed started raising rates was in 2004. From 2004 to 2006,
    short-term rates rose steadily.
    >>
    But long-term rates didn't rise very much.
    >>
    The Federal Reserve chairman called this phenomenon a “conundrum," and it
    raised questions about the ability of the Fed to guide the economy.
    Part of the reason long-term rates failed to rise was because of strong
    foreign demand.
    '''.replace('  ', ''),
    4: '''
    #### Long-term rates are low now, too
    Foreign buyers have helped keep long-term rates low recently, too — as have
    new rules encouraging banks to hold government debt and expectations that
    economic growth could be weak for a long time.
    >>
    The 10-year Treasury yield was as low as it has ever been in July 2012 and
    has risen only modestly since.
    Some economists refer to the economic pessimism as “the new normal.”
    '''.replace('  ', ''),
    5: '''
    #### Long-term rates are low now, too
    Here is the same chart viewed from above.
    '''.replace('  ', '')
}

ANNOTATIONS = {
    0: [],
    1: [dict(
        showarrow=True,
        x="3-yr",
        y='2019-10-07',
        z=0.006745,
        text="The dividend swap curve is priced in <br> very little growth <br>.",
        xref='x',
        yref='y',
        zref='z',
        xanchor='left',
        yanchor='auto'
    )],
    2: [],
    3: [],
    4: [],
    5: [],
}

def add_dash_yield(server, path_name = '/yieldapp/'):
    """
    This is the function used to add a dash application to the current 
    flask server. 
    Inputs:
        server: flask app
        path_name : url extension to access dash app

    Outputs:
        dash_app: dash server
    """
    route_prefix=''#'/api'
    # create dash app
    dash_app = Dash(__name__,
            server=server,
            routes_pathname_prefix=path_name,
            requests_pathname_prefix=route_prefix+path_name 
            # this is needed for deployment on bflabs
          )

    # create dash app layout (must do before creating callbacks)
    dash_app.layout = html.Div([
        html.Div(
            [
                dcc.Markdown(
                    '''
                    ### A View of a Chart That Predicts The Economic Future: The Yield Curve
                    This interactive report is a rendition of a
                    [New York Times original](https://www.nytimes.com/interactive/2015/03/19/upshot/3d-yield-curve-economic-growth.html).
                    '''.replace('  ', ''),
                    className='eight columns offset-by-two'
                )
            ],
            className='row',
            style={'text-align': 'center', 'margin-bottom': '15px'}
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Slider(
                            min=0,
                            max=5,
                            value=0,
                            marks={i: ''.format(i + 1) for i in range(6)},
                            id='slider'
                        ),
                    ],
                    className='row',
                    style={'margin-bottom': '10px'}
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Button('Back', id='back', style={
                                            'display': 'inline-block'}),
                                html.Button('Next', id='next', style={
                                            'display': 'inline-block'})
                            ],
                            className='two columns offset-by-two'
                        ),
                        dcc.Markdown(
                            id='text',
                            className='six columns'
                        ),
                    ],
                    className='row',
                    style={'margin-bottom': '10px'}
                ),
                dcc.Graph(
                    id='graph',
                    style={'height': '60vh'}
                ),
            ],
            id='page'
        ),
    ])

    custom_colorscl=[[0, "rgb(227, 230, 252)"], [0.25, "rgb(152, 163, 245)"], [0.75, "rgb(86, 86, 252)"], [1, "rgb(0,0,255)"]]

    # define callbacks to make graph interactive
    # Make 3d graph
    @dash_app.callback(Output('graph', 'figure'), [Input('slider', 'value')])
    def make_graph(value):

        if value is None:
            value = 0

        if value in [0, 2, 3]:
            z_secondary_beginning = [z[1] for z in zlist if z[0] == 'None']
            z_secondary_end = [z[0] for z in zlist if z[0] != 'None']
            z_secondary = z_secondary_beginning + z_secondary_end
            x_secondary = [
                '1-yr'] * len(z_secondary_beginning) + ['0-yr'] * len(z_secondary_end)
            y_secondary = ylist
            opacity = 0.8

        elif value == 1:
            x_secondary = xlist
            y_secondary = [ylist[-1] for i in xlist]
            z_secondary = zlist[-1]
            opacity = 0.8

        elif value == 4:
            z_secondary = [z[5] for z in zlist]
            x_secondary = ['5-yr' for i in z_secondary]
            y_secondary = ylist
            opacity = 0.8

        if value in range(0, 5):

            trace1 = dict(
                type="surface",
                x=xlist,
                y=ylist,
                z=zlist,
                hoverinfo='x+y+z',
                lighting={
                    "ambient": 0.95,
                    "diffuse": 0.99,
                    "fresnel": 0.01,
                    "roughness": 0.01,
                    "specular": 0.01,
                },
                opacity=opacity,
                showscale=False,
                zmax=9.18,
                zmin=0,
                scene="scene",
                cmin=-0.5,
                cmax=1,
                colorscale=custom_colorscl,
                contours=go.surface.Contours(
                        x=go.surface.contours.X(
                            highlight=True,
                            highlightcolor="#444444",
                        ),
                        y=go.surface.contours.Y(highlight=False),
                        z=go.surface.contours.Z(highlight=False),
                ) 
            )

            trace2 = dict(
                type='scatter3d',
                mode='lines',
                x=x_secondary,
                y=y_secondary,
                z=z_secondary,
                hoverinfo='x+y',
                line=dict(color='#444444')
            )

            data = [trace1, trace2]

        else:
            trace1 = dict(
                type="contour",
                x=ylist,
                y=xlist,
                z=np.array(zlist).T,
                colorscale=custom_colorscl,
                showscale=False,
                zmax=9.18,
                zmin=0,
                line=dict(smoothing=1, color='rgba(40,40,40,0.8)'),
            )

            data = [trace1]

        layout = dict(
            autosize=True,
            font=dict(
                size=12,
                color="#CCCCCC",
            ),
            margin=dict(
                t=5,
                l=5,
                b=5,
                r=5,
            ),
            showlegend=False,
            hovermode='closest',
            scene=dict(
                aspectmode="manual",
                aspectratio=dict(x=2, y=5, z=1.5),
                camera=dict(
                    up=UPS[value],
                    center=CENTERS[value],
                    eye=EYES[value]
                ),
                xaxis={
                    "showgrid": True,
                    "title": "",
                    "type": "category",
                    "zeroline": False,
                    "categoryorder": 'array',
                    "categoryarray": list(reversed(xlist))
                },
                yaxis=dict(
                    showgrid= True,
                    title="",
                    type="date",
                    zeroline= False,
                    showspikes=False,
                ),
                zaxis = dict(showspikes=False, 
                                              spikesides=False),
            )
        )

        figure = dict(data=data, layout=layout)
        # py.iplot(figure)
        return figure


    # Make annotations
    @dash_app.callback(Output('text', 'children'), [Input('slider', 'value')])
    def make_text(value):
        if value is None:
            value = 0

        return TEXTS[value]

    # Button controls
    @dash_app.callback(Output('slider', 'value'),
                  [Input('back', 'n_clicks'), Input('next', 'n_clicks')],
                  [State('slider', 'value')])
    def advance_slider(back, nxt, slider):

        if back is None:
            back = 0
        if nxt is None:
            nxt = 0
        if slider is None:
            slider = 0

        global last_back
        global last_next

        if back > last_back:
            last_back = back
            return max(0, slider - 1)
        if nxt > last_next:
            last_next = nxt
            return min(5, slider + 1)

    return dash_app.server
