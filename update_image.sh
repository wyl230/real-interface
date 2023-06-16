#!/bin/bash
docker build -f ./Dockerfile -t video-interface .
docker tag video-interface:latest registry.satellite.pku.edu.cn/stream-control:v1
docker push registry.satellite.pku.edu.cn/stream-control:v1
