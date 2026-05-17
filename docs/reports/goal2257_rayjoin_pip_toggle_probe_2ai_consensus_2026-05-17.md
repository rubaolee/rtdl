# Goal2257: RayJoin PIP Toggle Probe 2-AI Consensus

Status: accepted with boundary.

## Scope

This consensus covers Goal2255, a diagnostic probe of the current prepared
closed-shape PIP path on the RayJoin same-query stream.

## Evidence

- Report:
  `docs/reports/goal2255_rayjoin_pip_toggle_probe_2026-05-17.md`
- Default artifact:
  `docs/reports/goal2255_rayjoin_pip_toggle_default_pod_2026-05-17.json`
- No-prefilter artifact:
  `docs/reports/goal2255_rayjoin_pip_toggle_no_prefilter_pod_2026-05-17.json`
- No-one-pass artifact:
  `docs/reports/goal2255_rayjoin_pip_toggle_no_one_pass_pod_2026-05-17.json`
- Gemini review:
  `docs/reviews/goal2256_gemini_review_goal2255_rayjoin_pip_toggle_probe_2026-05-17.md`

## Consensus

Codex verdict: `accept-with-boundary`.

Gemini independent review verdict: `accept`.

Consensus verdict: `accept-with-boundary`.

Accepted diagnostic interpretation:

- default prepared closed-shape PIP median: `0.06666836328804493` seconds;
- disabling device prefilter median: `0.5072881113737822` seconds, about
  `7.61x` slower;
- disabling one-pass compact median: `0.09405476413667202` seconds, about
  `1.41x` slower.

The device-side predicate prefilter is the dominant current control, and
one-pass compact output also materially helps.

## Boundary

This consensus is diagnostic only. It does not authorize RayJoin reproduction
claims, RTDL-beats-RayJoin claims, broad PIP speedup claims, or v2.0 release readiness.
