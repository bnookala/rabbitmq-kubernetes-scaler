#!/usr/bin/env python

import pika
import sys
import time
import threading
from pyrabbit.api import Client as Rabbit
import kubernetes.client
from kubernetes import config
import os

config.load_kube_config()
v1 = kubernetes.client.CoreV1Api()
queue_threshold = 50
consumer_limit = 100

rabbit = Rabbit(os.environ['RABBIT_URL'] + ':15672', 'user', os.environ['RABBIT_PASSWORD'])

def timer():
    threading.Timer(30, timer).start()
    queue_length = rabbit.get_queue_depth('/', os.environ['QUEUE'])
    print("queue length is " + str(queue_length))

    api_response = get_existing_consumers()
    consumer_count = len(api_response.items)

    # conditions for scaling:
    # 1. no consumer nodes
    # 2. queue length is greater than our allowed threshold
    if consumer_count == 0:
        print("scaling up due to no available consumers in the queue")
        scale_up()
        return

    if queue_length >= queue_threshold:
        print("scaling up due to high queue")
        scale_up()
        return

    if queue_length <= queue_length and consumer_count >= 1:
        print("scaling down")
        # todo: implement scale down
        scale_down()
        return


def scale_down():
    # Not implemented yet.
    pass


def scale_up():
    namespace = 'default'

    pod = build_consumer_pod()

    container = build_container()
    container.env = [
        build_rabbit_url_env(),
        build_rabbit_queue_env(),
        build_rabbit_secret_env()
    ]

    image_pull_secret = kubernetes.client.V1LocalObjectReference()
    image_pull_secret.name = "acrsecret"

    pod.spec = kubernetes.client.V1PodSpec(
        containers=[container],
        image_pull_secrets=[image_pull_secret]
    )

    pretty = 'false'
    api_response = v1.create_namespaced_pod(namespace, pod, pretty=pretty)
    print(api_response)


def build_consumer_pod():
    metadata = kubernetes.client.V1ObjectMeta(
        generate_name="consumermq-",
        labels={
            "type": "consumermq"
        }
    )

    pod = kubernetes.client.V1Pod(
        api_version="v1",
        kind="Pod",
        metadata=metadata
    )

    return pod

def build_container():
    return kubernetes.client.V1Container(
        name="consumer-container",
        image="my-private-acr.azurecr.io/rabbitmq-k8s-consumer",
        image_pull_policy="Always"
    )

def build_rabbit_url_env():
    return kubernetes.client.V1EnvVar(
        name="RABBIT_URL",
        value=os.environ["RABBIT_URL"]
    )

def build_rabbit_queue_env():
    return kubernetes.client.V1EnvVar(
        name="QUEUE",
        value=os.environ["QUEUE"]
    )

def build_rabbit_secret_env():
    secret_key_ref = kubernetes.client.V1SecretKeySelector(
        name="rabbitsecret",
        key="password"
    )

    rabbit_secret = kubernetes.client.V1EnvVarSource(
        secret_key_ref=secret_key_ref
    )

    rabbit_password = kubernetes.client.V1EnvVar(
        name="RABBIT_PASSWORD",
        value_from=rabbit_secret
    )

    return rabbit_password

def get_existing_consumers():
    ns = 'default'
    label_selector = 'type=consumermq'

    pods = v1.list_namespaced_pod(ns, label_selector=label_selector)
    return pods


timer()