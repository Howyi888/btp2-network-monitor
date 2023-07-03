FROM node:18 as web
COPY ./web /web
WORKDIR /web

RUN npm install
RUN npm run build

FROM python:3.10-alpine
COPY ./btp2_monitor /app/btp2_monitor
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY --from=web /web/build /app/html
VOLUME [ "/app/data" ]
ENV NETWORKS_JSON="/app/data/networks.json"
ENV DOCUMENT_ROOT="/app/html"
ENV STORAGE_URL="/app/data/storage.db"
EXPOSE 8000
CMD [ "uvicorn", "btp2_monitor.webui:app", "--port", "8000",  "--host", ""]
