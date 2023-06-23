#!/bin/bash

export NETWORKS_JSON="networks.json"
export DOCUEMNT_ROOT="web/build"
export STORAGE_URL="storage.db"

( cd web ; npm run start & )

NPM_PID=$!
trap "kill ${NPM_PID}" EXIT

exec uvicorn btp2-monitor.webui:app --reload
