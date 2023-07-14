# FROM python:3.9-slim-buster
FROM video-interface-pku:base
# FROM ubuntu:22.04
# FROM python:3.9.12
LABEL maintainer="YourName <youremail@example.com>"

WORKDIR ./

# RUN apt-get update
# RUN apt-get update

# RUN apt-get install -y net-tools
# RUN apt-get install -y vim
# Copy all files to the container
COPY . .
# Install required packages
# RUN apt-get install -y python3 python3-pip

# Copy all files to the container
# Install required packages
# RUN python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt
# RUN pip install  -r requirements.txt


# Expose the default port for MQTT messaging
# EXPOSE 5001
# EXPOSE 1883

ENTRYPOINT ["python3", "./main.py"]

