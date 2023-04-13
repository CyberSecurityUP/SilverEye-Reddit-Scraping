import dash
from dash import dcc, html, Input, Output
import dash_table
import pandas as pd
import praw
import plotly.graph_objs as go


# https://www.reddit.com/prefs/apps/

reddit = praw.Reddit(client_id='YOUR CLIENT ID',
                     client_secret='YOUR CLIENT SECRET',
                     user_agent='Karma breakdown 1.0 by /u/_Daimon_')

def get_posts(hashtag):
    posts = []
    for post in reddit.subreddit('all').search(f'#{hashtag}'):
        posts.append((post.author.name, post.title, post.shortlink, post.selftext))
    return pd.DataFrame(posts, columns=['Author', 'Title', 'Link', 'Message'])

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Scraping do Reddit com Dash'),
    dcc.Input(id='hashtag-input', type='text', value='python'),
    html.Button(id='submit-button', n_clicks=0, children='Pesquisar'),
    dcc.Tabs(id='tabs', children=[
        dcc.Tab(label='Gráficos', children=[
            html.Div(id='graphs', children=[
                html.H2(children='Posts e usuários'),
                dcc.Graph(
                    id='post-count',
                    figure={'data': []}
                ),
                dcc.Graph(
                    id='user-count',
                    figure={'data': []}
                ),
            ])
        ]),
        dcc.Tab(label='Detalhes', children=[
            html.Div(id='details', children=[
                html.H2(children='Detalhes dos posts'),
                dash_table.DataTable(
                    id='post-table',
                    columns=[
                        {'name': 'Link', 'id': 'Link'},
                        {'name': 'Autor', 'id': 'Author'},
                        {'name': 'Mensagem', 'id': 'Message'}
                    ],
                    data=[],
                    style_cell={'textAlign': 'left'}
                )
            ])
        ])
    ])
])

@app.callback(
    [Output('post-count', 'figure'),
     Output('user-count', 'figure'),
     Output('post-table', 'data')],
    [Input('submit-button', 'n_clicks')],
    [Input('hashtag-input', 'value')]
)
def update_output(n_clicks, hashtag):
    df = get_posts(hashtag)
    n_posts = len(df)
    n_users = len(df['Author'].unique())
    post_count_fig = {'data': [go.Bar(x=['Posts'], y=[n_posts])]}
    user_count_fig = {'data': [go.Bar(x=['Usuários'], y=[n_users])]}
    return post_count_fig, user_count_fig, df.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)

