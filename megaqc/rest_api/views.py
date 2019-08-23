"""
Location of a rewritten API in a RESTful style, with appropriate resources
Following the JSON API standard where relevant: https://jsonapi.org/format/
"""
from flask import request, Blueprint, jsonify, make_response
from flask_restful import Resource, Api, marshal_with
from sqlalchemy.sql.functions import count
from sqlalchemy.orm import joinedload, contains_eager
import os
from flask_login import login_required, login_user, logout_user, current_user, login_manager
import json
from http import HTTPStatus
from numpy import mean, std, repeat, concatenate, flip

from megaqc.api.views import check_user, check_admin
from megaqc.model import models
import megaqc.user.models as user_models
from megaqc.extensions import db, restful
from megaqc import model
from megaqc.rest_api import schemas, filters, utils

api_bp = Blueprint('rest_api', __name__, url_prefix='/rest_api/v1')


class ReportList(Resource):
    def get(self, user_id=None):
        """
        Get a list of reports
        """
        query = db.session.query(
            models.Report,
        )
        if user_id is not None:
            query = query.filter(models.Report.user_id == user_id)

        return schemas.ReportSchema(many=True).dump(query.all())

    @check_user
    def post(self, user):
        """
        Upload a new report
        """
        file_name = utils.get_unique_filename()
        request.files['report'].save(file_name)
        upload_row = models.Upload.create(
            status="NOT TREATED",
            path=file_name,
            message="File has been created, loading in MegaQC is queued.",
            user_id=user.user_id
        )

        return schemas.UploadSchema(exclude=['path']).dump(upload_row)


class Report(Resource):
    def get(self, report_id):
        """
        Get data about this report
        """
        report_meta = db.session.query(
            models.Report,
        ).options(
            joinedload(models.Report.meta)
        ).filter(
            models.Report.report_id == report_id
        ).first()

        return schemas.ReportSchema(many=False).dump(report_meta)

    def put(self, report_id):
        """
        Update this report
        """
        raise NotImplementedError()

    @check_admin
    def delete(self, report_id, user):
        """
        Delete this report
        """
        db.session.query(models.Report).filter(models.Report.report_id == report_id).delete()
        db.session.commit()
        return {}


class ReportMeta(Resource):
    def get(self, report_id):
        """
        Get all data for a sample
        """
        # Here we need to prefetch the data and the data type because they will also be dumped to JSON
        meta = db.session.query(
            models.ReportMeta
        ).filter(
            models.ReportMeta.report_id == report_id
        ).all()

        return schemas.ReportMetaSchema(many=True).dump(meta)

    def post(self, report_id):
        return schemas.ReportMetaSchema(many=False).load(request.json)


class SamplesList(Resource):
    def get(self, report_id=None):
        """
        Get all samples for this report
        """

        # Only apply the report filter if we had a report ID
        filters = []
        if report_id is not None:
            filters.append([models.Sample.report_id == report_id])

        # Here we need to prefetch the data and the data type because they will also be dumped to JSON
        samples = db.session.query(
            models.Sample
        ).options(
            joinedload(models.Sample.data).joinedload(models.SampleData.data_type)
        ).filter(
            *filters
        ).all()

        return schemas.SampleSchema(many=True, exclude=['report']).dump(samples)

    def post(self, report_id):
        # Currently we only support uploading samples via a report
        raise NotImplementedError()


class Sample(Resource):
    def get(self, sample_id, report_id=None):
        """
        Get a single sample within a report
        """
        samples = db.session.query(
            models.Sample
        ).options(
            joinedload(models.Sample.data).joinedload(models.SampleData.data_type)
        ).filter(
            models.Sample.sample_id == sample_id
        ).first()

        return schemas.SampleSchema(many=False, exclude=['report']).dump(samples)

    def put(self, report_id, sample_id):
        """
        Update an existing sample
        """
        raise NotImplementedError()

    @check_admin
    def delete(self, sample_id, user, report_id=None):
        """
        Delete a single sample
        """
        db.session.query(
            models.Sample
        ).options(
            joinedload(models.Sample.data).joinedload(models.SampleData.data_type)
        ).filter(
            models.Sample.sample_id == sample_id
        ).delete()

        db.session.commit()

        return {}


