import graphene
from flask import Blueprint
from flask_graphql import GraphQLView
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

from megaqc.model import models

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
    node = relay.Node.Field()

    all_reports = SQLAlchemyConnectionField(Report)
    report = relay.Node.Field(Report)


schema = graphene.Schema(query=Query, types=[Report])
graphql_bp.add_url_rule(
    "", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True)
)
