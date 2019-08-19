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


class SubFactoryList(SubFactory):
    """Calls a factory 'size' times before the object has been generated.

    Attributes:
        factory (Factory): the factory to call "size-times"
        defaults (dict): extra declarations for calling the related factory
        factory_related_name (str): the name to use to refer to the generated
            object when calling the related factory
        size (int|lambda): the number of times 'factory' is called, ultimately
            returning a list of 'factory' objects w/ size 'size'.
    """

    def __init__(self, factory, size=2, **defaults):
        self.size = size
        super(SubFactoryList, self).__init__(factory, **defaults)

    def generate(self, *args, **kwargs):
        return [
            super(SubFactoryList, self).generate(*args, **kwargs)
            for i in range(self.size if isinstance(self.size, int) else self.size())
        ]


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

    report_meta_id = Faker('pyint')
    report_meta_key = Faker('word')
    report_meta_value = Faker('pystr')


class ReportFactory(BaseFactory):
    class Meta:
        model = models.Report

    # report_id = Faker('pyint')
    report_hash = Faker('sha1')
    created_at = Faker('date_time')
    uploaded_at = Faker('date_time')

    # user = SubFactory(UserFactory)
    meta = RelatedFactoryList(ReportMetaFactory, 'report', size=3)
    samples = RelatedFactoryList('tests.factories.SampleFactory', 'report', size=3)


class SampleFactory(BaseFactory):
    class Meta:
        model = models.Sample

    # sample_id = Faker('pyint')
    sample_name = Faker('word')

    report = SubFactory(ReportFactory, samples=[])
    data = RelatedFactoryList('tests.factories.SampleDataFactory', 'sample')


class SampleDataTypeFactory(BaseFactory):
    class Meta:
        model = models.SampleDataType

    sample_data_type_id = Faker('pyint')
    data_section = Faker('word')
    data_key = Faker('word')


class SampleDataFactory(BaseFactory):
    class Meta:
        model = models.SampleData

    sample_data_id = Faker('pyint')
    value = Faker('pyint')

    # sample = SubFactory(SampleFactory)
    data_type = SubFactory(SampleDataTypeFactory)
