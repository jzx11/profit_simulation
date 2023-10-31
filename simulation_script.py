import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import plotly.express as px
from scipy.stats import dgamma, weibull_min

# Create the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    # Wrap TR_3P Slider and its label in a Div
    html.Div([
        html.Label("TR_3P"),
        dcc.Slider(
            id='TR_3P-slider',
            min=0.15,
            max=0.5,
            step=0.01,
            value=0.25,
            marks={i: f"{i:.2f}" for i in np.arange(0.15, 0.51, 0.05)}
        ),
    ], style={'margin-bottom': '20px'}),  # Apply margin-bottom to the wrapping Div

    # Wrap GMV input and its label in a Div
    html.Div([
        html.Label("GMV"),
        dcc.Input(id="GMV-input", value=1000000, type="number")
    ], style={'margin-bottom': '20px'}),

    # Wrap GMV_PCT_1P2P slider and its label in a Div
    html.Div([
        html.Label("GMV_PCT_1P2P"),
        dcc.Slider(
            id='GMV_PCT_1P2P-slider',
            min=0,
            max=1,
            step=0.01,
            value=0.2,
            marks={i/10: f"{i/10}" for i in range(11)}
        ),
    ], style={'margin-bottom': '20px'}),

    # Wrap TR_1P2P slider and its label in a Div
    html.Div([
        html.Label("TR_1P2P"),
        dcc.Slider(
            id='TR_1P2P-slider',
            min=0,
            max=1,
            step=0.01,
            value=0.42,
            marks={i/10: f"{i/10}" for i in range(11)}
        ),
    ], style={'margin-bottom': '20px'}),

    # Wrap ATV input and its label in a Div
    html.Div([
        html.Label("ATV"),
        dcc.Input(id="ATV-input", value=83, type="number")
    ], style={'margin-bottom': '20px'}),
    
    html.Div(id='slider-output', style={'margin': '25px 0'}),
    dcc.Graph(id='simulation-graph')
])


@app.callback(
    [Output('simulation-graph', 'figure'),
     Output('slider-output', 'children')],
    [Input('TR_3P-slider', 'value'),
     Input('GMV-input', 'value'),
     Input('GMV_PCT_1P2P-slider', 'value'),
     Input('TR_1P2P-slider', 'value'),
     Input('ATV-input', 'value')]
)
def update_figure(TR_3P, GMV, GMV_PCT_1P2P, TR_1P2P, ATV):
    
    # Use the variables directly in your function
    GMV_PCT_3P = 1-GMV_PCT_1P2P
    
    # Number of simulations
    n_simulations = 10000
    
    # Initialize arrays to store results
    Transactions_results = np.zeros(n_simulations)
    COUPON_PER_TRANSACTION_results = np.zeros(n_simulations)
    ADS_PCT_GMV_results = np.zeros(n_simulations)
    NET_INFLOW_results = np.zeros(n_simulations)

    matching_combinations = []

    for sim in range(n_simulations):
        # Sample from distributions for each variable

        COUPON_PER_TRANSACTION = dgamma.rvs(a=1.8156, loc=68.32, scale=5.225)

        ADS_PCT_GMV = weibull_min.rvs(c=0.808, loc=0.0072, scale=0.062)

        # Calculate Intermediate Outputs

        Transactions = GMV/ATV

        Fees_1P2P = GMV * GMV_PCT_1P2P * TR_1P2P

        Fees_3P = GMV * GMV_PCT_3P * TR_3P

        Ads_Rev = GMV * ADS_PCT_GMV

        Total_Inflow = Fees_1P2P + Fees_3P + Ads_Rev

        Total_Coupons = COUPON_PER_TRANSACTION * Transactions

        # Calculate Final Outputs

        Net_Inflow = Total_Inflow - Total_Coupons


        # Store results in arrays
        Transactions_results[sim] = Transactions
        COUPON_PER_TRANSACTION_results[sim] = COUPON_PER_TRANSACTION
        ADS_PCT_GMV_results[sim] = ADS_PCT_GMV
        NET_INFLOW_results[sim] = Net_Inflow
    
    # Convert results arrays to a dataframe
    df = pd.DataFrame({
        'COUPON_PER_TRANSACTION': COUPON_PER_TRANSACTION_results,
        'ADS_PCT_GMV': ADS_PCT_GMV_results,
        'Net_Inflow': NET_INFLOW_results
    })

    # Filter out only the positive Net_Inflow results
    df_positive = df[df['Net_Inflow'] > 0]

    df_positive['ADS_PCT_GMV'] = df_positive['ADS_PCT_GMV']# Convert to percentage for visualization
    

    fig = px.scatter(df_positive, 
                     x='ADS_PCT_GMV', 
                     y='COUPON_PER_TRANSACTION', 
                     color='Net_Inflow',
                     size='Net_Inflow',
                     hover_data=['Net_Inflow'],
                     custom_data=['Net_Inflow'],
                     color_continuous_scale=px.colors.sequential.Viridis)

    fig.update_xaxes(tickformat=".0%")
    fig.update_traces(hovertemplate="ADS_PCT_GMV: %{x:.2%}<br>COUPON_PER_TRANSACTION: %{y:.2f}<br>Net_Inflow: %{customdata[0]:.2f}")

    return fig, f"Selected TR_3P value: {TR_3P:.2f}"

# Run the app
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)
