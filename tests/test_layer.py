import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from ctxlayer import data
from ctxlayer.layer import Claim, leaks, load_claims, naive_search, profile, search, verify

QUERIES = ["remote backend engineer with Go and Postgres", "python pytorch evals", "kubernetes platform manager",
           "remote data engineer snowflake", "founding designer figma", "remote full stack typescript graphql"]


@pytest.fixture(scope="module")
def claims():
    return load_claims()


def test_exactly_the_planted_hallucinations_are_rejected(claims):
    assert {(c.pid, c.field, c.value) for c in claims if c.status != "VERIFIED"} == data.PLANTED_WRONG


@pytest.mark.parametrize("aud", ["agent", "company"])
def test_no_leaks_anywhere(claims, aud):
    for q in QUERIES:
        assert leaks(search(claims, q, aud), aud, claims) == []
    for pid in data.TRANSCRIPTS:
        assert leaks(profile(claims, pid, aud), aud, claims) == []


def test_naive_matcher_does_leak(claims):
    assert sum(len(leaks(naive_search(claims, q), "agent", claims)) for q in QUERIES) > 0


def test_quote_redaction(claims):
    title = next(c for c in profile(claims, "p1", "agent")["claims"] if c["field"] == "title")
    assert "Northwind" not in title["evidence"]["quote"] and "[hidden]" in title["evidence"]["quote"]


def test_audience_widening(claims):
    agent = {c["field"] for c in profile(claims, "p2", "agent")["claims"]}
    company = {c["field"] for c in profile(claims, "p2", "company")["claims"]}
    assert "visa" not in agent and "visa" in company


def test_every_served_claim_has_evidence(claims):
    for pid in data.TRANSCRIPTS:
        for c in profile(claims, pid, "company")["claims"]:
            assert c["evidence"]["quote"] and c["evidence"]["t"]


@pytest.mark.parametrize("value,quote,ok", [
    ("Led a team of 4", "I led a team of four that rebuilt our reconciliation pipeline", True),
    ("Led a team of 12", "I led a team of four that rebuilt our reconciliation pipeline", False),
])
def test_number_check(value, quote, ok):
    assert (verify(Claim("p1", "achievement", value, quote, "02:10")).status == "VERIFIED") == ok


def test_http_endpoint():
    from ctxlayer.server import Handler
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    r = json.loads(urllib.request.urlopen(f"{base}/search?q=remote+go+postgres&audience=agent").read())
    assert r["results"][0]["id"] == "p1"
    assert json.loads(urllib.request.urlopen(f"{base}/tool").read())["name"] == "search_professionals"
    srv.shutdown()
