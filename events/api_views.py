from django.http import JsonResponse
from common.json import ModelEncoder
from .models import Conference, Location, State
from django.views.decorators.http import require_http_methods
import json


class ConferenceListEncoder(ModelEncoder):
    model = Conference
    properties = ["name"]


def api_list_conferences(request):
    conferences = Conference.objects.all()
    return JsonResponse(
        {"conferences": conferences},
        encoder=ConferenceListEncoder,
    )


class LocationListEncoder(ModelEncoder):
    model = Location
    properties = ["name"]


class ConferenceDetailEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
        "description",
        "max_presentations",
        "max_attendees",
        "starts",
        "ends",
        "created",
        "updated",
        "location",
    ]
    encoders = {
        "location": LocationListEncoder(),
    }


def api_show_conference(request, pk):
    conference = Conference.objects.get(id=pk)
    return JsonResponse(conference, ConferenceDetailEncoder, safe=False)


@require_http_methods(["GET", "POST"])
def api_list_locations(request):
    if request.method == "GET":
        locations = Location.objects.all()
        return JsonResponse(
            {"locations": locations},
            encoder=LocationListEncoder,
        )
    else:
        content = json.loads(request.body)
        # get the State obj and put it in the content dict
        state = State.objects.get(abbreviation=content["state"])
        content["state"] = state

        location = Location.objects.create(**content)
        return JsonResponse(
            location,
            LocationDetailEncoder,
            safe=False,
        )


class LocationDetailEncoder(ModelEncoder):
    model = Location
    properties = [
        "name",
        "city",
        "room_count",
        "created",
        "updated",
    ]

    def get_extra_data(self, o):
        return {"state": o.state.abbreviation}


def api_show_location(request, pk):
    location = Location.objects.get(id=pk)
    return JsonResponse(location, LocationDetailEncoder, safe=False)
