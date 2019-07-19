import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from megaqc.dash_views.components.python_component import PythonComponent


class SampleFilter(PythonComponent):
    def __init__(self):
        super().__init__()
        self.filter_groups = []
        self.filters = []

        # We define inputs at creation time, because we need access to their IDs for callback setup
        self.define_input('num-samples', self.box(0))
        self.define_input('sample-filters', {})
        self.define_output('selected-filter', '')

    def layout(self, num_samples, sample_filters, app):
        # At layout time we have access to the default store values, so set them now
        self.inputs['num-samples'].data = self.box(num_samples)
        self.inputs['sample-filters'].data = sample_filters

        return super().layout()

    def render(self, num_samples, sample_filters, app):
        num_samples = self.unbox(num_samples)

        if num_samples == 0:
            badge_colour = 'warning'
        elif num_samples >= 100:
            badge_colour = 'danger'
        else:
            badge_colour = 'success'

        filter_groups = []
        filters = []
        for i, sfg in enumerate(sorted(sample_filters.keys())):
            first_group = i == 0
            filter_id = '{}-filter-group-{}'.format(self.id, i)

            filter_groups.append(
                html.Div([
                    dbc.NavLink([
                        sfg
                    ],
                        active=first_group
                    )
                ], id=filter_id)
            )

            for j, sf in enumerate(sample_filters[sfg]):
                filter_id = '{}-filter-{}'.format(self.id, i)

                first_filter = j == 0
                filters.append(
                    dbc.ListGroup([
                        html.Button(
                            [
                                sf['name']
                            ],
                            className="sample-filter-btn list-group-item list-group-item-action" + (
                                " active" if first_filter else ""),
                            **{
                                'data-filterid': sf['id']
                            }
                        )
                    ])
                )

        return dbc.Card([
                            dbc.CardHeader([
                                "Filter Samples",
                                dbc.Badge("{} Samples".format(num_samples), color=badge_colour,
                                          className="ml-1", pill=True),
                                dbc.Button([
                                    "Add"
                                ], color='primary', outline=True, size='sm', className='float-right')
                            ], tag='h4'),
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Nav(filter_groups, pills=True, className='flex-column')
                                    ], md=4),
                                    dbc.Col(filters, md=8)
                                ])
                            ]),

                        ] + self.state_components())

    def setup_callbacks(self, app):
        super().setup_callbacks(app)

        # for filter_id, filter_value in self.filters:
        #     @app.callback(
        #         Output(self.outputs['selected_filter'].id, 'data'),
        #         [Input(filter_id, 'n_clicks')]
        #     )
        #     def filter_chosen():
        #         """
        #         When a new filter is selected, update the store with the filter name
        #         """
        #         return filter_value
