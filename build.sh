#!/bin/bash

VERSION=$(git describe --always --tags --dirty)

docker build --build-arg "MONITOR_VERSION=${VERSION}" -t btp2-monitor .
