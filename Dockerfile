# FROM python:3.9-slim-buster
FROM video-interface:latest
# FROM python:3.9.12
LABEL maintainer="YourName <youremail@example.com>"

WORKDIR ./

# Copy all files to the container
COPY . .
# Install required packages
# RUN pip install  -r requirements.txt

# Expose the default port for MQTT messaging
EXPOSE 5001
EXPOSE 1883

ENTRYPOINT ["python3", "./main.py"]

