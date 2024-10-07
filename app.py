"""
Docker Hub Collector

Prometheus exporter for Docker Hub rate limits
"""
import argparse
import logging
import os
import sys
import re
import time
from typing import Optional

import requests
from prometheus_client import start_http_server, REGISTRY
from prometheus_client.metrics_core import GaugeMetricFamily


class DockerHubCollector:
    """
    DockerHubCollector manages the collection of Docker Hub rate limit
    and exposes it as metrics for Prometheus.

    Methods:
        __init__(username, password, request_timeout):
            Initialize the Docker Hub collector with the given username and password.

        retrieve_rate_limit:
            Retrieve the Docker Hub rate limit information for a user.

        collect:
            Prometheus collector function
    """
    def __init__(
            self,
            username: Optional[str] = "",
            password: Optional[str] = "",
            request_timeout: int = 15
    ):
        """
        Initialize the Docker Hub collector with the given username and password.

        :param username: The username/access ID of Docker Hub.
            If empty, then anonymous retrieval will be used.
        :param password: The password/access secret of Docker Hub.
            If empty, then anonymous retrieval will be used.
        :param request_timeout: Timeout of requests in seconds towards Docker Hub
        """
        self._username = "" if username is None else username
        self._password = "" if password is None else password
        self._request_timeout = request_timeout

        if not isinstance(self._username, str) or not isinstance(self._password, str):
            raise ValueError("username and password must be strings")

    def retrieve_rate_limit(self):
        """
        Retrieve the Docker Hub rate limit information for a user.

        This method fetches the rate limits by first obtaining a token and then checking the rate
        limits for a specific Docker image pull.

        If a username and password are set, HTTP Basic authentication will be used.
        Upon successful retrieval, the token is used to make a HEAD request to obtain the
        rate limit headers.

        The rate limits are parsed from the headers and returned in a dictionary.

        The dictionary contains the following keys:
        - limit: The total number of allowed requests within the time interval.
        - remaining: The number of remaining requests within the time interval.
        - interval: The length of the time interval in seconds.
        - source: The source of the rate limits.

        If rate limit headers cannot be retrieved or if there is an error in parsing the headers,
        a `ValueError` is raised.

        :return: A dictionary containing rate limit information.
        :rtype: dict
        """
        # URLs are retrieved from https://docs.docker.com/docker-hub/download-rate-limit/

        # If username and password is set, then append HTTP Basic authentication
        if len(self._username) > 0 and len(self._password) > 0:
            authentication = (self._username, self._password)
        else:
            authentication = None

        # If authenticated method is used, then HTTP
        resp = requests.get(
            url="https://auth.docker.io/token?service=registry.docker.io&scope=repository:ratelimitpreview/test:pull", # pylint: disable=line-too-long
            auth=authentication,
            json=True,
            timeout=self._request_timeout
        )
        resp.raise_for_status()
        logging.debug("Successfully retrieved token!")

        # Retrieve rate limits by retrieving an example image
        headers = {
            "Authorization": f"Bearer {resp.json()['token']}"
        }
        resp = requests.head(
            url="https://registry-1.docker.io/v2/ratelimitpreview/test/manifests/latest",
            headers=headers,
            timeout=self._request_timeout
        )
        resp.raise_for_status()
        limit_resp = resp.headers.get('ratelimit-limit')
        remaining_resp = resp.headers.get('ratelimit-remaining')
        source = resp.headers.get('docker-ratelimit-source')

        # Print response messages
        logging.debug("ratelimit-limit: %s", limit_resp)
        logging.debug("ratelimit-remaining: %s", remaining_resp)
        logging.debug("docker-ratelimit-source: %s", source)

        if limit_resp is None or remaining_resp is None or source is None:
            raise ValueError(
                "ratelimit-limit, ratelimit-remaining or "
                "docker-ratelimit-source could not be retrieved"
            )

        # Parse retrieved headers
        rate_regex = re.compile(r"^(?P<limit>\d+);w=(?P<limit_interval>\d+)$")
        limit_match = rate_regex.match(limit_resp)
        remaining_match = rate_regex.match(remaining_resp)
        limit = limit_match.group("limit")
        limit_interval = limit_match.group("limit_interval")
        remaining = remaining_match.group("limit")
        remaining_interval = remaining_match.group("limit_interval")

        if (limit is None or limit_interval is None or
                remaining is None or remaining_interval is None):
            raise ValueError("Error while parsing rate limits")
        if int(limit_interval) != int(remaining_interval):
            raise ValueError("Intervals do not match!")

        # Print parsed values
        logging.debug("limit: %d", int(limit))
        logging.debug("remaining: %d", int(remaining))
        logging.debug("interval: %d", int(remaining_interval))
        logging.debug("source: %s", source)

        return {
            "limit": int(limit),
            "remaining": int(remaining),
            "interval": int(remaining_interval),
            "source": source
        }

    def collect(self):
        """
        Prometheus collector function
        """
        limits = self.retrieve_rate_limit()
        pulls_remaining = GaugeMetricFamily(
            name="dockerhub_pulls_remaining",
            documentation="Remaining pulls for Docker Hub",
            labels=["interval", "source"]
        )
        pulls_remaining.add_metric([str(limits["interval"]), limits["source"]], limits["remaining"])
        yield pulls_remaining

        pulls_total = GaugeMetricFamily(
            name="dockerhub_pulls_total",
            documentation="Total allowed pulls for Docker Hub",
            labels=["interval", "source"]
        )
        pulls_total.add_metric([str(limits["interval"]), limits["source"]], limits["limit"])
        yield pulls_total


