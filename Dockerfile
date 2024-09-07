FROM node:18 as web
COPY ./web /web
WORKDIR /web

RUN npm ci
RUN npm run build

FROM python:3.12.0a1-alpine
RUN apk update && apk add --no-cache build-base libffi-dev
ARG MONITOR_VERSION
COPY ./btp2_monitor /app/btp2_monitor
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY --from=web /web/build /app/html
VOLUME [ "/app/data" ]
ENV NETWORKS_JSON="/app/data/networks.json"
ENV DOCUMENT_ROOT="/app/html"
ENV STORAGE_URL="/app/data/storage.db"
ENV MONITOR_VERSION=${MONITOR_VERSION}
EXPOSE 8000
CMD [ "uvicorn", "btp2_monitor.webui:app", "--port", "8000",  "--host", ""]
