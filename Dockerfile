FROM ubuntu:20.04

RUN apt update -y
RUN apt upgrade -y
RUN apt install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install -y python3.9
RUN apt install -y
RUN apt install -y python3-pip
RUN apt install -y jq
RUN pip install poetry
