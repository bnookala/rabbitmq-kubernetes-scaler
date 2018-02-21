#!/usr/bin/env python

import pika
import time
import os

credentials = pika.PlainCredentials('user', os.environ['RABBIT_PASSWORD'])
parameters = pika.ConnectionParameters(os.environ['RABBIT_URL'], 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)

channel = connection.channel()
channel.queue_declare(queue=os.environ['QUEUE'])


# Callback to pretend to do work.
def callback(ch, method, properties, body):
    print method.delivery_tag

    print(" [x] Received %r" % body)
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    channel.basic_ack(delivery_tag=method.delivery_tag)

# Prefetch count to 1, otherwise the consumer gets all the data.
channel.basic_qos(
    prefetch_count=1,
    all_channels=True
)

channel.basic_consume(
    callback,
    queue=os.environ['QUEUE']
)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()