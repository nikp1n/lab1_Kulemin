from flask import Flask, Response
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
import time

app = Flask(__name__)


REQUESTS_TOTAL = Counter(
    "app_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Request latency",
    ["endpoint"]
)

APP_HEALTH = Gauge(
    "app_health_status",
    "Application health status (1 = healthy, 0 = unhealthy)"
)


@app.before_request
def start_timer():
    from flask import g
    g.start_time = time.time()

@app.after_request
def record_metrics(response):
    from flask import request, g

    latency = time.time() - g.start_time
    endpoint = request.path

    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
    REQUESTS_TOTAL.labels(
        method=request.method,
        endpoint=endpoint,
        status=response.status_code
    ).inc()

    return response


@app.route("/")
def index():
    return "OK"

@app.route("/api")
def api():
    return "API response"

@app.route("/health")
def health():
    APP_HEALTH.set(1)
    return "healthy"

@app.route("/ready")
def ready():
    return "ready"

@app.route("/metrics")
def metrics():
    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST
    )


if __name__ == "__main__":
    APP_HEALTH.set(1)
    app.run(host="0.0.0.0", port=8080)
