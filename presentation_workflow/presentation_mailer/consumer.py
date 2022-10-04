import json
import pika
import django
import os
import sys
from django.core.mail import send_mail


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "presentation_mailer.settings")
django.setup()


def process_approval_message(ch, method, properties, data):
    print("  Received %r" % data)
    presentationDetail = json.loads(data)

    emailBody = (
        presentationDetail.get("presenter_name")
        + ", we're happy to tell you that your presentation "
        + presentationDetail.get("title")
        + " has been accepted"
    )
    send_mail(
        "Your presentation has been accepted",
        emailBody,
        "admin@conference.go",
        [presentationDetail.get("presenter_email")],
        fail_silently=False,
    )


def process_rejection_message(ch, method, properties, data):
    print("  Received %r" % data)
    presentationDetail = json.loads(data)

    emailBody = (
        presentationDetail.get("presenter_name")
        + ", we regret to tell you that your presentation "
        + presentationDetail.get("title")
        + " has been rejected"
    )
    send_mail(
        "Your presentation has been rejected",
        emailBody,
        "admin@conference.go",
        [presentationDetail.get("presenter_email")],
        fail_silently=False,
    )


def process_queues():
    parameters = pika.ConnectionParameters(host="rabbitmq")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue="presentation_approvals")
    channel.queue_declare(queue="presentation_rejections")
    channel.basic_consume(
        queue="presentation_approvals",
        on_message_callback=process_approval_message,
        auto_ack=True,
    )
    channel.basic_consume(
        queue="presentation_rejections",
        on_message_callback=process_rejection_message,
        auto_ack=True,
    )
    channel.start_consuming()


if __name__ == "__main__":
    try:
        process_queues()
    
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


