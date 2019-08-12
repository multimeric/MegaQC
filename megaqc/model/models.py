# -*- coding: utf-8 -*-
import datetime as dt

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, ForeignKey, Column, Boolean, Integer, Float, Unicode, TIMESTAMP, Binary, DateTime, func

from megaqc.database import CRUDMixin
from megaqc.extensions import db


user_plotconfig_map = db.Table('user_plotconfig_map',
            db.Column('user_id', Integer, db.ForeignKey('users.user_id')),
            db.Column('plot_config_id', Integer, db.ForeignKey('plot_config.config_id'))
            )

user_sampletype_map = db.Table('user_sampletype_map',
            db.Column('user_id', Integer, db.ForeignKey('users.user_id')),
            db.Column('sample_data_type_id', Integer, db.ForeignKey('sample_data_type.sample_data_type_id'))
            )


class Report(db.Model, CRUDMixin):
    """a MultiQC report"""

    __tablename__ = 'report'
    report_id = Column(Integer, primary_key=True)
    # If the user is deleted, we still want to retain the report
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='SET NULL'), index=True)
    report_hash = Column(Unicode, index=True, unique=True)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    uploaded_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)

    user = relationship('User', back_populates='reports')
    report_meta = relationship('ReportMeta', back_populates='report')
    samples = relationship('Sample', back_populates='report')

    def __init__(self, **kwargs):
        """Create instance."""
        db.Model.__init__(self, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Report({rid!r})>'.format(rid=self.report_id)


class ReportMeta(db.Model, CRUDMixin):
    __tablename__ = 'report_meta'
    report_meta_id = Column(Integer, primary_key=True)
    report_meta_key = Column(Unicode, nullable=False)
    report_meta_value = Column(Unicode, nullable=False)
    # If the report is deleted, remove the report metadata
    report_id = Column(Integer, ForeignKey('report.report_id', ondelete='CASCADE'), index=True)

    report = relationship('Report', back_populates='report_meta')


class PlotConfig(db.Model, CRUDMixin):
    __tablename__ = 'plot_config'
    config_id = Column(Integer, primary_key=True)
    config_type = Column(Unicode,  nullable=False)
    config_name = Column(Unicode, nullable=False)
    config_dataset = Column(Unicode, nullable=True)
    data = Column(Unicode, nullable=False)

    fav_users = db.relationship('User', secondary=user_plotconfig_map, backref="favourite_plotconfigs")


class PlotData(db.Model, CRUDMixin):
    __tablename__ = "plot_data"
    plot_data_id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('report.report_id'), index=True)
    config_id = Column(Integer, ForeignKey('plot_config.config_id'))
    plot_category_id = Column(Integer(), ForeignKey('plot_category.plot_category_id'))
    sample_id = Column(Integer, ForeignKey('sample.sample_id'), index=True)
    data = Column(Unicode, nullable=False)


class PlotCategory(db.Model, CRUDMixin):
    __tablename__ = "plot_category"
    plot_category_id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('report.report_id'))
    config_id = Column(Integer, ForeignKey('plot_config.config_id'))
    category_name = Column(Unicode, nullable=True)
    data = Column(Unicode, nullable=False)


class PlotFavourite(db.Model, CRUDMixin):
    __tablename__ = "plot_favourite"
    plot_favourite_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), index=True)
    title = Column(Unicode, nullable=False)
    description = Column(Unicode, nullable=True)
    plot_type = Column(Unicode, nullable=False)
    data = Column(Unicode, nullable=False)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)


class Dashboard(db.Model, CRUDMixin):
    __tablename__ = "dashboard"
    dashboard_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), index=True)
    title = Column(Unicode, nullable=False)
    data = Column(Unicode, nullable=False)
    is_public = Column(Boolean, default=False, index=True)
    modified_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)


class SampleDataType(db.Model, CRUDMixin):
    __tablename__ = "sample_data_type"
    sample_data_type_id = Column(Integer, primary_key=True)
    data_id = Column(Unicode)
    data_section = Column(Unicode)
    data_key = Column(Unicode, nullable=False)

    sample_data = relationship('SampleData', back_populates='data_type')

class SampleData(db.Model, CRUDMixin):
    __tablename__ = "sample_data"
    sample_data_id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('report.report_id'), index=True)
    sample_data_type_id = Column(Integer, ForeignKey('sample_data_type.sample_data_type_id'))
    sample_id = Column(Integer, ForeignKey('sample.sample_id', ondelete='CASCADE'), index=True)
    value = Column(Unicode)

    sample = relationship('Sample', back_populates='data')
    data_type = relationship('SampleDataType', back_populates='sample_data')


class Sample(db.Model, CRUDMixin):
    __tablename__ = "sample"
    sample_id = Column(Integer, primary_key=True)
    sample_name = Column(Unicode)
    report_id = Column(Integer, ForeignKey('report.report_id', ondelete='CASCADE'), index=True)

    report = relationship('Report', back_populates='samples')
    data = relationship('SampleData', back_populates='sample')


class SampleFilter(db.Model, CRUDMixin):
    __tablename__ = "sample_filter"
    sample_filter_id = Column(Integer, primary_key=True)
    sample_filter_name = Column(Unicode)
    sample_filter_tag = Column(Unicode)
    is_public = Column(Boolean, index=True)
    sample_filter_data = Column(Unicode, nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), index=True)


class Upload(db.Model, CRUDMixin):
    __tablename__ = "uploads"
    upload_id = Column(Integer, primary_key=True)
    status = Column(Unicode, index=True)
    path = Column(Unicode)
    message = Column(Unicode)
    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    modified_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.user_id'))