def validate_arguments(options):
    """
    Validate argparse arguments

    :param options: Arguments coming from argparse
    :return: None
    :raises ValueError: If the port is not between 1 and 65535.
    :raises ValueError: If the timeout is less than 1 sec.
    :raises ValueError: If the listen address is not a valid IP address in the format of '1.2.3.4'.
    :raises ValueError: If only one of TLS key or TLS certificate is provided without the other.
    """
    # Port check
    if options.port < 1 or options.port > 65535:
        raise ValueError("Port must be between 1 and 65535")

    if options.timeout < 1:
        raise ValueError("Timeout must be a positive number")

    # Listen address check
    ip_regex = re.compile(r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$")
    if not ip_regex.match(options.listen):
        raise ValueError("IP address must be in the format of '1.2.3.4'")

    # TLS mutual inclusivity checks
    if (options.tls_key and not options.tls_crt) or (options.tls_crt and not options.tls_key):
        raise ValueError("TLS key and TLS crt must be specified if HTTPS is enabled!")


def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(
        description="Prometheus collector for Docker Hub rate limits"
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=8000,
        help="Port to expose metrics to (default: 8000)",
    )
    parser.add_argument(
        "-l", "--listen",
        type=str,
        default="0.0.0.0",
        help="Address to listen from (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--tls-crt",
        type=argparse.FileType("r"),
        help="TLS certificate file for HTTPS",
    )
    parser.add_argument(
        "--tls-key",
        type=argparse.FileType("r"),
        help="TLS private key file for HTTPS",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="Timeout of requests in seconds towards Docker Hub (default: 15)",
    )
    parser.add_argument(
        '-v', '--verbose',
        help='Enable verbose logs',
        action='store_const', dest='loglevel', const=logging.DEBUG,
        default=logging.INFO
    )
    options = parser.parse_args()
    logging.basicConfig(
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=options.loglevel
    )

    # Validate arguments
    try:
        validate_arguments(options)
    except ValueError as e:
        logging.critical("Error validating arguments: %s", e)
        sys.exit(1)

    # Check the mutual inclusivity of the Docker Hub credentials
    if (os.getenv("DOCKER_HUB_USERNAME") is not None and
        os.getenv("DOCKER_HUB_PASSWORD") is None) or \
       (os.getenv("DOCKER_HUB_USERNAME") is None and
        os.getenv("DOCKER_HUB_PASSWORD") is not None):
        logging.critical("DOCKER_HUB_USERNAME and DOCKER_HUB_PASSWORD must be set together!")
        sys.exit(1)

    use_https = bool(options.tls_crt and options.tls_key)

    # Start Prometheus exporter
    if use_https:
        start_http_server(
            port=options.port,
            addr=options.listen,
            certfile=options.tls_crt.name,
            keyfile=options.tls_key.name
        )
    else:
        start_http_server(
            port=options.port,
            addr=options.listen
        )
    REGISTRY.register(
        DockerHubCollector(
            os.getenv("DOCKER_HUB_USERNAME"),
            os.getenv("DOCKER_HUB_PASSWORD"),
            options.timeout
        )
    )
    logging.info("Exporter started at %s://%s:%d",
                 ('https' if use_https else 'http'),
                 options.listen,
                 options.port
    )
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shutting down...")


if __name__ == "__main__":
    main()
