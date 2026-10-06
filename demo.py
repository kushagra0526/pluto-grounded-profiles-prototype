"""python demo.py           -> verifier + leak audit (ours vs naive), writes out/report.html
python demo.py --serve   -> also starts the agent HTTP endpoint on :8765"""
from __future__ import annotations

import json
import sys
from html import escape
from pathlib import Path

from ctxlayer import data
from ctxlayer.layer import leaks, load_claims, naive_search, profile, search

HERE = Path(__file__).parent
QUERIES = ["remote backend engineer with Go and Postgres", "python pytorch evals", "kubernetes platform manager",
           "remote data engineer snowflake", "remote full stack typescript graphql", "founding designer figma react"]
CSS = """
:root{--bg:#f8f8f6;--fg:#1b1b19;--mut:#6c6a64;--line:#e3e1db;--card:#fff;--ok:#1d7a4f;--bad:#c2412d}
@media (prefers-color-scheme:dark){:root{--bg:#121211;--fg:#ecebe6;--mut:#9a978f;--line:#2b2a27;--card:#1a1a18;--ok:#58c08d;--bad:#ef7a66}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,sans-serif}
main{max-width:1180px;margin:0 auto;padding:30px 16px}h1{font-size:25px;margin:0}h2{font-size:17px;margin:26px 0 10px}.mut{color:var(--mut)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:20px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:13px}.kpi b{display:block;font-size:26px}
.scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line)}
th,td{text-align:left;padding:8px 9px;border-bottom:1px solid var(--line);vertical-align:top}th{font-size:11px;text-transform:uppercase;color:var(--mut)}
.ok{color:var(--ok);font-weight:700}.bad{color:var(--bad);font-weight:700}pre{white-space:pre-wrap;font:12px ui-monospace,monospace;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px}
"""


def main():
    claims = load_claims()
    bad = [c for c in claims if c.status != "VERIFIED"]
    print(f"\n{len(claims)} claims extracted from {len(data.TRANSCRIPTS)} voice interviews -> {len(bad)} rejected by the verifier")
    for c in bad:
        print(f"  ✗ {c.pid} {c.field:11} {c.value!r:60} — {c.why}")

    rows, ours_total, naive_total = "", 0, 0
    print("\nLeak audit (private or unverified values in responses):")
    for q in QUERIES:
        for aud in ("agent", "company"):
            o = leaks(search(claims, q, aud), aud, claims)
            ours_total += len(o)
            n = leaks(naive_search(claims, q), aud, claims)
            naive_total += len(n)
            rows += (f"<tr><td>{escape(q)}</td><td>{aud}</td><td class={'bad' if o else 'ok'}>{len(o)}</td>"
                     f"<td class={'bad' if n else 'ok'}>{len(n)}</td><td class=mut>{escape('; '.join(n[:3]))}</td></tr>")
        for pid in data.TRANSCRIPTS:
            for aud in ("agent", "company"):
                ours_total += len(leaks(profile(claims, pid, aud), aud, claims))
    print(f"  ours:  {ours_total} leaks across {len(QUERIES) * 2} searches + {len(data.TRANSCRIPTS) * 2} profile reads")
    print(f"  naive: {naive_total} leaks across the same {len(QUERIES) * 2} searches")

    example = search(claims, QUERIES[0], "agent")
    print(f"\nagent query: {QUERIES[0]!r}")
    print(json.dumps(example[0], indent=1, ensure_ascii=False)[:700])

    bad_rows = "".join(f"<tr><td>{c.pid}</td><td>{c.field}</td><td>{escape(c.value)}</td><td class=mut>“{escape(c.quote)}”</td><td class=bad>{escape(c.why)}</td></tr>" for c in bad)
    html = f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Grounded Agent Profiles</title><style>{CSS}</style></head><body><main>
<h1>Grounded, scoped profiles for agents</h1>
<div class=mut>6 synthetic voice interviews · claims checked against the transcript · field-level visibility enforced in search, profiles and quotes · unofficial prototype by Kushagra Pratap Singh</div>
<div class=kpis><div class=kpi><span class=mut>Claims extracted</span><b>{len(claims)}</b></div>
<div class=kpi><span class=mut>Rejected by verifier</span><b class=bad>{len(bad)}</b></div>
<div class=kpi><span class=mut>Leaks — this layer</span><b class=ok>{ours_total}</b></div>
<div class=kpi><span class=mut>Leaks — naive matcher</span><b class=bad>{naive_total}</b></div></div>
<h2>Claims the verifier rejected</h2><div class=scroll><table><tr><th>Who</th><th>Field</th><th>Claim</th><th>Quote cited</th><th>Why</th></tr>{bad_rows}</table></div>
<h2>Leak audit per query</h2><div class=scroll><table><tr><th>Query</th><th>Audience</th><th>Ours</th><th>Naive</th><th>Naive leaked</th></tr>{rows}</table></div>
<h2>Example agent response</h2><pre>{escape(json.dumps(example[0], indent=1, ensure_ascii=False))}</pre>
</main></body></html>"""
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "report.html").write_text(html, encoding="utf-8")
    print(f"\nreport: {HERE / 'out' / 'report.html'}")
    if "--serve" in sys.argv:
        from ctxlayer.server import serve
        serve()


if __name__ == "__main__":
    main()
