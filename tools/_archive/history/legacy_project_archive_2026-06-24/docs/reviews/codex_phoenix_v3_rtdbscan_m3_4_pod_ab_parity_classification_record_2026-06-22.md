# Codex Record: Phoenix V3 RTDBSCAN M3.4 Pod A/B Parity Classification

Date: 2026-06-22
Status: `codex_record_external_review_blocked_parity_not_release`

## Evidence

```text
report: docs/reports/phoenix_v3_rtdbscan_repeated_runner_route_m3_4_pod_ab_2026-06-22.md
summary: docs/rebuild/v3/evidence/phoenix_v3_rtdbscan_m3_4_pod_ab_20260622_204719/summary.json
```

## Classification

```text
m3_4_rtdbscan_repeated_runner_parity_not_material_not_release
```

Controlling values:

```text
geomean_runner_vs_legacy_speedup: 0.997557675600175
geomean_runner_vs_embree_speedup: 2.941644953697829
legacy_parity_recovered: true
material_set_a_candidate: false
runner_metadata_present_all_runner_samples: true
runner_repeated_execution_all_runner_samples: true
all_claim_flags_false: true
```

Codex accepts the parity classification because the relevant incumbent is the
legacy OptiX grouped-stream route, not Embree. The runner-vs-Embree result is
useful as a control, but it cannot be used as the material Set-A decision.

## Engineering Decision

Stop RTDBSCAN as the immediate second productized-path Set-A material probe.

Redirect Phoenix V3 performance work to:

```text
AABB runner generalization
productized typed continuation runner
device-resident internal phase contract
```

Preferred next action:

```text
AABB runner generalization
```

because AABB M2.1 is already the first material productized-path focused win.

## External Review State

Claude review was attempted once and timed out without substantive output:

```text
docs/reviews/external_ai_blocked_phoenix_v3_rtdbscan_m3_4_pod_ab_parity_classification_2026-06-22.md
```

This is not fresh 2-AI release consensus.

Existing Claude review still applies to the route contract and pod-authorization
boundary:

```text
docs/reviews/claude_phoenix_v3_rtdbscan_repeated_runner_route_m3_4_review_2026-06-22.md
```

## Boundary

This record does not authorize:

```text
release
public speedup claim
broad V3 faster than V2 claim
full all-app pod rerun
RTDBSCAN paper reproduction claim
V4 / C ABI / embedding work
```

Phoenix V3 remains:

```text
redo_required
```

## Goal-Level Decision Audit

Decision: accept M3.4 as parity/non-material evidence and redirect away from
RTDBSCAN as the immediate second material-probe path while recording the fresh
external review timeout.

1. Was I foolish?
   No. The decision follows the preregistered threshold and does not misuse the Embree control as the incumbent comparison.
2. If yes, what actions made the decision foolish?
   The foolish action would have been to claim a material win from `runner_vs_embree = 2.94x` while ignoring `runner_vs_legacy = 0.9976x`.
3. Was there another path that avoids being stuck on a foolish idea?
   Yes. Stop RTDBSCAN micro-tuning after parity and shift to a reusable mechanism with stronger evidence leverage.
4. Can I now try a different path that truly solves the problem?
   Yes. AABB runner generalization is the next concrete generic-runtime path toward a second material Set-A probe.
