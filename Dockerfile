FROM ubuntu:20.04

RUN apt update -y
RUN apt upgrade -y
RUN apt install -y python3.8
RUN apt install -y python3.8-venv
RUN apt install -y python3-pip
RUN apt install -y jq
RUN pip install poetry
RUN poetry config virtualenvs.in-project true
