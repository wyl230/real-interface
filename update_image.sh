#!/bin/bash
docker build -f ./Dockerfile -t video-interface-pku .
docker tag video-interface-pku:latest registry.satellite.pku.edu.cn/stream-control-pku:latest
docker push registry.satellite.pku.edu.cn/stream-control-pku:latest
