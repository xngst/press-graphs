"""
PRESSGRAPHS DASH CLIENT
WEB GUI interface for PressGraphs WebAPI 
"""
###################################
# IMPORTS
###################################
#builtins
from datetime import datetime
from datetime import timedelta
#3rd party
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table as dt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from dash.dependencies import Input, Output, State
#oww
from md import md_txt

###################################
# DEFINITIONS
###################################
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
app.title = 'Press Graphs'
app.config.suppress_callback_exceptions = True
server = app.server
startup_time = datetime.now().strftime("%Y %m %d %H:%M")

API_KEY = "" # register your own API key at http://pressgraphs.pythonanywhere.com/create/test_user
MAX_REQUEST_DAY = 90

def build_layout():
    """
    def to serve app.layout every time the app loads
    """
    layout = html.Div(style={"padding":"2vw"},
      children=[dcc.Location(id='url', refresh=True),
      dbc.Nav([
      dbc.NavItem(dbc.NavLink("kezdőlap", active=True, href="/")),
      dbc.NavItem(dbc.NavLink("dátum szerint", href="/all_date")),
      dbc.NavItem(dbc.NavLink("újságok szerint", href="/all_org")),
      dbc.NavItem(dbc.NavLink("újság szerint", href="/site_tab")),
      dbc.NavItem(dbc.NavLink("két újság összevetése", href="/site_vs_tab")),
      dbc.NavItem(dbc.NavLink("két szó összevetése", href="words_tab")),
      dbc.DropdownMenu(
        [dbc.DropdownMenuItem("újságok", href="mo"),
         dbc.DropdownMenuItem("útmutató", href ="manual"),
         dbc.DropdownMenuItem("elérhetőség", href="contact")],
        label="további info",
        nav=True)]),
      html.Hr(),
      html.Div(id='page-content'),
      html.Hr()])

    return layout

def md_linkler(url: str) ->str:
    """
    transforms url to markdown type link
    """
    md_link = f"[link]({url})"
    return md_link

def update_dt_by_date(dataframe: pd.DataFrame()) -> dt.DataTable():
    """
    updates dash_table with passed dataframe
    returns dash_table
    """
    dataframe["link"] = dataframe["url"].copy()
    dataframe["link"] = dataframe["link"].apply(md_linkler)
    columns = [{'name': 'dátum', 'id':'date'},
               {'name': 'oldal', 'id':'site'},
               {'name': 'cím', 'id':'title'},
               {'name': 'link', 'id':'link', 'type':'text', 'presentation': 'markdown'},
               {'name': 'url', 'id':'url'}]
    data = dataframe.to_dict('records')
    data_table = dt.DataTable(
        style_table={"padding": "50px", "maxHeight": '350px',
                     "overflowY": "scroll"},
        style_data={'whiteSpace': 'normal', 'height': 'auto'},
        style_cell={'textAlign': 'left'},
        style_cell_conditional=[
            {'if': {'column_id': 'date'}, 'width': '30px'},
            {'if': {'column_id': 'site'}, 'width': '30px'},
            {'if': {'column_id': 'title'}, 'width': '250px'},
            {'if': {'column_id': 'link'}, 'width': '30px'},
            {'if': {'column_id': 'url'}, 'width': '100px'}],
        data=data,
        columns=columns,
        page_size=50,
        export_format="xlsx")

    return data_table

def plot_all_by_date(*, dataframe: pd.DataFrame(), search_word: str) -> px.bar:
    """
    :date_count:pd.DataFrame
    returns: plotly.express.px.bar
    """
    if len(dataframe) > 0:
        dataframe.columns = ["találatok száma"]
        fig = px.bar(dataframe,
                     height=500,
                     x=dataframe.index,
                     y="találatok száma",
                     color="találatok száma",
                     labels={"x": "dátum", "date": "cikkek száma"},
                     opacity=.75,
                     color_continuous_scale="Geyser"
                     )

        fig.update_layout(
            title={'text': f"""A '{search_word}' szó száma a cikkek címeiben 
{dataframe.index.min()}--{dataframe.index.max()}.""",
                   'y': 0.900,
                   'x': 0.50},
            xaxis_title="Dátum",
            yaxis_title="Cikkek száma",
            yaxis_tickformat = 'd',
            transition={'duration': 500},
            plot_bgcolor="rgba(0,0,0,0)",
            font={"family":"Courier New, monospace",
                "size":11,
                "color":"#000000"
                })

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor = '#bdbdbd')

        if len(dataframe) < 5:
            fig.update_layout(xaxis_showticklabels = False, width=750)
            fig.update_yaxes(showgrid=False, dtick=1)

        return fig

    return px.bar()


