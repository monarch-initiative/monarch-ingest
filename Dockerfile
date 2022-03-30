FROM ubuntu:20.04

RUN apt update
RUN apt install -y python3-pip
RUN apt install -y jq
RUN pip install poetry

ENTRYPOINT ["poetry","run"]
