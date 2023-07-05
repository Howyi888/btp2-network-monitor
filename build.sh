#!/bin/bash

VERSION=$(git describe --always --tags --dirty)

docker build --no-cache --build-arg "MONITOR_VERSION=${VERSION}" -t btp2-monitor .
