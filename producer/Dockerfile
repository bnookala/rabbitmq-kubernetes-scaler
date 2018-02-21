FROM jfloff/alpine-python:2.7-onbuild
ADD .  /application
ADD ./kubeconfig.json /
ENV KUBECONFIG=/kubeconfig.json
ENTRYPOINT python /application/producer/producer.py