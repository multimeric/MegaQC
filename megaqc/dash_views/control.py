import dash_html_components as html
import dash_core_components as dcc
import dash
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import json
from numpy import std, mean, repeat, concatenate, flip

from megaqc.megaqc_dash import MegaQcDash
from megaqc.extensions import db
from megaqc.api.utils import get_sample_metadata_fields, aggregate_new_parameters
from megaqc.model.models import Sample, SampleData, SampleDataType, Report
from megaqc.public.views import order_sample_filters
from flask_login import login_required, login_user, logout_user, current_user

import dash_bootstrap_components as dbc
from megaqc.dash_views.components.field_select import field_select
from megaqc.dash_views.components.sample_filter import SampleFilter


def get_field_options():
    with app.server.app_context():
        fields = get_sample_metadata_fields()
        print(fields)
    return [{'label': d['nicename'], 'value': d['type_id']} for d in fields]


def get_plot(fields=[], filter=None):
    plots = []
    for field in fields:
        data = db.session.query(
            Report.created_at,
            SampleData.value
        ).select_from(
            Sample
        ).join(
            SampleData, Sample.sample_id == SampleData.sample_id
        ).join(
            SampleDataType, SampleData.sample_data_type_id == SampleDataType.sample_data_type_id
        ).join(
            Report, Report.report_id == Sample.report_id
        ).filter(
            SampleDataType.sample_data_type_id == field
        ).order_by(
            Report.created_at.asc(),
        ).all()

        x, y = zip(*data)
        y = [float(num) for num in y]

        # Add the raw data
        plots.append(go.Scatter(
            x=x,
            y=y,
            line=dict(color='rgb(0,100,80)'),
            mode='markers',
            name=field,
        ))

        # Add the mean
        y2 = repeat(mean(y), len(x))
        plots.append(go.Scatter(
            x=x,
            y=y2,
            line=dict(color='rgb(0,100,80)'),
            mode='lines',
            showlegend=False,
        ))

        # Add the stdev
        x3 = concatenate((x, flip(x, axis=0)))
        stdev = repeat(std(y), len(x))
        upper = y2 + stdev
        lower = y2 - stdev
        y3 = concatenate((lower, upper))
        plots.append(go.Scatter(
            x=x3,
            y=y3,
            fill='tozerox',
            fillcolor='rgba(0,100,80,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            # line=dict(color='rgb(0,100,80)'),
            # mode='lines',
            showlegend=False,
        ))

    return go.Figure(
        data=plots,
        layout=go.Layout(
            title='Data Trend',
            # showlegend=True,
            # legend=go.layout.Legend(
            #     x=0,
            #     y=1.0
            # ),
            # margin=go.layout.Margin(l=40, r=0, t=40, b=30)
        )
    )


app = MegaQcDash(routes_pathname_prefix='/dash/trend/', server=False, suppress_callback_exceptions=True)
sample_filter = SampleFilter()


def layout():
    if app.server is not None and 'SQLALCHEMY_TRACK_MODIFICATIONS' in app.server.config:
        fields = get_field_options()
        sample_filters = order_sample_filters()
        return_data = aggregate_new_parameters(current_user, [], False)
        num_samples = return_data[0]
        report_fields = return_data[1],
        sample_fields = return_data[2],
        report_fields_json = json.dumps(return_data[1]),
        sample_fields_json = json.dumps(return_data[2])
    else:
        fields = []
        sample_filters = {}
        num_samples = 0


    return html.Div([
        html.H1(['Data Trends']),

        dbc.Row([
            dbc.Col([
                sample_filter.layout(num_samples=num_samples, sample_filters=sample_filters, app=app)
            ], md=6),
            dbc.Col([
                field_select(app),
            ], md=6)
        ], className='mb-2'),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Trend Plot", className="card-title"),
                        dcc.Graph(
                            id='trend',
                            figure=get_plot()
                        )
                    ])
                ])
            ])
        ])
    ])


def setup_callbacks(app):
    sample_filter.setup_callbacks(app)

    @app.callback(
        Output('trend', 'figure'),
        [
            Input('field_select', 'value'),
            Input(sample_filter.outputs['selected-filter'].id, 'data')
        ]
    )
    def update_fields(field, filter):
        if field is None:
            field = []
        return get_plot(field)


setup_callbacks(app)


app.layout = layout