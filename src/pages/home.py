import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/')

layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H1("Welcome to Northeastern Airways", className="mb-4"),
            html.P(
                "Book your next journey across the UK with Northeastern Airways, "
                "your trusted partner for reliable and comfortable air travel.",
                className="lead"
            ),
            dbc.Card([
                dbc.CardImg(src="/assets/plane-banner.jpg", top=True),
                dbc.CardBody([
                    html.H4("Find Your Flight", className="card-title"),
                    html.P(
                        "Search for available flights and book your next journey.",
                        className="card-text"
                    ),
                    dbc.Button("Search Flights", color="primary", href="/flights")
                ])
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Quick Booking", className="card-title"),
                            html.P(
                                "Already know your travel dates? Book directly!",
                                className="card-text"
                            ),
                            dbc.Button("Book Now", color="success", href="/bookings/new")
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Check-in Online", className="card-title"),
                            html.P(
                                "Save time at the airport with our easy online check-in.",
                                className="card-text"
                            ),
                            dbc.Button("Check-in", color="info", href="/check-in")
                        ])
                    ])
                ], width=6)
            ])
        ], width=8),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Latest Updates"),
                dbc.CardBody([
                    html.H5("New Summer Routes Added!", className="card-title"),
                    html.P(
                        "We've added new routes for the summer season. "
                        "Explore our destinations and plan your holiday!",
                        className="card-text"
                    ),
                    html.Hr(),
                    html.H5("COVID-19 Travel Information", className="card-title"),
                    html.P(
                        "We're committed to ensuring your safety during travel. "
                        "Check our latest COVID-19 policies before your journey.",
                        className="card-text"
                    ),
                    html.Hr(),
                    html.H5("Special Offers", className="card-title"),
                    html.P(
                        "Book your flight today and enjoy special discounts "
                        "on selected destinations.",
                        className="card-text"
                    )
                ])
            ], className="mb-4"),
            
            dbc.Card([
                dbc.CardHeader("Quick Links"),
                dbc.ListGroup([
                    dbc.ListGroupItem("Flight Status", href="/status"),
                    dbc.ListGroupItem("Baggage Information", href="/baggage"),
                    dbc.ListGroupItem("Contact Us", href="/contact"),
                    dbc.ListGroupItem("FAQs", href="/faqs"),
                ], flush=True)
            ])
        ], width=4)
    ])
]) 