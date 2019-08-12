from megaqc.model import models, schemas
import megaqc.user.models as user_models

from pkg_resources import resource_stream


def test_get_report_list(mix, db, client):
    db.session.bulk_save_objects([
        mix.blend(
            models.Report,
            user=mix.blend(user_models.User),
            report_meta=mix.cycle(5).blend(models.ReportMeta),
            samples=mix.cycle(3).blend(models.Sample)
        )
    ])

    rv = client.get('/rest_api/v1/reports')

    # Check the request was successful
    assert rv.status_code == 200

    # Check that the returned data matches the schema
    errors = schemas.ReportSchema(many=True, session=db.session).validate(rv.json)
    assert len(errors) == 0


def test_post_report_list(db, client, token):
    rv = client.post(
        '/rest_api/v1/reports',
        data={'report': resource_stream('tests', 'multiqc_data.json')},
        headers={'access_token': token}
    )

    # Check the request was successful
    assert rv.status_code == 200

    # Check that there is a new Upload
    uploads = db.session.query(models.Upload).count()
    assert uploads == 1


def test_get_report(mix, db, client):
    rid = 1
    db.session.bulk_save_objects([
        mix.blend(
            models.Report,
            report_id=rid,
            user=mix.blend(user_models.User),
            report_meta=mix.cycle(5).blend(models.ReportMeta),
            samples=mix.cycle(3).blend(models.Sample)
        )
    ])

    rv = client.get('/rest_api/v1/reports/{}'.format(rid))

    # Check the request was successful
    assert rv.status_code == 200

    # Check that the returned data matches the schema
    errors = schemas.ReportSchema(many=False, session=db.session).validate(rv.json)
    assert len(errors) == 0


def test_delete_report(mix, db, client, token, admin_token):
    rid = 1
    db.session.add_all([
        mix.blend(
            models.Report,
            report_id=rid,
            user=mix.blend(user_models.User),
            report_meta=mix.cycle(5).blend(models.ReportMeta),
            samples=mix.cycle(3).blend(models.Sample)
        )
    ])

    # Check that there is one report
    uploads = db.session.query(models.Report).count()
    assert uploads == 1

    # Non-logged in users and non-admin users shouldn't be able to delete reports
    assert client.delete('/rest_api/v1/reports/{}'.format(rid)).status_code == 403
    assert client.delete('/rest_api/v1/reports/{}'.format(rid), headers={'access_token': token}).status_code == 403

    rv = client.delete('/rest_api/v1/reports/{}'.format(rid), headers={'access_token': admin_token})

    # Check the request was successful, as an admin
    assert rv.status_code == 200

    # Check that we deleted the report
    uploads = db.session.query(models.Report).count()
    assert uploads == 0
