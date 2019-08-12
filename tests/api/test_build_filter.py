import datetime

from megaqc.model import models
from megaqc.api.filters import build_filter_query, DATE_FORMAT


def test_daterange_in(self, filter_test_types, filter_test_reports, db):
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


def test_daterange_not_in(self, filter_test_types, filter_test_reports, db):
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
                'cmp': 'not in'
            }
        ]
    ])
    data = query.with_entities(
        models.Report.created_at,
        models.SampleData.value,
        models.Sample.sample_id,
        models.Report.report_id
    ).all()

    # This should return 2 samples
    assert len(data) == 2

    # These samples should come from only 1 reports
    reports = set([sample.report_id for sample in data])
    assert len(reports) == 1

    # Specifically, it should be the last report that is returned
    assert filter_test_reports[2].report_id in reports


def test_timedelta_in(self, filter_test_types, filter_test_reports, db):
    db.session.add_all(filter_test_types + filter_test_reports)

    # Finds all samples uploaded in the last 2 days
    query = build_filter_query([
        [
            {
                'type': 'timedelta',
                'value': 2,
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


def test_timedelta_not_in(self, filter_test_types, filter_test_reports, db):
    db.session.add_all(filter_test_types + filter_test_reports)

    # Finds all samples uploaded in the last 2 days
    query = build_filter_query([
        [
            {
                'type': 'timedelta',
                'value': 2,
                'cmp': 'not in'
            }
        ]
    ])
    data = query.with_entities(
        models.Report.created_at,
        models.SampleData.value,
        models.Sample.sample_id,
        models.Report.report_id
    ).all()

    # This should return 2 samples
    assert len(data) == 2

    # These samples should come from only 1 reports
    reports = set([sample.report_id for sample in data])
    assert len(reports) == 1

    # Specifically, it should be the last report that is returned
    assert filter_test_reports[2].report_id in reports


def test_reportmeta(self):
    pass


def test_samplemeta(self):
    pass
