![GitHub Release](https://img.shields.io/github/v/release/berkitamas/dockerhub-ratelimit-exporter) ![GitHub License](https://img.shields.io/github/license/berkitamas/dockerhub-ratelimit-exporter)


Docker Hub rate limit exporter
==============================

Prometheus exporter for Docker Hub rate limits

**Note:** To follow the highly advised least privilege principle, use an access token with "Public Repo Read-only" privileges.

Installation
------------
### Using Docker image
```
# Anonymous
docker run -it --rm \
  -p 8000:8000 \
  docker.io/berkitamas/dockerhub-ratelimit-exporter:<tag or latest>

# Authenticated
docker run -it --rm \
  -p 8000:8000 \
  -e DOCKER_HUB_USERNAME="username" \
  -e DOCKER_HUB_PASSWORD="changeme" \
  docker.io/berkitamas/dockerhub-ratelimit-exporter:<tag or latest>
```
### Manually
```
# Optionally create a Python venv
# Install Python requirements
pip install -r requirements.txt
# Start the application
python app.py
```

Usage
-----
```
usage: app.py [-h] [-p PORT] [-l LISTEN] [--tls-crt TLS_CRT] [--tls-key TLS_KEY] [--timeout TIMEOUT] [-v]

Prometheus collector for Docker Hub rate limits

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Port to expose metrics to (default: 8000)
  -l LISTEN, --listen LISTEN
                        Address to listen from (default: 0.0.0.0)
  --tls-crt TLS_CRT     TLS certificate file for HTTPS
  --tls-key TLS_KEY     TLS private key file for HTTPS
  --timeout TIMEOUT     Timeout of requests in seconds towards Docker Hub (default: 15)
  -v, --verbose         Enable verbose logs

```

Exposed metrics
---------------
(excluding common metrics)
```
# HELP dockerhub_pulls_remaining Remaining pulls for Docker Hub
# TYPE dockerhub_pulls_remaining gauge
dockerhub_pulls_remaining{interval="21600",source="<IP address or user UUID>"} 96.0
# HELP dockerhub_pulls_total Total allowed pulls for Docker Hub
# TYPE dockerhub_pulls_total gauge
dockerhub_pulls_total{interval="21600",source="<IP address or user UUID>"} 100.0
```

Environment variables
---------
* `DOCKER_HUB_USERNAME`: Docker Hub username/access ID
* `DOCKER_HUB_PASSWORD`: Docker Hub password/access secret

References
----------
* [Docker Hub rate limiting](https://docs.docker.com/docker-hub/download-rate-limit/)
