FROM python:3

ENV LOG_LEVEL=WARNING
ENV PORT=50051
ENV HOST_ENDPOINT=localhost:50050
ENV MAX_WORKERS=10

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD python ./src/function.py --log-level $LOG_LEVEL --port $PORT --host-endpoint $HOST_ENDPOINT --max-workers $MAX_WORKERS
