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
from marshmallow import fields
from marshmallow.schema import SchemaMeta
from marshmallow.utils import missing
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from megaqc.model.models import *
from megaqc.user.models import *
from megaqc.extensions import ma
from megaqc.rest_api.fields import JsonString


class NestedSessionMixin:

    @marshmallow.pre_load
    def set_nested_session(self, data):
        """Allow nested schemas to use the parent schema's session. This is a
        longstanding bug with marshmallow-sqlalchemy.

        https://github.com/marshmallow-code/marshmallow-sqlalchemy/issues/67
        https://github.com/marshmallow-code/marshmallow/issues/658#issuecomment-328369199
        """
        nested_fields = {k: v for k, v in self.fields.items() if type(v) == marshmallow.fields.Nested}
        for field in nested_fields.values():
            field.schema.session = self.session


class SelfNested(fields.Nested):
    def get_value(self, obj, attr, accessor=None, default=missing):
        """
        Normally we'd want to access obj[attr], but since we're actually just dumping a subsection of the parent,
        this isn't needed
        """
        return obj


# class SampleDataTypeSchema(Schema):
#     id = fields.Integer()
#     section = fields.String()
#     key = fields.String()

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

    id = fields.Integer(attribute='sample_data_id')
    key = ma.Method('type_key')
    section = ma.Method('type_section')
    value = fields.String()
    # sample = Relationship(
    #     related_view='rest_api.sample',
    #     related_view_kwargs={
    #         'sample_id': '<sample_id>'
    #     },
    #     many=False,
    #     type_='sample'
    # )

    def type_key(self, obj):
        return obj.data_type.data_key

    def type_section(self, obj):
        return obj.data_type.data_section


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

    id = fields.Integer(attribute='sample_id')
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
class SampleFilterSchema(Schema):
    class Meta:
        type_ = "sample_filter"
        self_view = 'rest_api.sample'
        self_view_kwargs = {
            'sample_id': '<id>'
        }

    id = fields.Integer(attribute='sample_filter_id')
    tag = fields.String(attribute='sample_filter_tag')
    name = fields.String(attribute='sample_filter_name')
    public = fields.Boolean(attribute='is_public')
    data = JsonString(attribute='sample_filter_data')

    user = Relationship(
        related_view='rest_api.user',
        related_view_kwargs={
            'user_id': '<user.id>'
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

    id = fields.Integer(attribute='report_id')
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


class ReportMetaSchema(Schema):
    class Meta:
        type_ = 'report_meta'
        # self_view = 'rest_api.reportmeta'
        # self_view_kwargs = {
        #     'report_id': '<id>'
        # }

    id = fields.Integer(attribute='report_meta_id')
    key = fields.String(attribute='report_meta_key')
    value = fields.String(attribute='report_meta_value')


class UserSchema(Schema):
    class Meta:
        type_ = "user"
        self_view = 'rest_api.user'
        self_view_kwargs = {
            'user_id': '<id>'
        }

    id = fields.Integer(attribute='user_id')
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
        type_='report'
    )
    # roles = fields.Function(lambda obj: [role.name for role in obj.roles])
    # filters = fields.List(ma.HyperlinkRelated('rest_api.filter', url_key='filter_id'))
    # reports = fields.List(ma.HyperlinkRelated('rest_api.report', url_key='report_id'))
    #
    # class Meta:
    #     model = User
    #     exclude = ('is_admin', 'user_id')
