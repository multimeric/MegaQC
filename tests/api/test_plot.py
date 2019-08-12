from flask import url_for
from plotly.offline import plot
import json
import pytest
import datetime

import megaqc.user.models as user_models
from megaqc.model import models
from megaqc.api.filters import build_filter_query, DATE_FORMAT


class TestPlotApi:
    @staticmethod
    def test_get_trend_series(mix, db, client):
        # Create 5 reports each with 1 sample. Each has a single field called 'test_field'
        data_type = mix.blend(models.SampleDataType, data_key='test_field')
        report = mix.cycle(5).blend(
            models.Report,
            created_at=lambda: mix.faker.date_time(),
            user=mix.blend(user_models.User),
            samples=lambda: mix.blend(
                models.Sample,
                data=lambda: mix.cycle(1).blend(models.SampleData, data_type=data_type,
                                                value=mix.faker.small_positive_integer)
            )

        )
        db.session.add_all([
            data_type,
            *report
        ])

        response = client.get(url_for('rest_api.trend_data', filter=json.dumps([]), fields=json.dumps(['test_field'])))

        # Check the request was successful
        assert response.status_code == 200

        # Check that there are 3 series (mean, stdev, raw data)
        assert len(response.json) == 3

        # Test that this is valid plot data
        plot({'data': response.json}, validate=True, auto_open=False)


@pytest.fixture()
def filter_test_types(mix):
    return [
        mix.blend(models.SampleDataType, data_key='field_1'),
        mix.blend(models.SampleDataType, data_key='field_2')
    ]


@pytest.fixture()
def filter_test_reports(mix, filter_test_types):
    types = filter_test_types
    return [
        mix.blend(
            models.Report,
            created_at=datetime.datetime.now() - datetime.timedelta(days=1),
            samples=[
                mix.blend(models.Sample, data=[
                    mix.blend(models.SampleData, type=types[0], value=1),
                    mix.blend(models.SampleData, type=types[1], value=1),
                ])
            ],
            meta=[
                mix.blend(models.ReportMeta, report_meta_key='key_1', report_meta_value=1),
                mix.blend(models.ReportMeta, report_meta_key='key_2', report_meta_value=1),
            ]
        ),
        mix.blend(
            models.Report,
            created_at=datetime.datetime.now() - datetime.timedelta(days=2),
            samples=[
                mix.blend(models.Sample, data=[
                    mix.blend(models.SampleData, type=types[0], value=2),
                    mix.blend(models.SampleData, type=types[1], value=2),
                ])
            ],
            meta=[
                mix.blend(models.ReportMeta, report_meta_key='key_1', report_meta_value=2),
                mix.blend(models.ReportMeta, report_meta_key='key_2', report_meta_value=2),
            ]
        ),
        mix.blend(
            models.Report,
            created_at=datetime.datetime.now() - datetime.timedelta(days=3),
            samples=[
                mix.blend(models.Sample, data=[
                    mix.blend(models.SampleData, type=types[0], value=3),
                    mix.blend(models.SampleData, type=types[1], value=3),
                ])
            ],
            meta=[
                mix.blend(models.ReportMeta, report_meta_key='key_1', report_meta_value=3),
                mix.blend(models.ReportMeta, report_meta_key='key_2', report_meta_value=3),
            ]
        )
    ]


class TestFilterApi:
    def test_daterange(self, filter_test_types, filter_test_reports, db):
        db.session.add_all(filter_test_types + filter_test_reports)

        # Finds all samples uploaded in the last 2 days
        query = build_filter_query([
            [
                {
                    'type': 'daterange',
                    'value': [
                        (datetime.datetime.now() - datetime.timedelta(days=2)).strftime(DATE_FORMAT),
                        (datetime.datetime.now()).strftime(DATE_FORMAT),
                    ],
                    'cmp': 'in'
                }
            ]
        ])
        data = query.with_entities(
            models.Report.created_at,
            models.SampleData.value,
            models.Sample.sample_id,
            models.Report.report_id
        ).all()

        # This should return 4 samples
        assert len(data) == 4

        # These samples should come from only 2 reports
        reports = set([sample.report_id for sample in data])
        assert len(reports) == 2

        # Specifically, it should be the first two reports that are returned
        assert filter_test_reports[0].report_id in reports
        assert filter_test_reports[1].report_id in reports

    def test_timedelta(self,filter_test_types, filter_test_reports, db):
        db.session.add_all(filter_test_types + filter_test_reports)

        # Finds all samples uploaded in the last 2 days
        query = build_filter_query([
            [
                {
                    'type': 'timedelta',
                    'value': [
                        (datetime.datetime.now() - datetime.timedelta(days=2)).strftime(DATE_FORMAT),
                        (datetime.datetime.now()).strftime(DATE_FORMAT),
                    ],
                    'cmp': 'in'
                }
            ]
        ])
        data = query.with_entities(
            models.Report.created_at,
            models.SampleData.value,
            models.Sample.sample_id,
            models.Report.report_id
        ).all()

        # This should return 4 samples
        assert len(data) == 4

        # These samples should come from only 2 reports
        reports = set([sample.report_id for sample in data])
        assert len(reports) == 2

        # Specifically, it should be the first two reports that are returned
        assert filter_test_reports[0].report_id in reports
        assert filter_test_reports[1].report_id in reports

    def test_reportmeta(self):
        pass

    def test_samplemeta(self):
        pass
