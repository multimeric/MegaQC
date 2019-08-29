"""
These schemas describe the format of the web requests to and from the API. They incidentally share most fields with the
database models, but they can be opinionated about REST-specific fields
"""
from marshmallow_sqlalchemy import ModelSchema
from flask_restful import url_for
from sqlalchemy.orm.collections import InstrumentedList
import json
from six import with_metaclass
import marshmallow
from marshmallow import fields, post_load
from marshmallow.schema import SchemaMeta
from marshmallow.utils import missing
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema as JsonApiSchema

from megaqc.model.models import *
from megaqc.user.models import *
from megaqc.extensions import ma
from megaqc.rest_api.fields import JsonString


class OptionalLinkSchema(JsonApiSchema):
    def __init__(self, use_links=True, *args, **kwargs):
        self.use_links = use_links
        super().__init__(*args, **kwargs)

    def get_resource_links(self, item):
        if not self.use_links:
            return None
        return super().get_resource_links(item)

    @post_load()
    def remove_empty_id(self, item, **kwargs):
        """
        Hack to deal with empty ID field that has to be sent
        """
        id_field = self.fields['id'].attribute
        if id_field in item and item[id_field] is None:
            del item[id_field]

        return item

# Make every schema use this
Schema = OptionalLinkSchema


class SampleDataSchema(Schema):
    """
    This is an abstraction of SampleData + SampleDataType into one object
    """

    class Meta:
        type_ = 'sample_data'
        # self_view = 'rest_api.sampledata'
        # self_view_many = 'rest_api.sampledata'
        # self_view_kwargs = {
        #     'sample_id': '<sample_id>'
        # }

    id = fields.String(attribute='sample_data_id', allow_none=True)
    key = fields.String(attribute='data_type.data_key')
    section = ma.String(attribute='data_type.data_section')
    value = fields.String()

    # We can't link to the parent sample because of
    # https://github.com/marshmallow-code/marshmallow-jsonapi/issues/247

    # sample = Relationship(
    #     related_view='rest_api.sample',
    #     related_view_kwargs={
    #         'sample_id': '<sample_id>'
    #     },
    #     many=False,
    #     type_='sample'
    # )


class SampleSchema(Schema):
    """
    This is an abstraction of Sample + SampleData + SampleDataType into one object
    """

    class Meta:
        type_ = 'sample'
        self_view = 'rest_api.sample'
        self_view_many = 'rest_api.sampleslist'
        self_view_kwargs = {
            'sample_id': '<id>'
        }

    id = fields.String(attribute='sample_id', allow_none=True)
    name = fields.String(attribute='sample_name')
    data = Relationship(
        related_view='rest_api.sampledata',
        related_view_kwargs={
            'sample_id': '<sample_id>'
        },
        # include_resource_linkage=True,
        many=True,
        type_='sample_data',
        schema="SampleDataSchema"
    )


# By using this metaclass, we stop all the default fields being copied into the schema, allowing us to rename them
class SampleFilterSchema(OptionalLinkSchema):
    class Meta:
        type_ = "sample_filter"
        self_view = 'rest_api.filter'
        self_view_many = 'rest_api.filterlist'
        self_view_kwargs = {
            'filter_id': '<id>'
        }

    id = fields.String(attribute='sample_filter_id', allow_none=True)
    tag = fields.String(attribute='sample_filter_tag')
    name = fields.String(attribute='sample_filter_name')
    public = fields.Boolean(attribute='is_public')
    data = JsonString(attribute='sample_filter_data')

    user = Relationship(
        related_view='rest_api.user',
        related_view_kwargs={
            'user_id': '<user_id>'
        }
    )


class ReportSchema(Schema):
    """
    This is an abstraction of Report + ReportMeta
    """

    class Meta:
        type_ = 'report'
        self_view = 'rest_api.report'
        self_view_many = 'rest_api.reportlist'
        self_view_kwargs = {
            'report_id': '<id>'
        }
        strict = True

    id = fields.String(attribute='report_id', allow_none=True)
    hash = fields.String(attribute='report_hash')
    created_at = fields.DateTime()
    uploaded_at = fields.DateTime()

    meta = Relationship(
        related_view='rest_api.reportmeta',
        related_view_kwargs={
            'report_id': '<report_id>'
        },
        many=True,
        type_='report_meta'
    )

    samples = Relationship(
        related_view='rest_api.sampleslist',
        related_view_kwargs={
            'report_id': '<report_id>'
        },
        many=True,
        type_='sample'
    )

    user = Relationship(
        related_view='rest_api.user',
        related_view_kwargs={
            'user_id': '<user_id>'
        },
        many=False,
        type_='user'
    )


class UploadSchema(Schema):
    class Meta:
        type_ = 'upload'
        self_view = 'rest_api.upload'
        self_view_many = 'rest_api.uploadlist'
        self_view_kwargs = {
            'upload_id': '<id>'
        }
        strict = True

    id = fields.String(attribute='upload_id', allow_none=True)
    status = fields.String()
    path = fields.String()
    message = fields.String()
    created_at = fields.DateTime()
    modified_at = fields.DateTime()

    user = Relationship(
        related_view='rest_api.user',
        related_view_kwargs={
            'user_id': '<user_id>'
        },
        many=False,
        type_='user',
        id_field='user_id'
    )


class ReportMetaSchema(Schema):
    class Meta:
        type_ = 'report_meta'
        # self_view = 'rest_api.reportmeta'
        # self_view_kwargs = {
        #     'report_id': '<id>'
        # }

    id = fields.String(attribute='report_meta_id', allow_none=True)
    key = fields.String(attribute='report_meta_key')
    value = fields.String(attribute='report_meta_value')


class UserSchema(Schema):
    class Meta:
        type_ = "user"
        self_view = 'rest_api.user'
        self_view_kwargs = {
            'user_id': '<id>'
        }

    id = fields.String(attribute='user_id', required=False, allow_none=True)
    username = fields.String()
    email = fields.String()
    salt = fields.String()
    password = fields.String()
    created_at = fields.DateTime()
    first_name = fields.String()
    last_name = fields.String()
    active = fields.Boolean()
    admin = fields.Boolean(attribute='is_admin')
    api_token = fields.String()

    reports = Relationship(
        related_view='rest_api.reportlist',
        related_view_kwargs={
            'user_id': '<user_id>'
        },
        many=True,
        type_='report',
        required=False
    )


class PlotSchema(Schema):
    class Meta:
        type_ = 'plot'

    id = fields.Constant(-1, dump_only=True, allow_none=True)
    type = fields.String()
    x = fields.List(fields.Raw())
    y = fields.List(fields.Raw())
    line = fields.Dict()
    mode = fields.String()
    name = fields.String()

    # @post_load(pass_many=True)
    # def remove_id(self, data, many, **kwargs):
    #     for datum in data:
    #         del datum['id']
    #     return data

    # roles = fields.Function(lambda obj: [role.name for role in obj.roles])
    # filters = fields.List(ma.HyperlinkRelated('rest_api.filter', url_key='filter_id'))
    # reports = fields.List(ma.HyperlinkRelated('rest_api.report', url_key='report_id'))
    #
    # class Meta:
    #     model = User
    #     exclude = ('is_admin', 'user_id')


class TrendSchema(PlotSchema):
    x = fields.List(fields.DateTime())
    y = fields.List(fields.Number())