def plot_all_by_sites(*, dataframe: pd.DataFrame(), search_word: str):
    """
    #Horizontal barchart with top n sites
    """
    if len(dataframe) > 0:

        df = dataframe
        df.rename(columns={'title': 'darab'}, inplace=True)

        fig = px.bar(df,
                     height=1500,
                     orientation='h',
                     x="darab",
                     y=df.index,
                     labels={"y": "orgánum", "x": "cikkek száma"},
                     opacity=.75,
                     )

        fig.update_layout(
            title={'text': "Találatok az elmúlt 90 napból"},
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis_title="Újságok",
            xaxis_title="Cikkek száma",
            font={
                "family":"Courier New, monospace",
                "size":10,
                "color":"#000000"
                })

        fig.update_traces(marker_color='black')
        fig.update_xaxes(showgrid=True, gridcolor='#bdbdbd')
        fig.update_yaxes(showgrid=False)

        return fig

    return px.bar()


def compare_two_sites(*,
                      search_word,
                      site1_df,
                      site2_df,
                      site_1,
                      site_2):
    """
    #Comparison line chart
    """

    if search_word:
        search_word = str(search_word).lower()
        site_corr = site1_df["count"].corr(site2_df["count"])

        fig = go.Figure(
            layout=go.Layout(
                annotations=[go.layout.Annotation(
                    text=f'Korrelációs együttható (r): {site_corr:.2f}',
                    hovertext="""Tartomány: -1 és 1 között. Jelzi két tetszőleges érték közötti lineáris kapcsolat nagyságát és irányát.""",
                    borderpad=1,
                    bgcolor="#ffffcc",
                    align='left',
                    showarrow=False,
                    xref='paper',
                    yref='paper',
                    x=0,
                    y=1,
                    bordercolor='grey',
                    borderwidth=1)]))

        fig.add_trace(go.Scatter(x=site1_df.index, y=site1_df["count"],
                                 mode='lines',
                                 line_shape='linear',
                                 name=f'{site_1}'))

        fig.add_trace(go.Scatter(x=site2_df.index, y=site2_df["count"],
                                 mode='lines',
                                 line_shape='linear',
                                 name=f'{site_2}'))

        fig.update_layout(
            title=f"""'{site_1}' és '{site_2}': '{search_word}' szó száma a cikkek címeiben""",
            xaxis_title="Dátum",
            yaxis_title="Cikkek száma",
            plot_bgcolor="rgba(0,0,0,0)",
            )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor='#bdbdbd')

        return fig

    return px.bar()


def compare_two_search_words(*,
                             sw_df_1,
                             sw_df_2,
                             search_word_1,
                             search_word_2):
    """
    #TODO
    """
    if search_word_1:
        sw1 = search_word_1.split()[0].strip()
        sw2 = search_word_2.split()[0].strip()

        corr = sw_df_1["count"].corr(sw_df_2["count"])

        fig = go.Figure(
            layout=go.Layout(
                annotations=[go.layout.Annotation(
                    text=f'Korrelációs együttható (r): {corr:.2f}',
                    hovertext="""Tartomány: -1 és 1 között.""",
                    borderpad=1,
                    bgcolor="#ffffcc",
                    align='left',
                    showarrow=False,
                    xref='paper',
                    yref='paper',
                    x=0,
                    y=1,
                    bordercolor='grey',
                    borderwidth=1)]))

        fig.add_trace(go.Scatter(x=sw_df_1.index, y=sw_df_1["count"],
                                 mode='lines',
                                 line_shape='linear',
                                 name=f'{sw1}'))

        fig.add_trace(go.Scatter(x=sw_df_2.index, y=sw_df_2["count"],
                                 mode='lines',
                                 line_shape='linear',
                                 name=f'{sw2}'))

        fig.update_layout(
            height=600,
            title={'text': f"'{sw1}' és '{sw2}' szavak száma a cikkek címeiben",
                   'y':0.90,
                   'x':0.5},
            xaxis_title="Dátum",
            yaxis_title="Cikkek száma",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(
                family="Courier New, monospace",
                size=11,
                color="#000000"
            ))
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor='#bdbdbd')

        return fig

    return  px.bar()


