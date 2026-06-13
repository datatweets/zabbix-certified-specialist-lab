# demo-api — a tiny Flask service exposing JSON metrics for the Online Shop.
# Endpoints:
#   GET /health   -> {"status": "ok"}
#   GET /metrics  -> {"orders": .., "failed_payments": .., "queue_length": ..,
#                     "response_time_ms": ..}
#   GET /slow     -> deliberately slow response (for response-time triggers)
#   GET /boom     -> returns HTTP 500 (for HTTP-error triggers)
FROM python:3.12-alpine

RUN pip install --no-cache-dir flask==3.0.3

WORKDIR /app
COPY app.py /app/app.py

EXPOSE 5000
CMD ["python", "/app/app.py"]
