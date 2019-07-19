import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from megaqc.api.utils import get_sample_metadata_fields


def _get_field_options(app):
    with app.server.app_context():
        fields = get_sample_metadata_fields()
        print(fields)
    return [{'label': d['nicename'], 'value': d['type_id']} for d in fields]


def field_select(app):
    """
    Re-useable component for selecting sample fields to plot
    """
    if app.server is not None and 'SQLALCHEMY_TRACK_MODIFICATIONS' in app.server.config:
        fields = _get_field_options(app)
    else:
        fields = []

    return dbc.Card([
        dbc.CardHeader([
            "Choose Fields to Plot"
        ], tag='h4'),
        dbc.CardBody(
            [
                dcc.Dropdown(
                    options=fields,
                    id='field_select',
                    multi=True,
                ),
            ]
        ),
    ])
