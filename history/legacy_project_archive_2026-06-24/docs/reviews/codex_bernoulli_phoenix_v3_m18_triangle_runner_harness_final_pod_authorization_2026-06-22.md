# Phoenix V3 M18 Triangle Runner Harness Final POD Authorization

Date: 2026-06-22

Reviewer: Bernoulli

Verdict: `accept_m18_authorize_one_focused_triangle_pod`

## Authorization Scope

```text
focused_triangle_pod_authorized_now: true
authorized_run_count: 1
authorized_command_scope: documented M18 command only
hard_cap: 2 h / $0.50
all_app_pod_authorized: false
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
third_strict_set_a_material_probe_before_pod_evidence: false
```

## Reviewer Findings

No remaining P1 blockers were found.

The second-review P1 blockers are closed:

- control-route oracle checks now fail closed for Embree and legacy controls;
- edge-file identity is checksummed and enforced before real variants.

The initial hot-path scalar materialization blocker also remains closed.

## Operational Constraints

- Run exactly one focused Triangle POD job.
- Use the documented command with `--require-rt-hardware` and
  `--generate-edge-file`.
- Preserve the M17/M18 success bars.
- Stop on any failed check.
- Do not treat the run as release, all-app, public speedup, or broad
  V3-over-V2 authorization.

## Verification Cited By Reviewer

```text
58 focused tests OK
4 release-readiness tests OK
release wording gate pass
py_compile OK
dry-run failed_check_count=0
dry-run variant_count=3
dry-run edge_file_preflight_status=dry_run_not_required
bad edge identity fails before variants
control oracle mismatch fails closed
```

## Goal-Level Decision Audit

Decision: spend POD on exactly one focused Triangle M18 run under the reviewed
authorization.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   It would be foolish to expand this authorization into repeated runs,
   all-app runs, or release/public speedup claims.
3. Was there another path?
   Yes. Continue local-only harness work, but the reviewed blocker for one
   focused run is now closed.
4. Can I now try a different path?
   Yes. Run exactly one documented focused POD job, capture raw evidence, and
   return to 2-AI review before any broader spend or claim.
