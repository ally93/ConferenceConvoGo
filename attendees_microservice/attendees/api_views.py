from django.http import JsonResponse
from common.json import ModelEncoder

# from events.models import Conference
from .models import Attendee, ConferenceVO, AccountVO

# from events.api_views import ConferenceListEncoder
from django.views.decorators.http import require_http_methods
import json


class ConferenceVODetailEncoder(ModelEncoder):
    model = ConferenceVO
    properties = ["name", "import_href"]


class AttendeeListEncoder(ModelEncoder):
    model = Attendee
    properties = ["name"]


@require_http_methods(["GET", "POST"])
def api_list_attendees(request, conference_vo_id=None):
    if request.method == "GET":
        attendees = Attendee.objects.filter(conference=conference_vo_id)
        return JsonResponse(
            {"attendees": attendees},
            encoder=AttendeeListEncoder,
        )
    else:
        content = json.loads(request.body)

        # Get the Conference object and put it in the content dict
        try:
            conference_href = f"/api/conferences/{conference_vo_id}/"
            conference = ConferenceVO.objects.get(import_href=conference_href)
            content["conference"] = conference
        except ConferenceVO.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400,
            )

        attendee = Attendee.objects.create(**content)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )


# class ConferenceEncoder(ModelEncoder):
#     model = Conference
#     properties = ["name"]


class AttendeeDetailEncoder(ModelEncoder):
    model = Attendee
    properties = ["email", "name", "company_name", "created", "conference"]
    encoders = {
        "conference": ConferenceVODetailEncoder(),
    }

    def get_extra_data(self, o):
        # Get the count of AccountVO objects with email equal to o.email
        count = AccountVO.objects.filter(email=o.email).count()
        # Return a dictionary with "has_account": True if count > 0
        val = {"has_account": count > 0}
        return val



@require_http_methods(["GET", "PUT", "DELETE"])
def api_show_attendee(request, pk):
    if request.method == "GET":
        attendee = Attendee.objects.get(id=pk)
        return JsonResponse(attendee, AttendeeDetailEncoder, safe=False)
    elif request.method == "DELETE":
        count, _ = Attendee.objects.filter(id=pk).delete()
        return JsonResponse(
            {"deleted": count > 0}
        )  # returns true if something is deleted
    else:
        # copied from create
        content = json.loads(request.body)
        try:
            # new code
            if "conference" in content:
                conference = ConferenceVO.objects.get(
                    abbreviation=content["location"]
                )
                content["conference"] = conference
        except ConferenceVO.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
            )

        # new code
        Attendee.objects.filter(id=pk).update(**content)

        # copied from get detail
        attendee = Attendee.objects.get(id=pk)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )
