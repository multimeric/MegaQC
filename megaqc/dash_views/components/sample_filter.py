import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc


def sample_filter(num_samples, sample_filters):
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
        filter_groups.append(
            dbc.NavLink([
                sfg
            ], active=first_group)
        )

        for j, sf in enumerate(sample_filters[sfg]):
            first_filter = j == 0
            filters.append(
                dbc.ListGroup([
                    html.Button(
                        [
                            sf['name']
                        ],
                        className="sample-filter-btn list-group-item list-group-item-action" + (" active" if first_filter else ""),
                        **{
                            'data-filterid': sf['id']
                        }
                    )
                ])
            )

    return dbc.Card([
        dbc.CardBody([
            html.H4([
                "Filter Samples",
                dbc.Badge("{} Samples".format(num_samples), color=badge_colour, className="ml-1", pill=True),
                dbc.Button([
                    "Add"
                ], color='primary', outline=True, size='sm', className='float-right')
            ], className="card-title"),

            dbc.Row([
                dbc.Col([
                    dbc.Nav(filter_groups, className='nav-pills')
                ], md=4),
                dbc.Col(filters, md=8)
            ])
        ])
    ])
