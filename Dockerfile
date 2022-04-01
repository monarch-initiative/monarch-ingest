FROM ubuntu:20.04

# Install python & jq & curl

RUN apt update -y
RUN apt upgrade -y
RUN apt install -y python3.8
RUN apt install -y python3.8-venv
RUN apt install -y python3-pip
RUN apt install -y jq
RUN apt install -y curl

# Install gsutil

## Downloading gcloud package
RUN curl https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz > /tmp/google-cloud-sdk.tar.gz

## Installing the package
RUN mkdir -p /usr/local/gcloud \
  && tar -C /usr/local/gcloud -xvf /tmp/google-cloud-sdk.tar.gz \
  && /usr/local/gcloud/google-cloud-sdk/install.sh

## Adding the package path to local
ENV PATH $PATH:/usr/local/gcloud/google-cloud-sdk/bin

# Install poetry and configure for local venv

RUN pip install poetry
RUN poetry config virtualenvs.in-project true
