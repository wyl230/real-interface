
docker run --rm -v "$PWD":/src -w /src gcc-test:latest g++ sender-re.cpp loguru.cpp  -std=c++20 -lpthread -ldl
