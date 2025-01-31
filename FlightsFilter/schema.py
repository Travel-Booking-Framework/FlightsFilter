import graphene
from FFilter.schema import FlightsQuery


class Query(FlightsQuery, graphene.ObjectType):
    pass


class Mutation(graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
