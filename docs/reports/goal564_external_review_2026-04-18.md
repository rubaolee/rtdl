# Goal 564: v0.9 Release-Candidate Flow Audit — External Review

Date: 2026-04-18

Reviewer: Claude Sonnet 4.6 (external review pass)

## Verdict

ACCEPT

## Evidence Examined

- `docs/reports/goal564_v0_9_release_candidate_flow_audit_2026-04-18.md`
- `docs/release_reports/v0_9/README.md`
- `docs/release_reports/v0_9/support_matrix.md`
- `docs/reports/goal562_hiprt_correctness_matrix_linux_2026-04-18.json`
- `docs/reports/goal562_hiprt_backend_perf_compare_linux_2026-04-18.json` (header/summary spot-check)
- `docs/reports/goal562_external_review_2026-04-18.md`
- `docs/reports/goal563_external_review_2026-04-18.md`

## Findings

### Goal and review ledger

The audit lists 27 goals (537–563) each with a report and external-style review.
The machine-check field reports `missing_or_unclear []`, meaning no gaps were
found at audit time. The ledger is internally consistent with the scope of a v0.9
HIPRT release candidate.

### HIPRT correctness matrix (JSON spot-check)

`goal562_hiprt_correctness_matrix_linux_2026-04-18.json` was read in full.
All 18 entries carry `"status": "PASS"` and `"parity": true`. The summary block
`{"fail": 0, "hiprt_unavailable": 0, "not_implemented": 0, "pass": 18}` matches
the per-entry data exactly. No discrepancies found.

### Cross-backend smoke matrix

The `goal562_hiprt_backend_perf_compare_linux_2026-04-18.json` header confirms
`repeats: 1`, four backends (hiprt, embree, optix, vulkan), and a correctly
scoped `honesty_boundary` field. The Goal 562 external review confirms 72 entries
all `PASS` with `parity_vs_cpu_reference: true`; that review is accepted and its
findings are consistent with the JSON structure.

### Pre-release test gate (Goal 562)

232 tests pass on both macOS and the Linux backend host. Goal 562 external review
is ACCEPT with no conditions.

### Documentation audit (Goal 563)

Goal 563 external review confirmed that stale HIPRT preview wording was removed,
all public docs state v0.8.0 as current release and HIPRT as an active v0.9
candidate, and no broken local links were found.

### Release-candidate package

`docs/release_reports/v0_9/README.md` and `support_matrix.md` exist, are
current, and the status line reads "active candidate, not released as `v0.9.0`".
Platform boundaries (Linux NVIDIA GTX 1070, CUDA/Orochi mode, no AMD GPU
validation, no RT-core speedup claim) are explicitly stated.

### Honesty of known-boundaries section

The audit's "Known Boundaries" list correctly documents: no final release action
from this audit alone, NVIDIA-only validation, GTX 1070 has no RT cores,
performance not leading on small cold-start fixtures, `prepare_hiprt` narrower
than `run_hiprt`, and smoke-only performance comparison. No overclaiming was
found anywhere in the examined artifacts.

## Conditions

None. The flow audit is accurate, the evidence chain is coherent, and all stated
boundaries are explicitly documented.

## Release Decision

The v0.9 HIPRT candidate is ready for user-controlled release authorization.
This review does not itself authorize or perform the `v0.9.0` tag or publish
action; that remains a separate explicit user decision.
