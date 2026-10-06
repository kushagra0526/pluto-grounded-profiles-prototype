"""Grounding verifier + visibility policy + matcher for voice-built profiles.

Audiences, narrowest first: private (only the person) < companies (verified hiring teams) < agents (any AI agent).
A requester sees a field only if the person shared it at least that widely, and only VERIFIED claims are ever served.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher

from . import data

LEVEL = {"private": 0, "companies": 1, "agents": 2}
REQUESTER = {"agent": 2, "company": 1}
NUM_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
             "ten": 10, "eleven": 11, "twelve": 12, "twenty": 20, "thirty": 30, "forty": 40}
TITLE_WORDS = {"junior", "senior", "staff", "principal", "lead", "head", "director", "manager", "vp"}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9%]+", " ", s.lower()).strip()


def _numbers(s: str) -> set[int]:
    out = {int(x.replace(",", "")) for x in re.findall(r"\d[\d,]*", s)}
    out |= {NUM_WORDS[w] for w in re.findall(r"[a-z]+", s.lower()) if w in NUM_WORDS}
    return out


@dataclass
class Claim:
    pid: str
    field: str
    value: str
    quote: str
    t: str
    status: str = "UNCHECKED"     # VERIFIED | UNSUPPORTED
    why: str = ""


def find_quote(pid: str, quote: str) -> tuple[str, str] | None:
    """Return (timestamp, turn text) whose text contains the quote (exact after normalising, or ≥ 0.9 fuzzy)."""
    q = _norm(quote)
    for t, text in data.TRANSCRIPTS[pid]:
        n = _norm(text)
        if q in n:
            return t, text
        if len(q) > 12:
            for i in range(0, max(1, len(n) - len(q) + 1), 3):
                if SequenceMatcher(None, q, n[i:i + len(q)]).ratio() >= 0.9:
                    return t, text
    return None


def verify(c: Claim) -> Claim:
    hit = find_quote(c.pid, c.quote)
    if hit is None:
        c.status, c.why = "UNSUPPORTED", "quote not found in the transcript"
        return c
    q = _norm(c.quote)
    vn, qn = _numbers(c.value), _numbers(c.quote)
    if vn - qn:
        c.status, c.why = "UNSUPPORTED", f"number {sorted(vn - qn)} not in the quote (quote says {sorted(qn) or 'none'})"
        return c
    if c.field == "skills" and _norm(c.value) not in q:
        c.status, c.why = "UNSUPPORTED", f"'{c.value}' is never said in the quote"
        return c
    if c.field == "title":
        extra = set(_norm(c.value).split()) & TITLE_WORDS - set(q.split())
        if extra:
            c.status, c.why = "UNSUPPORTED", f"title word(s) {sorted(extra)} not said — quote: '{c.quote}'"
            return c
    if c.field == "employer" and _norm(c.value) not in q:
        c.status, c.why = "UNSUPPORTED", "employer name not in the quote"
        return c
    c.status = "VERIFIED"
    return c


def load_claims() -> list[Claim]:
    return [verify(Claim(pid, f, v, q, t)) for pid, rows in data.CLAIMS.items() for f, v, q, t in rows]


def visibility(pid: str, fld: str) -> str:
    return data.VISIBILITY_OVERRIDES.get(pid, {}).get(fld, data.VISIBILITY_DEFAULT.get(fld, "private"))


def visible(c: Claim, audience: str) -> bool:
    return c.status == "VERIFIED" and LEVEL[visibility(c.pid, c.field)] >= REQUESTER[audience]


def redact(claims: list[Claim], pid: str, audience: str, quote: str) -> str:
    """Evidence quotes are verbatim speech, so they can mention a field the person kept private
    ("senior engineer at <private employer>"). Blank out every hidden value of this person."""
    for c in claims:
        if c.pid == pid and not visible(c, audience) and len(c.value) > 2:
            quote = re.sub(re.escape(c.value), "[hidden]", quote, flags=re.I)
    return quote


# ------------------------------------------------------------------ profile + search (the agent-facing surface)

def profile(claims: list[Claim], pid: str, audience: str) -> dict:
    out: dict = {"id": pid, "name": data.NAMES[pid], "claims": []}
    for c in claims:
        if c.pid == pid and visible(c, audience):
            out["claims"].append({"field": c.field, "value": c.value,
                                 "evidence": {"quote": redact(claims, pid, audience, c.quote), "t": c.t}})
    return out


SKILL_VOCAB = {"go", "postgres", "python", "pytorch", "kubernetes", "docker", "figma", "react", "typescript", "graphql",
               "spark", "snowflake", "node"}


def parse_query(q: str) -> dict:
    words = set(_norm(q).split())
    return {"skills": words & SKILL_VOCAB, "remote": "remote" in words,
            "terms": words - SKILL_VOCAB - {"remote", "a", "an", "the", "who", "with", "and", "or", "for", "in", "wants", "want"}}


def search(claims: list[Claim], query: str, audience: str, k: int = 3) -> list[dict]:
    q = parse_query(query)
    results = []
    for pid in data.TRANSCRIPTS:
        vis = [c for c in claims if c.pid == pid and visible(c, audience)]
        score, reasons = 0.0, []
        for c in vis:
            v = _norm(c.value)
            if c.field == "skills" and v in q["skills"]:
                score += 2
                reasons.append({"why": f"said they use {c.value}", "quote": redact(claims, pid, audience, c.quote), "t": c.t})
            if c.field == "wants" and q["remote"] and "remote" in v:
                score += 1.5
                reasons.append({"why": "wants remote", "quote": redact(claims, pid, audience, c.quote), "t": c.t})
            hits = q["terms"] & set(v.split())
            if c.field in ("role", "wants", "achievement") and hits:
                score += 0.5 * len(hits)
                reasons.append({"why": f"{c.field}: {c.value}", "quote": redact(claims, pid, audience, c.quote), "t": c.t})
        if score:
            results.append({"id": pid, "name": data.NAMES[pid], "score": round(score, 2), "reasons": reasons[:4]})
    return sorted(results, key=lambda r: -r["score"])[:k]


def naive_search(claims: list[Claim], query: str, k: int = 3) -> list[dict]:
    """What a matcher looks like without the two guards: every claim, verified or not, any visibility."""
    q = parse_query(query)
    results = []
    for pid in data.TRANSCRIPTS:
        mine = [c for c in claims if c.pid == pid]
        score = sum(2 for c in mine if c.field == "skills" and _norm(c.value) in q["skills"])
        score += sum(1.5 for c in mine if c.field == "wants" and q["remote"] and "remote" in _norm(c.value))
        if score:
            summary = "; ".join(f"{c.field}: {c.value}" for c in mine)
            results.append({"id": pid, "name": data.NAMES[pid], "score": score, "summary": summary})
    return sorted(results, key=lambda r: -r["score"])[:k]


def leaks(response, audience: str, claims: list[Claim]) -> list[str]:
    """Private/out-of-scope or unverified values of a person that appear in that person's part of a response."""
    items = response if isinstance(response, list) else [response]
    text = {r["id"]: str(r).lower() for r in items}
    bad = []
    for c in claims:
        hidden = c.status != "VERIFIED" or LEVEL[visibility(c.pid, c.field)] < REQUESTER[audience]
        if hidden and c.pid in text and c.value.lower() in text[c.pid]:
            bad.append(f"{c.pid}.{c.field} = {c.value!r} ({'unverified' if c.status != 'VERIFIED' else visibility(c.pid, c.field)})")
    return bad


TOOL_SCHEMA = {
    "name": "search_professionals",
    "description": "Find professionals whose own words match a role. Returns only fields they chose to share with your audience, each with a quote and timestamp from their interview.",
    "input_schema": {"type": "object", "properties": {
        "query": {"type": "string", "description": "e.g. 'remote backend engineer with Go and Postgres'"},
        "k": {"type": "integer", "default": 3}}, "required": ["query"]},
}