###################################
# LAYOUT
###################################

print("loading layout")
app.layout = build_layout

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')])

def display_page(pathname):
    if pathname == '/all_date':
        return page_1_layout
    elif pathname == '/all_org':
        return page_2_layout
    elif pathname == '/site_tab':
        return page_3_layout
    elif pathname == '/site_vs_tab':
        return page_4_layout
    elif pathname == '/words_tab':
        return page_5_layout
    elif pathname == '/contact':
        return page_6_layout
    elif pathname == '/manual':
        return page_7_layout
    elif pathname == '/mo':
        return page_8_layout
    else:
        return index_page

###################################
# INDEX
###################################

index_page = html.Div([
	dcc.Markdown(children=md_txt.index_txt)])

###################################
# PAGE 1 LAYOUT
###################################

page_1_layout = html.Div([
    dbc.Row(dbc.Col(html.Div(
        dbc.Input(id="search_input",
                  placeholder="keresett szó...",
                  type="text",
                  value="")), width=3)),
    html.Br(),
    dbc.Button("Keresés",
    	outline=True,
    	color="info",
    	className="mr-1",
    	id='submit-button',
    	n_clicks=0),

	dbc.Checklist(options=[{"label": "keresés szavakon belül", "value": 1}],
				  value=[],
				  id="switch-input",
				  switch=True),

  dcc.Graph(id='max_date_bargraph'),
  html.Div(id="table1", style={'font-family': 'Impact'})])

###################################
# PAGE 1 CHART CALLBACK
###################################

@app.callback(Output('max_date_bargraph', 'figure'),
  [Input('submit-button', 'n_clicks'),
   Input('search_input', 'n_submit'),
   Input('switch-input', 'value')],
  [State('search_input', 'value')])

def date_count_all_site(n_clicks, n_submit, switch_value, search_word):
  """
  """
  if n_clicks or n_submit:
    search_word = search_word.strip()

    if switch_value:
      switch_value = 1

    else:
      switch_value = 0

    site="all"
    today = datetime.today().strftime("%Y-%m-%d")
    from_date = (datetime.today() - \
    timedelta(days = MAX_REQUEST_DAY)).strftime("%Y-%m-%d")

    api_url = f"http://pressgraphs.pythonanywhere.com/date/count/"\
    f"{API_KEY}/{search_word}/{switch_value}/{from_date}/{today}/{site}"

    response = requests.get(api_url)
    content = response.json()[1]["data"]
    res_df = pd.DataFrame(content)

    if len(res_df) > 0:
      res_df.set_index("date", inplace=True)

  else:
    res_df = pd.DataFrame()
  fig = plot_all_by_date(dataframe=res_df, search_word=search_word)

  return fig

###################################
# PAGE 1 DATA TABLE CALLBACK
###################################
@app.callback(Output('table1', 'children'),
    [Input('max_date_bargraph', 'clickData'),
     Input('submit-button', 'n_clicks'),
	   Input('switch-input', 'value')],
	  [State('search_input', 'value')])

