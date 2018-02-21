#!/usr/bin/env python

import pika
import sys
import random
import os

credentials = pika.PlainCredentials('user', os.environ['RABBIT_PASSWORD'])
parameters = pika.ConnectionParameters(os.environ['RABBIT_URL'], 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue=os.environ['QUEUE'])

for i in range(50):
    message = '.' * random.randint(10, 100)
    channel.basic_publish(
        exchange='',
        routing_key=os.environ['QUEUE'],
        body=message,
        properties=pika.BasicProperties(
            delivery_mode = 2, # make message persistent
        )
    )
    print(" [x] Sent %r" % message)

channel.close()