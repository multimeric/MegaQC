# -*- coding: utf-8 -*-
"""Factories to help in tests."""
from factory import PostGenerationMethodCall, Sequence, Faker, SubFactory, RelatedFactory, RelatedFactoryList, \
    SelfAttribute
from factory.alchemy import SQLAlchemyModelFactory

from megaqc.database import db
from megaqc.model import models
from megaqc.user.models import User


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session


class UserFactory(BaseFactory):
    """User factory."""

    username = Faker('user_name')
    email = Faker('ascii_email')
    password = PostGenerationMethodCall('set_password', 'example')
    active = True
    first_name = Faker('first_name')
    last_name = Faker('last_name')

    class Meta:
        """Factory configuration."""

        model = User


class ReportMetaFactory(BaseFactory):
    class Meta:
        model = models.ReportMeta

    report_meta_key = Faker('word')
    report_meta_value = Faker('pystr')


class ReportFactory(BaseFactory):
    class Meta:
        model = models.Report

    report_hash = Faker('sha1')
    created_at = Faker('date_time')
    uploaded_at = Faker('date_time')

    user = SubFactory(UserFactory)
    meta = RelatedFactoryList(ReportMetaFactory, 'report', size=3)
    samples = RelatedFactoryList('tests.factories.SampleFactory', 'report', size=3)


class SampleFactory(BaseFactory):
    class Meta:
        model = models.Sample

    sample_name = Faker('word')

    report = SubFactory(ReportFactory, samples=[])
    data = RelatedFactoryList('tests.factories.SampleDataFactory', 'sample')


class SampleDataTypeFactory(BaseFactory):
    class Meta:
        model = models.SampleDataType

    data_section = Faker('word')
    data_key = Faker('word')


class SampleDataFactory(BaseFactory):
    class Meta:
        model = models.SampleData

    value = Faker('pyint')

    # sample = SubFactory(SampleFactory)
    data_type = SubFactory(SampleDataTypeFactory)
