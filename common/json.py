from json import JSONEncoder
from datetime import datetime
from django.db.models import QuerySet


class DateEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        else:
            return super().default(o)


class QuerySetEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, QuerySet):
            return list(o)
        else:
            return super().default(o)


class ModelEncoder(QuerySetEncoder, DateEncoder, JSONEncoder):
    def default(self, o):
        """
        #   if the object to decode is the same class as what's in the
        #   model property, then
        #     * create an empty dictionary that will hold the property names
        #       as keys and the property values as values
        #     * for each name in the properties list
        #         * get the value of that property from the model instance
        #           given just the property name
        #         * put it into the dictionary with that property name as
        #           the key
        #     * return the dictionary
        #   otherwise,
        #       return super().default(o)  # From the documentation
        """
        if isinstance(o, self.model):
            dict = {}
            if hasattr(o, "get_api_url"):
                dict["href"] = o.get_api_url()
            for property in self.properties:
                value = getattr(o, property)
                dict[property] = value

            return dict
        else:
            return super().default(o)

