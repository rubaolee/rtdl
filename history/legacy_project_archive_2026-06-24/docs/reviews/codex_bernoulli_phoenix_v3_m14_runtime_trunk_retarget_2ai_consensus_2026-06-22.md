# Codex + Bernoulli 2-AI Consensus: Phoenix V3 M14 Runtime-Trunk Retarget Status

Date: 2026-06-22
Status: `accept_m14_need_third_strict_probe`

This consensus records the M14 status-gate review. It is not a release
authorization and authorizes no POD spend.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
focused_pod_spend_authorized_now: false
```

## Inputs

- Call for review:
  `docs/reviews/call_for_review_phoenix_v3_m14_runtime_trunk_retarget_status_2026-06-22.md`
- M14 JSON:
  `docs/rebuild/v3/phoenix_v3_m14_runtime_trunk_retarget_status_2026-06-22.json`
- M14 report:
  `docs/reports/phoenix_v3_m14_runtime_trunk_retarget_status_2026-06-22.md`

Local gates before review:

```text
M14 JSON parse: OK
M14 claim-boundary scan: OK
Focused evidence regression tests: 14 tests OK
```

## Bernoulli Verdict

Bernoulli returned verdict `accept_m14_need_third_strict_probe`.

Authorizations and classifications:

- release authorization: no
- public speedup authorization: no
- all-app POD authorization: no
- focused POD authorization: no
- Barnes-Hut counts as material runtime-trunk Set-A evidence: yes, narrowly
- RTNN counts as material runtime-trunk Set-A evidence: yes
- Hausdorff counts as material runtime-trunk Set-A evidence: no

Bernoulli's rationale: M14 is conservative and mostly accurate, but Hausdorff
is positive focused runner-backed evidence, not a strict third material Set-A
close. Its runner-vs-legacy gains are too small for that role, so Phoenix
should select a third stricter Set-A family, likely Triangle or another unfaked
material probe, before preparing the all-app precondition protocol.

## Codex Position

Codex accepts Bernoulli's verdict.

Barnes-Hut and RTNN may be counted as material runtime-trunk Set-A evidence
under the recorded boundaries:

- Barnes-Hut: productized trunk carries the real fused high-performance route
  at parity; do not claim the wrapper is faster than the existing fused route.
- RTNN: productized trunk improves legacy cold-plus-query and runner-wall
  metrics at serious repeat50 scale with signature parity.

Hausdorff remains positive focused runner-backed evidence, but not the strict
third material Set-A probe because runner-vs-legacy gains are small.

## Consensus

Decision: `accept_m14_need_third_strict_probe`

- Do not prepare all-app protocol yet.
- Do not run all-app POD.
- Do not run focused POD immediately.
- Select a third stricter Set-A material probe locally first.
- Candidate priority starts with Triangle, unless local audit shows it lacks a
  real physical runtime source.

## Next Controlled Work

M15 should be local:

1. Audit Triangle and any alternative Set-A candidates for a real reusable
   runtime-trunk performance source.
2. Choose the best third strict Set-A probe by written criteria.
3. Produce call-for-review before any POD.
4. Only after 2-AI approval should a focused POD A/B be run.

## Goal-Level Decision Audit

Decision: require a third strict Set-A material probe before all-app protocol.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   The foolish action would be counting Hausdorff's small runner-vs-legacy
   gains as a strict third material probe and moving toward all-app too soon.
3. Was there another path?
   Yes: prepare all-app protocol immediately. That would repeat the earlier
   blended-score failure pattern before the focused runtime-trunk case is
   strong enough.
4. Can I now try a different path?
   Yes: audit Triangle or another Set-A family for a real runtime source and
   seek review before any new POD.
