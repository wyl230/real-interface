# FROM python:3.9-slim-buster
FROM video-interface:latest
# FROM python:3.9.12
LABEL maintainer="YourName <youremail@example.com>"

WORKDIR ./

# RUN sed -i "s@/archive.ubuntu.com/@/mirrors.tuna.tsinghua.edu.cn/@g" /etc/apt/sources.list \
    # && rm -Rf /var/lib/apt/lists/* \
    # && apt-get update
    #
# RUN apt-get update

# RUN apt-get install -y net-tools
# RUN apt-get install -y vim
# Copy all files to the container
COPY . .
# Install required packages
# RUN pip install  -r requirements.txt

# Expose the default port for MQTT messaging
EXPOSE 5001
EXPOSE 1883

ENTRYPOINT ["python3", "./main.py"]

