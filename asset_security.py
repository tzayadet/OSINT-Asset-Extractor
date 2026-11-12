"""Network-scope validation for the OSINT asset collector."""

import ipaddress
import socket
from urllib.parse import urlsplit


BLOCKED_SUFFIXES = (
    ".localhost",
    ".local",
    ".internal",
    ".lan",
)


def validate_public_http_url(url, resolver=None):
    """Reject non-HTTP URLs, embedded credentials and non-public destinations.

    Hostnames are resolved and every returned address must be globally routable.
    This is a scope guard, not a network sandbox or DNS-pinning implementation.
    """
    parsed = urlsplit(url)
    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError("Only HTTP and HTTPS URLs are allowed.")
    if not parsed.hostname:
        raise ValueError("URL must contain a hostname.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("URLs containing embedded credentials are not allowed.")

    try:
        port = parsed.port or (443 if parsed.scheme.lower() == "https" else 80)
    except ValueError as exc:
        raise ValueError("URL contains an invalid port.") from exc

    hostname = parsed.hostname.rstrip(".").lower()
    if not hostname or hostname == "localhost" or hostname.endswith(BLOCKED_SUFFIXES):
        raise ValueError("Local or internal hostnames are not allowed.")

    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        lookup = resolver or socket.getaddrinfo
        try:
            records = lookup(hostname, port, type=socket.SOCK_STREAM)
        except OSError as exc:
            raise ValueError(f"Hostname could not be resolved: {hostname}") from exc

        addresses = set()
        for record in records:
            try:
                addresses.add(ipaddress.ip_address(record[4][0].split("%", 1)[0]))
            except (ValueError, IndexError, TypeError):
                continue
        if not addresses:
            raise ValueError(f"Hostname has no usable IP addresses: {hostname}")
        if any(not item.is_global for item in addresses):
            raise ValueError(f"Hostname resolves to a non-public address: {hostname}")
    else:
        if not address.is_global:
            raise ValueError("Private, loopback, link-local or reserved IPs are not allowed.")

    return True
