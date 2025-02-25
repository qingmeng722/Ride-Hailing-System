FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
RUN apt-get update && apt-get install -yq --no-install-recommends \
    python3-distutils \
    && apt-get clean