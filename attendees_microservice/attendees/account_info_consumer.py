from datetime import datetime
import json
import pika
from pika.exceptions import AMQPConnectionError
import django
import os
import sys
import time

# from symbol import parameters


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendees_bc.settings")
django.setup()

from attendees.models import AccountVO


# Declare a function to update the AccountVO object (ch, method, properties, body)
def update_accountVO(ch, method, properties, body):
    content = json.loads(body)
    print("Got new account ", content)
    # first_name = content["first_name"]
    # last_name = content["last_name"]
    # email = content["email"]
    # is_active = content["is_active"]
    content["updated"] = datetime.fromisoformat(content["updated"])

    if content["is_active"]:
        AccountVO.objects.update_or_create(
            **content, defaults={"email": content["email"]}
        )
    #   otherwise:
    else:
        #       Delete the AccountVO object with the specified email, if it exists
        AccountVO.objects.filter(email=content["email"]).delete()


# Based on the reference code at
#   https://github.com/rabbitmq/rabbitmq-tutorials/blob/master/python/receive_logs.py
# infinite loop
while True:
    try:

        def main():
            # create the pika connection parameters
            parameters = pika.ConnectionParameters(host="rabbitmq")
            # create a blocking connection with the parameters
            connection = pika.BlockingConnection(parameters)
            # open a channel
            channel = connection.channel()
            # declare a fanout exchange named "account_info"
            channel.exchange_declare(
                exchange="account_info", exchange_type="fanout"
            )
            # declare a randomly-named queue
            result = channel.queue_declare(queue="")
            # bind the queue to the "account_info" exchange
            channel.queue_bind(
                exchange="account_info", queue=result.method.queue
            )
            # do a basic_consume for the queue name that calls function above
            channel.basic_consume(
                queue="",
                on_message_callback=update_accountVO,
                auto_ack=True,
            )
            print("Starting to consume...")
            # tell the channel to start consuming
            channel.start_consuming()

        if __name__ == "__main__":
            try:
                main()

            except KeyboardInterrupt:
                print("Interrupted")
                try:
                    sys.exit(0)
                except SystemExit:
                    os._exit(0)

    #   except AMQPConnectionError
    #       print that it could not connect to RabbitMQ
    #       have it sleep for a couple of seconds
    except AMQPConnectionError:
        print("Could not connect to RabbitMQ")
        time.sleep(2.0)