class SampleData(Resource):
    def get(self, sample_id):
        """
        Get all data for a sample
        """
        # Here we need to prefetch the data and the data type because they will also be dumped to JSON
        samples = db.session.query(
            models.SampleData
        ).options(
            joinedload(models.SampleData.data_type)
        ).filter(
            models.SampleData.sample_id == sample_id
        ).all()

        return schemas.SampleDataSchema(many=True, exclude=['report']).dump(samples)

    def post(self, sample_id):
        return schemas.SampleDataSchema(many=False).load(request.json)


class UserList(Resource):
    @check_admin
    def get(self, user):
        """
        Get a list of users
        """
        users = db.session.query(
            user_models.User
        ).options(
            joinedload(user_models.User.roles)
        ).all()

        # Only admins can do this, so it doesn't matter if we return their password/key
        return schemas.UserSchema(many=True).dump(users)

    def post(self):
        """
        Create a new user
        """
        data = schemas.UserSchema(exclude=['reports', 'salt', 'api_token']).load(request.json, session=db.session)
        new_user = User(**data)
        new_user.set_password(data.password)
        new_user.active = True
        new_user.save()


class User(Resource):
    @check_admin
    def get(self, user_id, user):
        """
        Get a specific user
        """
        users = db.session.query(
            user_models.User
        ).options(
            joinedload(user_models.User.roles)
        ).filter(
            user_models.User.user_id == user_id
        ).first()

        return schemas.UserSchema(many=False).dump(users)

    def put(self, user_id):
        """
        Update a user
        """
        raise NotImplementedError()

    @check_admin
    def delete(self, user_id):
        """
        Delete a user
        """
        db.session.query(
            user_models.User
        ).filter(
            user_models.User.user_id == user_id
        ).delete()
        db.session.commit()

        return {}


class DashboardList(Resource):
    def get(self, user_id):
        pass

    def post(self, user_id):
        pass


class Dashboard(Resource):
    def get(self, user_id, dashboard_id):
        pass

    def put(self, user_id, dashboard_id):
        pass

    def delete(self, user_id, dashboard_id):
        pass


class FavouriteList(Resource):
    def get(self, user_id):
        pass

    def post(self, user_id):
        pass


class Favourite(Resource):
    def get(self, user_id, favourite_id):
        pass

    def put(self, user_id, favourite_id):
        pass

    def delete(self, user_id, favourite_id):
        pass


class FilterList(Resource):
    def get(self, user_id=None):
        query = db.session.query(
            models.SampleFilter
        ).join(
            user_models.User, user_models.User.user_id == models.SampleFilter.user_id
        ).options(
            # We're already joining to the users table in order to filter, so use this to load the relationship
            contains_eager(models.SampleFilter.user)
        )

        # If this is the filter list for a single user, filter it down to that
        if user_id is not None:
            query = query.filter(user_models.User.user_id == user_id)

        results = query.all()
        return schemas.SampleFilterSchema(many=True).dump(results)

    @check_user
    def post(self, user):
        load_schema = schemas.SampleFilterSchema(many=False, exclude=('user', 'id'))
        dump_schema = schemas.SampleFilterSchema(many=False)

        model = load_schema.load(request.json, session=db.session).data
        model.user_id = user.user_id
        db.session.add(model)
        db.session.commit()

        return dump_schema.dump(model)


