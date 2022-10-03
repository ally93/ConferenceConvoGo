from json import JSONEncoder
from datetime import datetime
from django.db.models import QuerySet


class DateEncoder(JSONEncoder):
    def default(self, o):
        # if o is an instance of datetime
        #    return o.isoformat()
        # otherwise
        #    return super().default(o)
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


class ModelEncoder(DateEncoder, QuerySetEncoder, JSONEncoder):
    encoders = {}
    def default(self, o):
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
        if isinstance(o, self.model):
            dict = {}
            # if o has the attribute get_api_url
            if hasattr(o, "get_api_url"):
                # then add its return value to the dictionary
                #  with  the key "href"
                dict['href'] = o.get_api_url()
            for property in self.properties:
                val = getattr(o, property)
                if property in self.encoders:
                    encoder = self.encoders[property]
                    val = encoder.default(val)
                dict[property] = val
            dict.update(self.get_extra_data(o))
            return dict
        else:
            return super().default(o)

    def get_extra_data(self, o):
        return {}