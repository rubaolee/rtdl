# Goal919 Codex Review

Date: 2026-04-25

Verdict: ACCEPT

I independently checked the promotion against the repository state and the
artifact digest:

- The RTX artifact is real RTX evidence for the bounded prepared count-summary
  path: `copies=20000`, `event_count=120000`, `hotspot_count=99999`, with
  separated `optix_prepare`, `optix_query`, and `python_postprocess` phases.
- The new Goal919 Embree baseline is same-scale: `copies=20000`,
  `iterations=3`, `event_count=120000`, `hotspot_count=99999`, and
  `summary_sha256=35666dd007dfa50658cfb7e1d472ff804571c5128b5c6bf4ffc14b613facc976`.
- A local JSON comparison verified exact hotspot-list parity between the RTX
  artifact and the same-scale Embree baseline.
- The matrix and docs promote only the bounded prepared count-summary path.
  Neighbor-row output, whole-app hotspot analytics, and public speedup claims
  remain explicitly excluded.

Focused verification passed 47 tests plus `py_compile` and `git diff --check`.
