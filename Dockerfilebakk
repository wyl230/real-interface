# FROM python:3.9-slim-buster
FROM ubuntu:22.04
# FROM python:3.9.12
LABEL maintainer="YourName <youremail@example.com>"

WORKDIR ./
RUN sed -i "s@/archive.ubuntu.com/@/mirrors.tuna.tsinghua.edu.cn/@g" /etc/apt/sources.list \
    && rm -Rf /var/lib/apt/lists/* \
    && apt-get update 

RUN apt-get install -y python3 python3-pip

# Copy all files to the container
COPY . .
# Install required packages
RUN python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt
# RUN pip install  -r requirements.txt

# Expose the default port for MQTT messaging
EXPOSE 5001
EXPOSE 1883

ENTRYPOINT ["python3", "./main.py"]

