#!/bin/bash

export NETWORKS_JSON="networks.json"
export DOCUEMNT_ROOT="web/build"
export STORAGE_URL="storage.db"
export MONITOR_VERSION=$(git describe --always --tags --dirty)

if [ "$1" != "noweb" ] ; then
    ( cd web ; npm run start & )
    NPM_PID=$!
    trap "kill ${NPM_PID}" EXIT
fi

exec uvicorn btp2_monitor.webui:app --reload
