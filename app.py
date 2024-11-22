import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output

data = pd.read_csv('CHIRS_cancer_data.csv')

# Create a list of unique counties and indicators for dropdown options
counties = data['County Name'].unique()
indicators = data['Indicator Name'].unique()

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the dashboard
app.layout = html.Div([
    html.H1("Cancer Trends in New York State", style={'textAlign': 'center'}),
    
    # Dropdowns for selecting county and indicator
   # Container for dropdowns and titles
    html.Div([
        html.Div([
            html.Label("Select County:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='county-dropdown',
                options=[{'label': county, 'value': county} for county in counties],
                value=counties[0],  # Default county
                style={'width': '100%', 'margin': '10px'}
            ),
        ], style={'width': '45%', 'display': 'inline-block', 'margin': '10px'}),
        
        html.Div([
            html.Label("Select Indicator:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='indicator-dropdown',
                options=[{'label': indicator, 'value': indicator} for indicator in indicators],
                value=indicators[0],  # Default indicator
                style={'width': '100%', 'margin': '10px'}
            ),
        ], style={'width': '45%', 'display': 'inline-block', 'margin': '10px'})
    ], style={'textAlign': 'center'}),
    
    # Graph to show cancer trends over time
    dcc.Graph(id='trend-graph'),
    
    # Display percentage change
    html.Div(id='percentage-change', style={'fontSize': '20px', 'textAlign': 'center'}),
    
    # Play button to animate the trend
    html.Div([
        dcc.Interval(id='animate-interval', interval=1000, n_intervals=0, disabled=True),
        html.Button("Play Animation", id='play-button', n_clicks=0, style={'fontSize': '20px', 'marginTop': '20px'}),
    ], style={'textAlign': 'center'})
])

# Callback to update the trend graph based on selected county and indicator
@app.callback(
    [Output('trend-graph', 'figure'),
     Output('percentage-change', 'children')],
    [Input('county-dropdown', 'value'),
     Input('indicator-dropdown', 'value'),
     Input('animate-interval', 'n_intervals')]
)
def update_graph(county, indicator, n_intervals):
    # Filter the data based on selected county and indicator
    filtered_data = data[(data['County Name'] == county) & (data['Indicator Name'] == indicator)]

    # Calculate the percentage change between the first and last year
    start_year = filtered_data['Date Year'].min()
    end_year = filtered_data['Date Year'].max()
    start_value = filtered_data[filtered_data['Date Year'] == start_year]['Trend Data County Value'].iloc[0]
    end_value = filtered_data[filtered_data['Date Year'] == end_year]['Trend Data County Value'].iloc[0]
    
    percentage_change = ((end_value - start_value) / start_value) * 100
    
    # Prepare the data to be displayed (show only up to n_intervals data points)
    data_to_plot = filtered_data.iloc[:n_intervals + 1]

    # Create the trace for the line chart
    trace = go.Scatter(
        x=data_to_plot['Date Year'],
        y=data_to_plot['Trend Data County Value'],
        mode='lines+markers',
        name=f'{county} - {indicator}'
    )

    # Create layout for the plot with zooming enabled on the Y-axis
    layout = go.Layout(
        title=f"Cancer Trend for {county} ({indicator})",
        xaxis={'title': 'Year'},
        yaxis={'title': 'Cancer Rate', 'fixedrange': False},  # Enable zooming on Y-axis
        showlegend=True,
        hovermode='closest',
        dragmode='zoom'  # Enable zoom interaction
    )

    figure = {'data': [trace], 'layout': layout}

    # Return the graph and the percentage change text
    percentage_text = f"Percentage Change: {percentage_change:.2f}% from {start_year} to {end_year}"
    
    return figure, percentage_text

# Callback to handle the play button for animation
@app.callback(
    Output('animate-interval', 'disabled'),
    [Input('play-button', 'n_clicks')]
)
def toggle_animation(n_clicks):
    if n_clicks > 0:
        return False  # Enable animation
    return True  # Disable animation
    
server = app.server

# Running the app
if __name__ == '__main__':    
    port = int(os.getenv("PORT", "10000"))  # Default to 10000 if PORT is not set
    app.run_server(host="0.0.0.0", port=port, debug=True)
