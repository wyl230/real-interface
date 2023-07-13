#!/bin/bash
# cp ../pku-stream_generator/sender .
docker build -f ./Dockerfile -t video-interface-pku .
docker tag video-interface-pku:latest registry.satellite.pku.edu.cn/stream-control-pku:latest
docker push registry.satellite.pku.edu.cn/stream-control-pku:latest
