# Codex Self-Review: Phoenix V3 M21 All-App POD Protocol

Status: `codex_self_review_ready_pending_external_verdict`

This is not an external review and does not authorize the all-app POD run. It records the Codex-side technical judgment before the required external verdict.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_run_authorized_now: false
```

## Verdict

`approve_protocol_ready_pending_external_run_authorization`

The M21 protocol is technically complete enough to submit for external authorization. It should not be run unless an external reviewer returns exactly `authorize_m21_one_all_app_pod_run`.

## Basis

The packet now includes the required M20 items:

```text
non-release header
fail-closed bars
frozen case-id whitelist
same RTX 4000 Ada hardware gate
project venv/sys.executable preflight
LibRTS OptiX AABB watch row
all-app correctness/oracle gate
post-run interpretation
resource estimate and hard cap
```

It also adds a dedicated post-run evaluator:

```text
scripts/v3_phoenix_m21_all_app_protocol_gate.py
```

This matters because the older Set-A/B scorecard gate describes the current failed baseline, while M21 needs a future-run verdict gate.

## Validation

Local validation:

```text
23 targeted tests OK
M21 protocol JSON parses
scoped git diff --check clean
v3 release wording gate pass
```

Old baseline check:

```text
scripts/v3_phoenix_m21_all_app_protocol_gate.py returns exit=2 on the old 1.012x summary
status: protocol_fail_invalid_or_out_of_scope
fail bars include Barnes-Hut app geomean and librts_embree_aabb_index
correctness/suite failures are surfaced instead of hidden
```

No-benchmark POD preflight:

```text
ssh/GPU/venv/import check only; no benchmark run
GPU: NVIDIA RTX 4000 Ada Generation
driver: 550.127.05
compute capability: 8.9
python: /root/rtdl_v3_rebuild_20260620/.venv/bin/python
cupy: 14.1.1
numba: 0.65.1
remote bash -n on patched runner: pass
```

## Blocking Boundary

This self-review cannot unlock POD spend. The run remains blocked until the external review file exists and says:

```text
authorize_m21_one_all_app_pod_run
one_all_app_pod_run_authorized: true
max_run_count: 1
```

Any other result means revise protocol, do more focused work, or record blocked-not-release.

## Goal-Level Decision Audit

1. Was I foolish?

No for this decision.

2. If yes, what actions made the decision foolish?

It would be foolish to treat my own self-review as a substitute for external authorization.

3. Was there another path?

Yes: run the all-app POD based on the local packet and three focused probes. That still violates the M20 verdict.

4. Can I now try a different path?

Yes. Keep all-app blocked, retain this as Codex-side review, and wait for Claude or another external reviewer before spending POD time.
