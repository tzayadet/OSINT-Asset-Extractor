import unittest
from unittest.mock import patch

from asset_security import validate_public_http_url


class PublicURLValidationTests(unittest.TestCase):
    def test_accepts_public_ip_literal(self):
        self.assertTrue(validate_public_http_url("https://93.184.216.34/assets/file.pdf"))

    def test_rejects_private_and_special_ip_literals(self):
        for address in (
            "127.0.0.1",
            "10.0.0.5",
            "172.16.0.1",
            "192.168.1.10",
            "169.254.169.254",
            "::1",
            "fc00::1",
        ):
            with self.subTest(address=address):
                with self.assertRaises(ValueError):
                    validate_public_http_url(f"http://[{address}]/")

    def test_rejects_local_hostnames(self):
        for host in ("localhost", "printer.local", "db.internal", "router.lan"):
            with self.subTest(host=host):
                with self.assertRaises(ValueError):
                    validate_public_http_url(f"http://{host}/")

    def test_rejects_non_http_schemes_and_embedded_credentials(self):
        for url in (
            "file:///etc/passwd",
            "ftp://example.com/file",
            "http://user:pass@example.com/",
        ):
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    validate_public_http_url(url)

    def test_rejects_invalid_ports(self):
        with self.assertRaises(ValueError):
            validate_public_http_url("https://example.com:99999/")

    def test_accepts_public_hostname_when_dns_is_public(self):
        def resolver(host, port, type):
            return [(None, None, None, None, ("93.184.216.34", port))]

        self.assertTrue(
            validate_public_http_url("https://example.com/", resolver=resolver)
        )

    def test_rejects_hostname_with_any_non_public_dns_answer(self):
        def resolver(host, port, type):
            return [
                (None, None, None, None, ("93.184.216.34", port)),
                (None, None, None, None, ("10.0.0.7", port)),
            ]

        with self.assertRaises(ValueError):
            validate_public_http_url("https://example.com/", resolver=resolver)

    def test_rejects_hostname_without_dns_answers(self):
        def resolver(host, port, type):
            return []

        with self.assertRaises(ValueError):
            validate_public_http_url("https://example.com/", resolver=resolver)


if __name__ == "__main__":
    unittest.main()