class Filter(Resource):
    def get(self, filter_id, user_id=None):
        query = db.session.query(
            models.SampleFilter
        ).join(
            user_models.User, user_models.User.user_id == models.SampleFilter.user_id
        ).options(
            contains_eager(models.SampleFilter.user)
        ).filter(
            models.SampleFilter.sample_filter_id == filter_id
        )

        # If this is the filter list for a single user, filter it down to that
        if user_id is not None:
            query = query.filter(user_models.User.user_id == user_id)

        results = query.first_or_404()

        return schemas.SampleFilterSchema(many=False).dump(results)

    @check_user
    def put(self, filter_id, user, user_id=None):
        load_schema = schemas.SampleFilterSchema(many=False, exclude=('user', 'id'))

        # Validate the incoming json
        if request.json is None:
            return {'errors': errors}, HTTPStatus.BAD_REQUEST

        errors = load_schema.validate(request.json, session=db.session)
        if len(errors) > 0:
            return {'errors': errors}, HTTPStatus.BAD_REQUEST

        # Find an instance that meets the user_id and filter_id constraints
        query = db.session.query(
            models.SampleFilter
        ).join(
            user_models.User, user_models.User.user_id == models.SampleFilter.user_id
        ).options(
            contains_eager(models.SampleFilter.user)
        ).filter(
            models.SampleFilter.sample_filter_id == filter_id
        )
        if user_id is not None:
            query = query.filter(user_models.User.user_id == user_id)
        curr_instance = query.first_or_404()

        # Check permissions
        if not (user.is_admin or curr_instance.user_id == user.user_id):
            return '', HTTPStatus.UNAUTHORIZED

        # Update the instance
        new_instance = load_schema.load(request.json, session=db.session, instance=curr_instance).data
        db.session.add(model)
        db.session.commit()

        # Dump the new instance as the response
        dump_schema = schemas.SampleFilterSchema(many=False)
        return dump_schema.dump(new_instance)

    def delete(self, filter_id):
        query = db.session.query(
            models.SampleFilter
        ).join(
            user_models.User, user_models.User.user_id == models.SampleFilter.user_id
        ).options(
            contains_eager(models.SampleFilter.user)
        ).filter(
            models.SampleFilter.sample_filter_id == filter_id
        )

        instance = query.first_or_404()

        db.session.delete(instance)

        return {}


class TrendSeries(Resource):
    def get(self):
        filter = json.loads(request.args.get('filter', '[]'))
        fields = json.loads(request.args['fields'])

        query = filters.build_filter_query(filter)
        plots = []
        for field in fields:

            # Choose the columns to select, and further filter it down to samples with the column we want to plot
            query = query.with_entities(
                models.Report.created_at,
                models.SampleData.value
            ).filter(
                models.SampleDataType.data_key == field
            ).order_by(
                models.Report.created_at.asc(),
            )
            data = query.all()

            # If the query returned nothing, skip this field
            if len(data) == 0:
                break

            x, y = zip(*data)
            y = [float(num) for num in y]

            # Add the raw data
            plots.append(dict(
                type='scatter',
                x=x,
                y=y,
                line=dict(color='rgb(0,100,80)'),
                mode='markers',
                name=field,
            ))

            # Add the mean
            y2 = repeat(mean(y), len(x))
            plots.append(dict(
                type='scatter',
                x=x,
                y=y2.tolist(),
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
            plots.append(dict(
                type='scatter',
                x=x3.tolist(),
                y=y3.tolist(),
                fill='tozerox',
                fillcolor='rgba(0,100,80,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=False,
            ))

        return jsonify(plots)


# @restful.representation('application/json')
# def return_json(data, code, headers=None):
#     """
#     Massage the response into a json:api compatible format: https://jsonapi.org/format/
#     """
#     if code == HTTPStatus.OK:
#         ret = {'data': data}
#     else:
#         ret = {'errors': data}
#
#     resp = make_response(json.dumps(ret), code)
#     resp.headers.extend(headers or {})
#     return resp

restful.add_resource(ReportList, '/reports', '/users/<int:user_id>/reports')
restful.add_resource(Report, '/reports/<int:report_id>')
restful.add_resource(ReportMeta, '/reports/<int:report_id>/meta')

restful.add_resource(SamplesList, '/reports/<int:report_id>/samples', '/samples')
restful.add_resource(Sample, '/samples/<int:sample_id>')
restful.add_resource(SampleData, '/samples/<int:sample_id>/data')

restful.add_resource(UserList, '/users')
restful.add_resource(User, '/users/<int:user_id>')

restful.add_resource(TrendSeries, '/plots/trends/series', endpoint='trend_data')

restful.add_resource(FilterList, '/filters', '/users/<int:user_id>/filters')
restful.add_resource(Filter, '/filters/<int:filter_id>')

restful.init_app(api_bp)
