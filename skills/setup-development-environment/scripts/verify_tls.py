#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import socket
import ssl
import urllib.error
import urllib.request
from urllib.parse import urlparse


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, new_url):
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--minimum-days", type=int, default=14)
    parser.add_argument("--timeout", type=float, default=8)
    args = parser.parse_args()

    parsed = urlparse(args.url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        parser.error("url must be a public https URL without credentials")

    try:
        port = parsed.port or 443
    except ValueError:
        parser.error("url contains an invalid port")
    context = ssl.create_default_context()
    with socket.create_connection((parsed.hostname, port), timeout=args.timeout) as raw_socket:
        with context.wrap_socket(raw_socket, server_hostname=parsed.hostname) as tls_socket:
            certificate = tls_socket.getpeercert()
            expires_at = dt.datetime.fromtimestamp(
                ssl.cert_time_to_seconds(certificate["notAfter"]),
                tz=dt.timezone.utc,
            )
            remaining = expires_at - dt.datetime.now(dt.timezone.utc)
            if remaining < dt.timedelta(days=args.minimum_days):
                raise SystemExit(f"certificate expires too soon: {remaining.days} days")

    http_url = parsed._replace(scheme="http", netloc=parsed.hostname).geturl()
    opener = urllib.request.build_opener(NoRedirect)
    request = urllib.request.Request(http_url, method="GET", headers={"User-Agent": "codex-environment-check/1"})
    try:
        response = opener.open(request, timeout=args.timeout)
        status = response.status
        location = response.headers.get("Location", "")
    except urllib.error.HTTPError as error:
        status = error.code
        location = error.headers.get("Location", "")

    if status not in {301, 302, 307, 308} or not location.startswith("https://"):
        raise SystemExit("HTTP endpoint does not redirect to HTTPS")

    print(json.dumps({
        "hostname": parsed.hostname,
        "expires_at": expires_at.isoformat(),
        "remaining_days": remaining.days,
        "http_redirect_status": status,
        "http_redirect_location": location,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
