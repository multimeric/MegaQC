import graphene
from flask import Blueprint
from flask_graphql import GraphQLView
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

from megaqc.model import models
from megaqc.graphql import filters

graphql_bp = Blueprint('graphql', __name__, url_prefix='/graphql')


class Report(SQLAlchemyObjectType):
    class Meta:
        model = models.Report
        interfaces = (relay.Node,)


class ReportMeta(SQLAlchemyObjectType):
    class Meta:
        model = models.ReportMeta
        interfaces = (relay.Node,)


class PlotConfig(SQLAlchemyObjectType):
    class Meta:
        model = models.PlotConfig
        interfaces = (relay.Node,)


class PlotData(SQLAlchemyObjectType):
    class Meta:
        model = models.PlotData
        interfaces = (relay.Node,)


class PlotCategory(SQLAlchemyObjectType):
    class Meta:
        model = models.PlotCategory
        interfaces = (relay.Node,)


class PlotFavourite(SQLAlchemyObjectType):
    class Meta:
        model = models.PlotFavourite
        interfaces = (relay.Node,)


class Dashboard(SQLAlchemyObjectType):
    class Meta:
        model = models.Dashboard
        interfaces = (relay.Node,)


class SampleDataType(SQLAlchemyObjectType):
    class Meta:
        model = models.SampleDataType
        interfaces = (relay.Node,)


class SampleData(SQLAlchemyObjectType):
    class Meta:
        model = models.SampleData
        interfaces = (relay.Node,)


class Sample(SQLAlchemyObjectType):
    filter = graphene.JSONString(default_value=[], required=False)

    class Meta:
        model = models.Sample
        interfaces = (relay.Node,)


class SampleFilter(SQLAlchemyObjectType):
    class Meta:
        model = models.SampleFilter
        interfaces = (relay.Node,)


class Upload(SQLAlchemyObjectType):
    class Meta:
        model = models.Upload
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    def resolve_all_samples(parent, info, filter=[], **kwargs):
        query = filters.build_filter_query(filter)
        return query.all()
        # print(info)
        # return super().resolve_samples(info, **kwargs)

    node = relay.Node.Field()

    all_reports = SQLAlchemyConnectionField(Report)
    report = relay.Node.Field(Report)

    all_report_meta = SQLAlchemyConnectionField(ReportMeta)
    report_meta = relay.Node.Field(ReportMeta)

    all_plot_config = SQLAlchemyConnectionField(PlotConfig)
    plot_config = relay.Node.Field(PlotConfig)

    all_plot_data = SQLAlchemyConnectionField(PlotData)
    plot_data = relay.Node.Field(PlotData)

    all_plot_categories = SQLAlchemyConnectionField(PlotCategory)
    plot_category = relay.Node.Field(PlotCategory)

    all_plot_favourites = SQLAlchemyConnectionField(PlotFavourite)
    plot_favourite = relay.Node.Field(PlotFavourite)

    all_dashboards = SQLAlchemyConnectionField(Dashboard)
    dashboard = relay.Node.Field(Dashboard)

    all_sample_data_types = SQLAlchemyConnectionField(SampleDataType)
    sample_data_type = relay.Node.Field(SampleDataType)

    all_sample_datas = SQLAlchemyConnectionField(SampleData)
    sample_data = relay.Node.Field(SampleData)

    all_samples = SQLAlchemyConnectionField(Sample)
    sample = relay.Node.Field(Sample)

    all_sample_filters = SQLAlchemyConnectionField(SampleFilter)
    sample_filter = relay.Node.Field(SampleFilter)

    all_uploads = SQLAlchemyConnectionField(Upload)
    upload = relay.Node.Field(Upload)


schema = graphene.Schema(query=Query, types=[
    Report,
    ReportMeta,
    PlotConfig,
    PlotData,
    PlotCategory,
    PlotFavourite,
    Dashboard,
    SampleDataType,
    SampleData,
    Sample,
    SampleFilter,
    Upload
])
graphql_bp.add_url_rule(
    "", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True)
)
