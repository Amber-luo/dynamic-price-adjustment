# -*- coding: utf-8 -*-
import pymysql
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# ------------------ 数据库配置 ------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "960917",
    "database": "ecommerce",
    "charset": "utf8mb4"
}

# ------------------ 读取数据库数据 ------------------
def get_data():
    conn = pymysql.connect(**DB_CONFIG)
    query = "SELECT * FROM product_price;"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ------------------ 数据准备 ------------------
df = get_data()
df['profit_margin'] = (df['own_price'] - df['cost']) / df['own_price']
product_list = df['product_id'].unique()

# ------------------ Dash 应用 ------------------
app = dash.Dash(__name__)
app.title = "产品价格分析仪表盘"

app.layout = html.Div([
    html.H1("产品价格分析仪表盘", style={'textAlign': 'center'}),

    html.Div([
        html.Label("选择产品:"),
        dcc.Dropdown(
            id='product-dropdown',
            options=[{'label': str(pid), 'value': pid} for pid in product_list],
            value=product_list.tolist(),  # 默认选中所有产品
            multi=True
        )
    ], style={'width': '50%', 'margin': 'auto'}),

    html.Hr(),

    dcc.Tabs([
        dcc.Tab(label='价格分布', children=[
            dcc.Graph(id='price-distribution')
        ]),
        dcc.Tab(label='价格箱线图', children=[
            dcc.Graph(id='price-boxplot')
        ]),
        dcc.Tab(label='自家 vs 竞品价格', children=[
            dcc.Graph(id='price-scatter')
        ]),
        dcc.Tab(label='利润率柱状图', children=[
            dcc.Graph(id='profit-bar')
        ])
    ])
])

# ------------------ 回调函数 ------------------
@app.callback(
    Output('price-distribution', 'figure'),
    Output('price-boxplot', 'figure'),
    Output('price-scatter', 'figure'),
    Output('profit-bar', 'figure'),
    Input('product-dropdown', 'value')
)
def update_charts(selected_products):
    filtered_df = df[df['product_id'].isin(selected_products)]

    # 价格分布直方图
    fig_dist = px.histogram(filtered_df, x='own_price', nbins=20, 
                            title='自家产品价格分布', marginal="box", color_discrete_sequence=['skyblue'])

    # 价格箱线图
    fig_box = px.box(filtered_df, x='product_id', y='own_price', 
                     title='各产品价格箱线图', color='product_id')

    # 自家 vs 竞品价格散点图
    fig_scatter = px.scatter(filtered_df, x='competitor_price', y='own_price', color='product_id',
                             title='自家价格 vs 竞品价格', trendline="ols")
    fig_scatter.add_shape(
        type="line",
        x0=filtered_df['competitor_price'].min(),
        y0=filtered_df['competitor_price'].min(),
        x1=filtered_df['competitor_price'].max(),
        y1=filtered_df['competitor_price'].max(),
        line=dict(color="red", dash="dash")
    )

    # 利润率柱状图
    avg_margin = filtered_df.groupby('product_id')['profit_margin'].mean().reset_index()
    fig_profit = px.bar(avg_margin, x='product_id', y='profit_margin', 
                        title='各产品平均利润率', color='product_id', text='profit_margin')
    fig_profit.update_yaxes(range=[0, 1])

    return fig_dist, fig_box, fig_scatter, fig_profit

# ------------------ 启动应用 ------------------
if __name__ == '__main__':
    app.run(debug=True)