def update_table(clickData, n_clicks, switch_value, search_word):
  """
  #TODO
  """
  if clickData:
      search_word = search_word.strip()
      date = list(clickData["points"])[0]["label"]
      site = "all"

      if switch_value:
        switch_value = 1
      else:
        switch_value = 0

      api_url = f"http://pressgraphs.pythonanywhere.com/date/list/"\
      f"{API_KEY}/{search_word}/{switch_value}/{date}/{date}/{site}"

      response = requests.get(api_url)
      content = response.json()[1]["data"]

      df = pd.DataFrame(content)

      return update_dt_by_date(df)

  else:
      return

###################################
# PAGE 2 LAYOUT
###################################

page_2_layout = html.Div([
    dbc.Row(dbc.Col(html.Div(
        dbc.Input(id="search_input",
                  placeholder="keresett szó...",
                  type="text",
                  value="")), width=3)),
    html.Br(),
    dbc.Button("Keresés",
    	outline=True,
    	color="info",
    	className="mr-1",
    	id='submit-button',
    	n_clicks=0),

	dbc.Checklist(options=[{"label": "keresés szavakon belül", "value": 1}],
				  value=[],
				  id="switch-input",
				  switch=True),

  html.Div(id='my-output'),

  dcc.Graph(id='bargraph_2'),
  html.Div(id="table2", style={'font-family': 'Impact'})])

###################################
# PAGE 2 CHART CALLBACK
###################################

@app.callback(Output('bargraph_2', 'figure'),
  [Input('submit-button', 'n_clicks'),
   Input('search_input', 'n_submit'),
   Input('switch-input', 'value')],
  [State('search_input', 'value')])

def update_by_site(n_clicks, n_submit, switch_value, search_word):

    if n_clicks or n_submit:
        search_word = search_word.strip()

        if switch_value:
          switch_value = 1

        else:
          switch_value = 0

        site="all"
        today = datetime.today().strftime("%Y-%m-%d")
        from_date = (datetime.today() - \
      	timedelta(days = MAX_REQUEST_DAY)).strftime("%Y-%m-%d")

        api_url = f"http://pressgraphs.pythonanywhere.com/date/list/"\
        f"{API_KEY}/{search_word}/{switch_value}/{from_date}/{today}/{site}"

        response = requests.get(api_url)
        content = response.json()[1]["data"]
        res_df = pd.DataFrame(content)

        df = res_df.groupby(by="site").count()["title"]
        df = pd.DataFrame(df.sort_values(ascending=True)[:])

    else:
      df = pd.DataFrame()

    fig = plot_all_by_sites(dataframe=df, search_word=search_word)

    return fig

###################################
# PAGE 2 DATA TABLE CALLBACK
###################################

@app.callback(Output('table2', 'children'),
    [Input('bargraph_2', 'clickData'),
    Input('submit-button', 'n_clicks'),
    Input('switch-input', 'value')],
    [State('search_input', 'value')])

def display_clickData_2(clickData, n_clicks, switch_value, search_word):

    if clickData:
        search_word = search_word.strip()
        today = datetime.today().strftime("%Y-%m-%d")
        from_date = (datetime.today() - \
          timedelta(days = MAX_REQUEST_DAY)).strftime("%Y-%m-%d")
        site = list(clickData["points"])[0]["label"]

        if switch_value:
          switch_value = 1

        else:
            switch_value = 0    

        api_url = f"http://pressgraphs.pythonanywhere.com/date/list/"\
        f"{API_KEY}/{search_word}/{switch_value}/{from_date}/{today}/{site}"
        response = requests.get(api_url)

        content = response.json()[1]["data"]
        df = pd.DataFrame(content)

        return update_dt_by_date(df)

    else:
      return


###################################
# PAGE 3 LAYOUT
###################################

api_url = f"""http://pressgraphs.pythonanywhere.com/{API_KEY}/info/sites/all"""
response = requests.get(api_url)
schema = response.json()[0]
st_options = pd.DataFrame(response.json()[1]["data"])

