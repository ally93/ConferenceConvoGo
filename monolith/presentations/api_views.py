from django.http import JsonResponse
from common.json import ModelEncoder
from events.api_views import ConferenceListEncoder
from .models import Presentation, Status
from django.views.decorators.http import require_http_methods
import json
from events.models import Conference
import pika

# from attendees.models import Attendee
# from attendees.api_views import AttendeeDetailEncoder


class PresentationListEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "title",
    ]

    def get_extra_data(self, o):
        return {"status": o.status.name}


@require_http_methods(["GET", "POST"])
def api_list_presentations(request, conference_id):
    if request.method == "GET":
        presentations = Presentation.objects.filter(conference=conference_id)
        return JsonResponse(
            {"presentations": presentations}, encoder=PresentationListEncoder
        )
    else:
        content = json.loads(request.body)

        # Get the Conference object and put it in the content dict
        try:
            conference = Conference.objects.get(id=conference_id)
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400,
            )

        presentation = Presentation.create(**content)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )


class PresentationDetailEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "presenter_name",
        "company_name",
        "presenter_email",
        "title",
        "synopsis",
        "created",
        "conference",
    ]
    encoders = {
        "conference": ConferenceListEncoder(),
    }

    def get_extra_data(self, o):
        return {"status": o.status.name}


@require_http_methods(["GET", "PUT", "DELETE"])
def api_show_presentation(request, pk):
    if request.method == "GET":
        presentation = Presentation.objects.get(id=pk)
        return JsonResponse(
            presentation, PresentationDetailEncoder, safe=False
        )
    elif request.method == "DELETE":
        count, _ = Presentation.objects.filter(id=pk).delete()
        return JsonResponse(
            {"deleted": count > 0}
        )  # returns true if something is deleted
    else:
        # copied from create
        content = json.loads(request.body)
        try:
            # new code
            if "status" in content:
                status = Status.objects.get(name=content["status"])
                content["status"] = status
        except Status.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid status"},
                status=400,
            )
        try:
            # new code
            if "conference" in content:
                conference = Conference.objects.get(name=content["conference"])
                content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference"},
                status=400,
            )

        # new code
        Presentation.objects.filter(id=pk).update(**content)

        # copied from get detail
        presentation = Presentation.objects.get(id=pk)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )


@require_http_methods(["PUT"])
def api_approve_presentation(request, pk):
    presentation = Presentation.objects.get(id=pk)
    presentation.approve()
    presentationJson = JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )
    producer(presentation, "presentation_approvals")
    return presentationJson


@require_http_methods(["PUT"])
def api_reject_presentation(request, pk):
    presentation = Presentation.objects.get(id=pk)
    presentation.reject()
    presentationJson = JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )
    producer(presentation, 'presentation_rejections')
    return presentationJson


class PresentationProducerEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "presenter_name",
        "presenter_email",
        "title",
    ]


def producer(data, q_name):
    parameters = pika.ConnectionParameters(host="rabbitmq")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=q_name)
    channel.basic_publish(
        exchange="",
        routing_key=q_name,
        body=json.dumps(data, cls=PresentationProducerEncoder),
    )
    connection.close()
