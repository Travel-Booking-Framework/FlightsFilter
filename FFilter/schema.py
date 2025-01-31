# schema.py
import graphene
from graphene import ObjectType
from graphene_django.types import DjangoObjectType
from elasticsearch_dsl import Search
from django_elasticsearch_dsl.search import Search as ElasticsearchSearch
from elasticsearch import Elasticsearch
from datetime import datetime


# GraphQL ObjectTypes for related models
class AircraftType(graphene.ObjectType):
    aircraft_model = graphene.String()
    aircraft_capacity = graphene.Int()
    aircraft_manufacturer = graphene.String()


class AirlineType(graphene.ObjectType):
    airline_name = graphene.String()
    airline_code = graphene.String()


class AirportType(graphene.ObjectType):
    airport_name = graphene.String()
    airport_code = graphene.String()
    airport_city = graphene.String()


# GraphQL ObjectType for Flight with necessary fields
class FlightType(graphene.ObjectType):
    flight_number = graphene.String()
    flight_type = graphene.String()
    trip_type = graphene.String()
    departure_datetime = graphene.String()
    departure_time = graphene.String()  # Extracting only time (HH:MM)
    arrival_datetime = graphene.String()
    final_price = graphene.BigInt()
    base_price = graphene.BigInt()
    tax = graphene.Decimal()
    discount = graphene.Decimal()
    departure_airport = graphene.Field(AirportType)
    arrival_airport = graphene.Field(AirportType)
    airline = graphene.Field(AirlineType)
    aircraft = graphene.Field(AircraftType)
    baggage_limit_kg = graphene.Float()
    cabin_type = graphene.String()


# Base Filter Strategy
class FilterStrategy:
    def apply_filter(self, search, value):
        pass


# Strategy for applying dynamic filters based on parameters
class DepartureAirportFilter(FilterStrategy):
    def apply_filter(self, search, value):
        return search.filter('term', departure_airport__airport_code=value)


class ArrivalAirportFilter(FilterStrategy):
    def apply_filter(self, search, value):
        return search.filter('term', arrival_airport__airport_code=value)


class DepartureDateFilter(FilterStrategy):
    def apply_filter(self, search, value):
        return search.filter('term', departure_datetime=value)


class AircraftCapacityFilter(FilterStrategy):
    def apply_filter(self, search, value):
        return search.filter('term', aircraft__aircraft_capacity=value)


class CabinTypeFilter(FilterStrategy):
    def apply_filter(self, data, value):
        return [f for f in data if f.cabin_type == value]


class AirlineFilter(FilterStrategy):
    def apply_filter(self, data, value):
        return [f for f in data if f.airline.airline_name == value]


class BaggageLimitFilter(FilterStrategy):
    def apply_filter(self, data, value):
        return [f for f in data if f.baggage_limit_kg == value]


class DepartureTimeFilter(FilterStrategy):
    def apply_filter(self, data, value):
        return [f for f in data if f.departure_time == value]


# Advanced Filters for Step 2
class PriceFilter:
    def apply_filter(self, flights, min_price=None, max_price=None):
        if min_price:
            flights = [f for f in flights if f.final_price >= min_price]
        if max_price:
            flights = [f for f in flights if f.final_price <= max_price]
        return flights


class FastestFlightFilter:
    def apply_filter(self, flights):
        return min(flights, key=lambda f: (f.arrival_datetime - f.departure_datetime))


class EarliestFlightFilter:
    def apply_filter(self, flights):
        return min(flights, key=lambda f: f.departure_datetime)


class LatestFlightFilter:
    def apply_filter(self, flights):
        return max(flights, key=lambda f: f.departure_datetime)


# Main GraphQL Query
class FlightsQuery(ObjectType):
    flights = graphene.List(
        FlightType,
        departure_airport=graphene.String(),
        arrival_airport=graphene.String(),
        departure_date=graphene.String(),
        aircraft_capacity=graphene.Int(),
        min_price=graphene.Float(),
        max_price=graphene.Float(),
        baggage_limit=graphene.Float(),
        airline_name=graphene.String(),
        departure_time=graphene.String(),
        filter_by=graphene.String()
    )

    def resolve_flights(self, info, departure_airport=None, arrival_airport=None, departure_date=None,
                         aircraft_capacity=None, min_price=None, max_price=None, baggage_limit=None,
                         airline_name=None, departure_time=None, filter_by=None):
        client = Elasticsearch()
        search = ElasticsearchSearch(using=client, index="flights")

        # Filter Map for base filters (from Strategy Pattern)
        filter_map = {
            'departure_airport': DepartureAirportFilter(),
            'arrival_airport': ArrivalAirportFilter(),
            'departure_date': DepartureDateFilter(),
            'aircraft_capacity': AircraftCapacityFilter(),
            'cabin_type': CabinTypeFilter()
        }

        # Apply dynamic base filters
        for field, value in locals().items():
            if value and field in filter_map:
                search = filter_map[field].apply_filter(search, value)

        # Execute the search query
        response = search.execute()

        # Collect the results into a list of FlightType objects
        flights = [
            FlightType(
                flight_number=hit.flight_number,
                flight_type=hit.flight_type,
                trip_type=hit.trip_type,
                departure_datetime=hit.departure_datetime,
                departure_time=hit.departure_datetime.split("T")[1],  # Extracting only time HH:MM
                arrival_datetime=hit.arrival_datetime,
                final_price=hit.final_price,
                departure_airport=AirportType(
                    airport_name=hit.departure_airport['airport_name'],
                    airport_code=hit.departure_airport['airport_code'],
                    airport_city=hit.departure_airport['airport_city']
                ),
                arrival_airport=AirportType(
                    airport_name=hit.arrival_airport['airport_name'],
                    airport_code=hit.arrival_airport['airport_code'],
                    airport_city=hit.arrival_airport['airport_city']
                ),
                airline=AirlineType(
                    airline_name=hit.airline['airline_name'],
                    airline_code=hit.airline['airline_code']
                ),
                aircraft=AircraftType(
                    aircraft_model=hit.aircraft['aircraft_model'],
                    aircraft_capacity=hit.aircraft['aircraft_capacity'],
                    aircraft_manufacturer=hit.aircraft['aircraft_manufacturer']
                ),
                baggage_limit_kg=hit.baggage_limit_kg,
                cabin_type=hit.cabin_type
            )
            for hit in response
        ]

        # Extract lists for filtering in step 2
        airline_names = list(set([flight.airline.airline_name for flight in flights]))
        baggage_limits = list(set([flight.baggage_limit_kg for flight in flights]))
        cabin_types = list(set([flight.cabin_type for flight in flights]))
        departure_times = list(set([flight.departure_time for flight in flights]))

        # Apply dynamic price filter
        price_filter = PriceFilter()
        flights = price_filter.apply_filter(flights, min_price, max_price)

        # Apply dynamic filters for baggage_limit, airline_name, and departure_time
        flights = BaggageLimitFilter().apply_filter(flights, baggage_limit) if baggage_limit else flights
        flights = AirlineFilter().apply_filter(flights, airline_name) if airline_name else flights
        flights = DepartureTimeFilter().apply_filter(flights, departure_time) if departure_time else flights

        # Apply dynamic filters for fastest, earliest, or latest flights
        advanced_filters_map = {
            "fastest": FastestFlightFilter(),
            "earliest": EarliestFlightFilter(),
            "latest": LatestFlightFilter()
        }

        if filter_by in advanced_filters_map:
            flights = advanced_filters_map[filter_by].apply_filter(flights)

        # Returning the filtered flights along with the extracted lists
        return {
            "flights": flights,
            "airline_names": airline_names,
            "baggage_limits": baggage_limits,
            "cabin_types": cabin_types,
            "departure_times": departure_times
        }