page_3_layout = html.Div([
	html.H5("oldal szerinti keresés"),
    dbc.Row(dbc.Col(html.Div(
        dbc.Input(id="search_input",
                  placeholder="keresett szó...",
                  type="text",
                  value='')), width=3)),
	html.Br(),
    dbc.Row(dbc.Col(html.Div(dcc.Dropdown(
                id="sites",
                options=[{
                    'label': i,
                    'value': i
                } for i in st_options["site"]],
		        placeholder="keresett oldal...",
                value='')), width=3)),
    html.Br(),
    dbc.Button("Keresés",
			   outline=True,
               color="info",
               className="mr-1",
               id='submit-button',
               n_clicks=0),
	dbc.Checklist(options=[{"label": "keresés szavakon belül", "value": 1}],
				  value=[],
				  id="switch-input",
				  switch=True),

    dcc.Graph(id='bargraph_3'),
	html.Div(id="table3")])

###################################
# PAGE 3 CHART CALLBACK
###################################

@app.callback(Output('bargraph_3','figure'),
    [Input('submit-button', 'n_clicks'),
     Input('search_input', 'n_submit'),
     Input('switch-input', 'value')],
    [State('search_input', 'value'),
    State('sites', 'value')])

def update_site_graph(n_clicks, n_submit, switch_value, search_word, site):
    """
    """
    if n_clicks or n_submit:
        search_word = search_word.strip()

        if switch_value:
          switch_value = 1

        else:
          switch_value = 0

        site=site
        today = datetime.today().strftime("%Y-%m-%d")
        from_date = (datetime.today() - \
        timedelta(days = MAX_REQUEST_DAY)).strftime("%Y-%m-%d")

        api_url = f"http://pressgraphs.pythonanywhere.com/date/count/"\
        f"{API_KEY}/{search_word}/{switch_value}/{from_date}/{today}/{site}"

        response = requests.get(api_url)
        content = response.json()[1]["data"]
        res_df = pd.DataFrame(content)

        if len(res_df) > 0:
          res_df.set_index("date",inplace=True)

    else:
        res_df = pd.DataFrame()

    fig = plot_all_by_date(dataframe=res_df,
        search_word=search_word)

    return fig

###################################
# PAGE 3 DATA TABLE CALLBACK
###################################

@app.callback(Output('table3', 'children'),
    [Input('bargraph_3', 'clickData'),
     Input('submit-button', 'n_clicks'),
     Input('switch-input', 'value')],
    [State('search_input', 'value'),
     State('sites', 'value')])

def display_clickData_3(clickData, n_clicks, switch_value, search_word, site):
    """
    #TODO
    """
    if clickData:
        search_word = search_word.strip()
        date = list(clickData["points"])[0]["label"]

        if switch_value:
          switch_value = 1

        else:
          switch_value = 0

        api_url = f"http://pressgraphs.pythonanywhere.com/date/list/"\
        f"{API_KEY}/{search_word}/{switch_value}/{date}/{date}/{site}"
        response = requests.get(api_url)
        content = response.json()[1]["data"]
        df = pd.DataFrame(content)

        return update_dt_by_date(df)

    else:
        return

###################################
# PAGE 4 LAYOUT
###################################

api_url = f"""http://pressgraphs.pythonanywhere.com/{API_KEY}/info/sites/all"""
response = requests.get(api_url)
schema = response.json()[0]
st_options = pd.DataFrame(response.json()[1]["data"])

page_4_layout = html.Div([
	html.H5("két oldal összevetése"),
    dbc.Row(dbc.Col(html.Div(
        dbc.Input(id="search_input",
                  placeholder="keresett szó...",
                  type="text",
                  value='')),width=3)),
	html.Br(),
    dbc.Row(dbc.Col(html.Div(dcc.Dropdown(
                id="site_1",
                options=[{
                    'label': i,
                    'value': i
                } for i in st_options["site"]],
		        placeholder="első oldal...",
                value='')), width=3)),
    html.Br(),
    dbc.Row(dbc.Col(html.Div(dcc.Dropdown(
                id="site_2",
                options=[{
                    'label': i,
                    'value': i
                } for i in st_options["site"]],
		        placeholder="második oldal...",
                value='')), width=3)),

    html.Br(),
    dbc.Button("Keresés",
			   outline=True,
               color="info",
               className="mr-1",
               id='submit-button',
               n_clicks=0),
	dbc.Checklist(options=[{"label": "keresés szavakon belül", "value": 1}],
				  value=[],
				  id="switch-input",
				  switch=True,
				 ),

    dcc.Graph(id='graph_4'),
	html.Div(id="table4")])

