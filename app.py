import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from urllib.parse import urlparse

# Read the CSV file
df = pd.read_csv('Life_Sciences_and_Information_Technology_Company_Listing__March_2024_20250628.csv')

# Clean and filter the data
# Remove rows where longitude or latitude is missing or invalid
df = df.dropna(subset=['Longitude', 'Latitude'])
df = df[(df['Longitude'] != 0) & (df['Latitude'] != 0)]

# Convert longitude and latitude to numeric, handling any string values
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')

# Remove any remaining invalid coordinates
df = df.dropna(subset=['Longitude', 'Latitude'])

# Clean website URLs
def clean_website(url):
    if pd.isna(url) or url == '':
        return None
    url = str(url).strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

df['Website_Clean'] = df['Website'].apply(clean_website)

# Create color mapping for business types
business_type_colors = {
    'Life Sciences': '#1f77b4',
    'Technology': '#ff7f0e'
}

# Create the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1("Cambridge Life Sciences and Technology Companies", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
    
    html.Div([
        html.Div([
            html.Label("Filter by Business Type:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='business-type-filter',
                options=[
                    {'label': 'All Companies', 'value': 'All'},
                    {'label': 'Life Sciences', 'value': 'Life Sciences'},
                    {'label': 'Technology', 'value': 'Technology'}
                ],
                value='All',
                style={'marginBottom': 20}
            )
        ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div([
            html.Label("Search Companies:", style={'fontWeight': 'bold'}),
            dcc.Input(
                id='company-search',
                type='text',
                placeholder='Enter company name...',
                style={'width': '100%', 'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px'}
            )
        ], style={'width': '40%', 'display': 'inline-block', 'marginLeft': '20px', 'verticalAlign': 'top'}),
        
        html.Div([
            html.Label("Companies Found:", style={'fontWeight': 'bold'}),
            html.Div(id='company-count', style={'fontSize': '18px', 'color': '#2c3e50'})
        ], style={'width': '25%', 'display': 'inline-block', 'marginLeft': '20px', 'verticalAlign': 'top'})
    ], style={'marginBottom': 30}),
    
    dcc.Graph(
        id='company-map',
        style={'height': '600px'}
    ),
    
    # Modal overlay for company details
    html.Div(
        id='modal-overlay',
        children=[
            html.Div([
                html.Div([
                    html.Button(
                        "×",
                        id='close-modal',
                        style={
                            'float': 'right',
                            'fontSize': '24px',
                            'fontWeight': 'bold',
                            'border': 'none',
                            'background': 'none',
                            'cursor': 'pointer',
                            'color': '#666'
                        }
                    ),
                    html.Div(id='modal-content')
                ], style={
                    'backgroundColor': 'white',
                    'padding': '30px',
                    'borderRadius': '10px',
                    'maxWidth': '600px',
                    'maxHeight': '80vh',
                    'overflow': 'auto',
                    'position': 'relative',
                    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
                })
            ], style={
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center',
                'height': '100vh'
            })
        ],
        style={
            'position': 'fixed',
            'top': 0,
            'left': 0,
            'width': '100%',
            'height': '100%',
            'backgroundColor': 'rgba(0,0,0,0.5)',
            'zIndex': 1000,
            'display': 'none'
        }
    )
])

