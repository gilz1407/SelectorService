FROM python:3.6-stretch AS build

ARG REQS=base

COPY ./requirements/$REQS.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]