###################################
# PAGE 4 CAHRT CALLBACK
###################################

@app.callback(Output('graph_4','figure'),
    [Input('submit-button', 'n_clicks'),
     Input('search_input', 'n_submit'),
    Input('switch-input', 'value')],
    [State('search_input', 'value'),
    State('site_1', 'value'),
    State('site_2', 'value')])

def update_site_comparison(n_clicks, n_submit, switch_value, search_word, st1, st2):
    """
    #TODO
    """
    if n_clicks or n_submit:
        search_word = search_word.strip()

        if switch_value:
          switch_value = 1

        else:
          switch_value = 0

        today = datetime.today().strftime("%Y-%m-%d")
        from_date = (datetime.today() - \
          timedelta(days = MAX_REQUEST_DAY)).strftime("%Y-%m-%d")

        api_url = f"http://pressgraphs.pythonanywhere.com/date/count/"\
        f"{API_KEY}/{search_word}/{switch_value}/{from_date}/{today}/{st1}"""
        response = requests.get(api_url)
        s_1_content = response.json()[1]["data"]
        s1_df = pd.DataFrame(s_1_content)
        s1_df.set_index("date", inplace=True)

        api_url = f"http://pressgraphs.pythonanywhere.com/date/count/"\
        f"{API_KEY}/{search_word}/{switch_value}/{from_date}/{today}/{st2}"""
        response = requests.get(api_url)
        s_2_content = response.json()[1]["data"]
        s2_df = pd.DataFrame(s_2_content)
        s2_df.set_index("date", inplace=True)

    else:
        s1_df = pd.DataFrame()
        s2_df = pd.DataFrame()

    fig = compare_two_sites(search_word=search_word,
                  site1_df=s1_df,
                  site2_df=s2_df,
                  site_1=st1,
                  site_2=st2)

    return fig

###################################
# PAGE 4 DATA TABLE CALLBACK
###################################

@app.callback(
    Output('table4', 'children'),
    [Input('graph_4', 'clickData'),
    Input('submit-button', 'n_clicks'),
    Input('switch-input', 'value')],
    [State('search_input', 'value'),
    State('site_1', 'value'),
    State('site_2', 'value')]
)

def display_clickData_4(clickData, n_clicks, switch_value, search_word, st1, st2):
    """
    #TODO
    """
    if clickData:
        search_word = search_word.strip()
        date = list(clickData["points"])[0]["x"]

        if switch_value:
          switch_value = 1

        else:
          switch_value = 0

        site_indicator = clickData["points"][0]['curveNumber']
        if site_indicator == 0:
          api_url = f"http://pressgraphs.pythonanywhere.com/date/list/"\
          f"{API_KEY}/{search_word}/{switch_value}/{date}/{date}/{st1}"

        else:
          api_url = f"http://pressgraphs.pythonanywhere.com/date/list/"\
          f"{API_KEY}/{search_word}/{switch_value}/{date}/{date}/{st2}"

        response = requests.get(api_url)
        content = response.json()[1]["data"]
        df = pd.DataFrame(content)

        return update_dt_by_date(df)

    else:
      return

###################################
# PAGE 5 LAYOUT
###################################

page_5_layout = html.Div([
	html.H5("két szó összevetése"),
    dbc.Row(dbc.Col(html.Div(
        dbc.Input(id="search_input_1",
                  placeholder="első keresett szó...",
                  type="text",
                  value='')), width=3)),
    html.Br(),
    dbc.Row(dbc.Col(html.Div(
        dbc.Input(id="search_input_2",
                  placeholder="második keresett szó...",
                  type="text",
                  value='')), width=3)),
    html.Br(),
    dbc.Button("Keresés",
			   outline=True,
               color="info",
               className="mr-1",
               id='submit-button',
               n_clicks=0),
	dbc.Checklist(options=[{"label": "keresés szavakon belül", "value": 1}],
				  value=[],
				  id="switch-input",
				  switch=True),

    dcc.Graph(id='graph_5'),
    html.Div(id="table5")])

