"""Smoke test: import the client, call get_all, and confirm it parses."""

from yc_api import YCClient


def test_get_all() -> None:
    client = YCClient()
    companies = client.get_all()
    assert len(companies) > 0
