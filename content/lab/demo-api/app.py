"""demo-api: a minimal Online Shop API that emits JSON metrics for Zabbix.

It returns slowly-changing pseudo-random business metrics so that HTTP-agent
items, JSONPath preprocessing, dependent items and triggers all have realistic
data to work with. No external dependencies beyond Flask.
"""
import time
from flask import Flask, jsonify, Response

app = Flask(__name__)
START = time.time()


def _metrics():
    # Deterministic-ish values derived from uptime so graphs move but stay sane.
    t = int(time.time() - START)
    orders = 1000 + (t // 5)
    failed_payments = (t // 60) % 7
    queue_length = (t % 50)
    response_time_ms = 50 + (t % 30)
    return {
        "orders": orders,
        "failed_payments": failed_payments,
        "queue_length": queue_length,
        "response_time_ms": response_time_ms,
    }


@app.route("/health")
def health():
    return jsonify(status="ok", uptime_seconds=int(time.time() - START))


@app.route("/metrics")
def metrics():
    return jsonify(_metrics())


@app.route("/slow")
def slow():
    time.sleep(3)
    return jsonify(status="ok", note="deliberately slow")


@app.route("/boom")
def boom():
    return Response('{"error":"simulated failure"}',
                    status=500, mimetype="application/json")


@app.route("/")
def root():
    return jsonify(service="demo-api", endpoints=["/health", "/metrics", "/slow", "/boom"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