###################################
# PAGE 5 CHART CALLBACK
###################################
@app.callback(
    Output('graph_5','figure'),
    [Input('submit-button', 'n_clicks'),
    Input('switch-input', 'value')],
    [State('search_input_1', 'value'),
    State('search_input_2', 'value')])

def update_word_comparison(n_clicks, switch_value, sw_1, sw_2):
    """
    """
    if n_clicks or n_submit:
        search_word = sw_1.strip()

        if switch_value:
          switch_value = 1

        else:
          switch_value = 0

        site="all"
        today = datetime.today().strftime("%Y-%m-%d")
        from_date = (datetime.today() - \
        timedelta(days = MAX_REQUEST_DAY)).strftime("%Y-%m-%d")

        api_url = f"http://pressgraphs.pythonanywhere.com/date/count/"\
        f"{API_KEY}/{sw_1}/{switch_value}/{from_date}/{today}/{site}"
        response = requests.get(api_url)
        content_1 = response.json()[1]["data"]
        df_1 = pd.DataFrame(content_1)
        df_1.set_index("date", inplace=True)

        api_url = f"http://pressgraphs.pythonanywhere.com/date/count/"\
        f"{API_KEY}/{sw_2}/{switch_value}/{from_date}/{today}/{site}"
        response = requests.get(api_url)
        content_2 = response.json()[1]["data"]
        df_2 = pd.DataFrame(content_2)
        df_2.set_index("date", inplace=True)

    else:
      df_1 = pd.DataFrame()
      df_2 = pd.DataFrame()
      sw_1 = ""
      sw_2 = ""

    fig = compare_two_search_words(sw_df_1=df_1,
                           sw_df_2=df_2,
                           search_word_1=sw_1,
                           search_word_2=sw_2)
    return fig

###################################
# PAGE 5 DATA TABLE CALLBACK
###################################

@app.callback(
    Output('table5', 'children'),
    [Input('graph_5', 'clickData'),
    Input('switch-input', 'value')],
    [State('search_input_1', 'value'),
    State('search_input_2', 'value')])

def display_clickData_5(clickData, switch_value, sw_1, sw_2):
    """
    #TODO
    """
    if clickData:
        sw_1 = sw_1.strip()
        sw_2 = sw_2.strip()
        date = list(clickData["points"])[0]["x"]
        site="all"

        if switch_value:
          switch_value = 1

        else:
          switch_value = 0

        sw_indicator = clickData["points"][0]['curveNumber']
        if sw_indicator == 0:
          api_url = f"http://pressgraphs.pythonanywhere.com/date/list/"\
          f"{API_KEY}/{sw_1}/{switch_value}/{date}/{date}/{site}"

        else:
          api_url = f"http://pressgraphs.pythonanywhere.com/date/list/"\
          f"{API_KEY}/{sw_2}/{switch_value}/{date}/{date}/{site}"

        response = requests.get(api_url)
        content = response.json()[1]["data"]

        df = pd.DataFrame(content)

        return update_dt_by_date(df)

    else:
      return

###################################
# CONTACT
###################################
page_6_layout = html.Div([
	html.H4("Elérhetőség"),
	dcc.Markdown(children=md_txt.contact)])

###################################
# MANUAL
###################################
page_7_layout = html.Div([
	html.H4("Használati útmutató"),
	dcc.Markdown(children=md_txt.manual)])

###################################
# SITE LIST
###################################
page_8_layout = html.Div([
  html.H4("Monitorozott oldalak listája"),
	dcc.Markdown(children=md_txt.modus_operandi)])

###################################
# RUN APP SERVER
###################################
if __name__ == '__main__':
	app.run_server(debug=True, port=8050)
  #app.run_server()
