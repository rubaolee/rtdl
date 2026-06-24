# Phoenix V3 M18 Triangle Runner Harness Second Review

Date: 2026-06-22

Reviewer: Bernoulli

Verdict: `revise_m18_harness`

## Explicit Authorization State

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
third_strict_set_a_material_probe_closed: false
```

## Findings

P1: M18 still did not fail closed on the full M17 correctness bar. M17
requires all three variants to match `oracle_triangle_count=320000`, but the
M18 `failure_checks` path checked only the productized runner oracle status.
Synthetic mismatched control payloads could return no failed checks when the
runner and speed bars passed.

P1: M17 requires the K4 80,000-clique edge file to be generated once and
checksummed before variants run. M18 generated the file if missing, but recorded
no checksum, so the focused POD command could use a stale or different existing
file without evidence.

## Explicit Answers

- Does the revision close the initial hot-path scalar materialization blocker?
  yes.
- Is the harness sufficient for exactly one focused Triangle POD run now? no.
- Is focused POD authorized now? no.
- Is all-app POD authorized now? no.
- Is release authorized? no.
- Is public speedup wording authorized? no.
- Is broad V3-over-V2 wording authorized? no.
- Does Triangle become the third strict Set-A material probe now, before POD
  evidence? no.

## Required Before Focused POD

- Add fail-closed oracle checks for Embree and legacy controls.
- Add edge-file checksum recording and enforcement before variants run.
- Add tests for both.
- Rerun the 55-test M16/M17/M18 gate, wording gate, `py_compile`, dry-run, and
  true-authorization scan.

## Goal-Level Decision Audit

Decision: accept `revise_m18_harness`, keep POD blocked, and fix the two P1
fail-closed issues before resubmitting.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   It would be foolish to run POD while control-route correctness and edge-file
   identity are not fail-closed.
3. Was there another path?
   Yes: ignore the review and run the focused POD. That would produce evidence
   that may not measure the required row or controls.
4. Can I now try a different path?
   Yes. Make the harness fail closed on all three oracle checks and on exact
   K4 edge-file identity, then request a new 2-AI verdict.