@app.callback(
    [Output('company-map', 'figure'),
     Output('company-count', 'children')],
    [Input('business-type-filter', 'value'),
     Input('company-search', 'value')]
)
def update_map(business_type, search_term):
    # Filter data based on business type
    if business_type != 'All':
        filtered_df = df[df['Business Type'] == business_type].copy()
    else:
        filtered_df = df.copy()
    
    # Filter by search term if provided
    if search_term and search_term.strip():
        search_term = search_term.lower()
        filtered_df = filtered_df[
            filtered_df['Business Name'].str.lower().str.contains(search_term, na=False)
        ]
    
    # Create the map
    fig = go.Figure()
    
    # Add markers for each company
    for _, company in filtered_df.iterrows():
        # Determine color based on business type
        color = business_type_colors.get(company['Business Type'], '#7f7f7f')
        
        # Create hover text
        hover_text = f"<b>{company['Business Name']}</b><br>"
        hover_text += f"Type: {company['Business Type']}<br>"
        hover_text += f"Address: {company['Address']}, {company['City']}, {company['State']} {company['Zip Code']}<br>"
        
        if pd.notna(company['Business Description']) and company['Business Description']:
            # Truncate description if too long
            desc = company['Business Description']
            if len(desc) > 100:
                desc = desc[:100] + "..."
            hover_text += f"Description: {desc}<br>"
        
        if company['Website_Clean']:
            hover_text += f"Website: {company['Website_Clean']}"
        
        # Add marker
        fig.add_trace(go.Scattermapbox(
            lat=[company['Latitude']],
            lon=[company['Longitude']],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=10,
                color=color,
                opacity=0.8
            ),
            text=hover_text,
            hoverinfo='text',
            name=company['Business Name'],
            customdata=[[
                company['Business Name'],
                company['Business Type'],
                company['Address'],
                company['City'],
                company['State'],
                company['Zip Code'],
                company['Business Description'],
                company['Website_Clean'],
                company['Year Established']
            ]]
        ))
    
    # Update layout
    fig.update_layout(
        mapbox=dict(
            style='open-street-map',
            center=dict(lat=42.3736, lon=-71.1097),  # Cambridge, MA center
            zoom=12
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        height=600
    )
    
    return fig, f"{len(filtered_df)} companies"

@app.callback(
    [Output('modal-overlay', 'style'),
     Output('modal-content', 'children')],
    [Input('company-map', 'clickData'),
     Input('close-modal', 'n_clicks')],
    [State('modal-overlay', 'style')]
)
def toggle_modal(clickData, close_clicks, modal_style):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return {'position': 'fixed', 'top': 0, 'left': 0, 'width': '100%', 'height': '100%', 'backgroundColor': 'rgba(0,0,0,0.5)', 'zIndex': 1000, 'display': 'none'}, []
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'close-modal':
        return {'position': 'fixed', 'top': 0, 'left': 0, 'width': '100%', 'height': '100%', 'backgroundColor': 'rgba(0,0,0,0.5)', 'zIndex': 1000, 'display': 'none'}, []
    
    if trigger_id == 'company-map' and clickData:
        # Get the clicked company data
        custom_data = clickData['points'][0]['customdata']
        
        company_name = custom_data[0]
        business_type = custom_data[1]
        address = custom_data[2]
        city = custom_data[3]
        state = custom_data[4]
        zip_code = custom_data[5]
        description = custom_data[6]
        website = custom_data[7]
        year_established = custom_data[8]
        
        # Create the modal content
        modal_content = [
            html.H2(company_name, style={'color': '#2c3e50', 'marginBottom': 15, 'marginRight': 30}),
            html.Div([
                html.Strong("Business Type: "), html.Span(business_type)
            ], style={'marginBottom': 10}),
            html.Div([
                html.Strong("Address: "), html.Span(f"{address}, {city}, {state} {zip_code}")
            ], style={'marginBottom': 10}),
        ]
        
        if pd.notna(year_established) and year_established:
            modal_content.append(
                html.Div([
                    html.Strong("Year Established: "), html.Span(str(year_established))
                ], style={'marginBottom': 10})
            )
        
        if pd.notna(description) and description:
            modal_content.append(
                html.Div([
                    html.Strong("Description: "), html.Span(description)
                ], style={'marginBottom': 15})
            )
        
        if website:
            modal_content.append(
                html.A(
                    "Visit Website", 
                    href=website, 
                    target="_blank",
                    style={
                        'backgroundColor': '#3498db',
                        'color': 'white',
                        'padding': '12px 24px',
                        'textDecoration': 'none',
                        'borderRadius': '5px',
                        'display': 'inline-block',
                        'fontWeight': 'bold',
                        'marginTop': '10px'
                    }
                )
            )
        
        return {'position': 'fixed', 'top': 0, 'left': 0, 'width': '100%', 'height': '100%', 'backgroundColor': 'rgba(0,0,0,0.5)', 'zIndex': 1000, 'display': 'block'}, modal_content
    
    return {'position': 'fixed', 'top': 0, 'left': 0, 'width': '100%', 'height': '100%', 'backgroundColor': 'rgba(0,0,0,0.5)', 'zIndex': 1000, 'display': 'none'}, []

if __name__ == '__main__':
    app.run(debug=True)
