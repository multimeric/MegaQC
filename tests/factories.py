# -*- coding: utf-8 -*-
"""Factories to help in tests."""
from factory import PostGenerationMethodCall, Sequence, Faker, SubFactory
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

    username = Sequence(lambda n: 'user{0}'.format(n))
    email = Sequence(lambda n: 'user{0}@example.com'.format(n))
    password = PostGenerationMethodCall('set_password', 'example')
    active = True

    class Meta:
        """Factory configuration."""

        model = User

class ReportMetaFactory(BaseFactory):
    report_meta_id = Faker('pyint')
    report_meta_key = Faker('word')
    report_meta_value = Faker('pystr')

class ReportFactory(BaseFactory):
    class Meta:
        model = models.Report

    report_id = Faker('pyint')
    report_hash = Faker('sha1')
    created_at = Faker('date_time')
    uploaded_at = Faker('date_time')

    user = SubFactory(UserFactory)
    report_meta = SubFactory(ReportMetaFactory)
