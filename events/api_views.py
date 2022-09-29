from django.http import JsonResponse
from common.json import ModelEncoder
from .models import Conference, Location, State
from django.views.decorators.http import require_http_methods
import json


class ConferenceListEncoder(ModelEncoder):
    model = Conference
    properties = ["name"]


@require_http_methods(["GET", "POST"])
def api_list_conferences(request):
    if request.method == "GET":
        conferences = Conference.objects.all()
        return JsonResponse(
            {"conferences": conferences},
            encoder=ConferenceListEncoder,
        )
    else:
        content = json.loads(request.body)
    #    Get the location obj and put it in the content dict
        try:
            location = Location.objects.get(id=content["location"])
            content["location"] = location
        except Location.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid location id"},
                status=400,
            )
        
        conference = Conference.objects.create(**content)
        return JsonResponse(
            conference,
            ConferenceDetailEncoder,
            safe=False,
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

@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_conference(request, pk):
    if request.method == "GET":
        conference = Conference.objects.get(id=pk)
        return JsonResponse(conference, ConferenceDetailEncoder, safe=False)
    elif request.method == "DELETE":
        count, _ = Conference.objects.filter(id=pk).delete()
        return JsonResponse(
            {"deleted": count > 0}
        )  # returns true if something is deleted
    else:
        # copied from create
        content = json.loads(request.body)
        try:
            # new code
            if "location" in content:
                location = Location.objects.get(abbreviation=content["location"])
                content["location"] = location
        except Location.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
            )

        # new code
        Conference.objects.filter(id=pk).update(**content)

        # copied from get detail
        conference = Conference.objects.get(id=pk)
        return JsonResponse(
            conference,
            encoder=ConferenceDetailEncoder,
            safe=False,
        )


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
        try:
            # get the State obj and put it in the content dict
            state = State.objects.get(abbreviation=content["state"])
            content["state"] = state
        except State.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
            )

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


@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_location(request, pk):
    if request.method == "GET":
        location = Location.objects.get(id=pk)
        return JsonResponse(location, LocationDetailEncoder, safe=False)
    elif request.method == "DELETE":
        count, _ = Location.objects.filter(id=pk).delete()
        return JsonResponse(
            {"deleted": count > 0}
        )  # returns true if something is deleted
    else:
        # copied from create
        content = json.loads(request.body)
        try:
            # new code
            if "state" in content:
                state = State.objects.get(abbreviation=content["state"])
                content["state"] = state
        except State.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
            )

        # new code
        Location.objects.filter(id=pk).update(**content)

        # copied from get detail
        location = Location.objects.get(id=pk)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )

