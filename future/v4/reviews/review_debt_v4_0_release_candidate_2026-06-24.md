# Review Debt: V4.0 Release Candidate

Date: 2026-06-24

Status: enumerated release-candidate review debt, not release authorization.

## Why This Debt Exists

The engineering candidate has fresh POD validation, but the user's release rule
requires external review before any release decision. This file makes the open
review debt explicit so `v4_review_debt_open` is resolvable rather than a
phantom blocker.

Antigravity CLI was checked in non-interactive `--print` mode on 2026-06-24. A
minimal health-check prompt exited successfully but returned empty output, so it
was not treated as an available external reviewer for this release decision.

## Debt Tracker

| ID | Debt | Status | Close Or Waive Condition |
| --- | --- | --- | --- |
| D1 | External release-candidate review | `closed` | Closed by `future/v4/reviews/claude_v4_0_release_candidate_recorded_review_2026-06-24.md` and follow-up closure review. |
| D2 | Antigravity non-interactive reviewer unavailable | `tool_unavailable` | Waived only if the release decision record explicitly states that Antigravity CLI unavailability is not required for V4.0 because Claude review plus internal multihead review were obtained. |
| D3 | Internal multihead amendments | `closed` | Closed by `future/v4/reviews/internal_multihead_v4_release_candidate_amendments_2026-06-24.md`, `future/v4/reviews/internal_multihead_v4_release_candidate_amendment_closure_review_2026-06-24.md`, and passing local/POD gates. |
| D4 | Claude C-1 review-debt enumeration | `closed` | Closed by this tracker. |
| D5 | Claude C-2 clean-commit rerun protocol | `closed` | Closed by `future/v4/release_rerun_protocol_2026-06-24.md`. |
| D6 | Claude M-1 grouped-argmin true-zero-copy explanation | `closed` | Closed by `future/v4/ray_triangle_device_array_frontdoor.md` and `future/v4/README.md`. |
| D7 | Claude M-2 CuPy planner hardening | `closed` | Closed by `src/rtdsl/v4_operator_catalog.py` returning no V4.0 `api_surface` for `partner="cupy"` and by passing tests. |
| D8 | Claude L-1 per-example forbidden-claim gate checks | `closed` | Closed by `scripts/v4_catalog_regression_gate.py` checking forbidden claim flags and by passing tests. |
| D9 | Claude follow-up low-severity recursive claim-flag hardening | `closed` | Closed by recursive forbidden-claim checks, the negative regression test, and local/POD gates passing on `50af025033660a40fa0041996ff68d5b80a7325d`. |

## Waiver Definition

A waiver is not implicit. To waive any open debt, the release decision record
must name the debt ID, state that it is not required for V4.0, give the reason,
and preserve the non-authorization boundaries for V4.x items.

## Required Review Packet

- `future/v4/reviews/call_for_review_v4_0_release_candidate_2026-06-24.md`

## Current Candidate Evidence

- Candidate packet: `future/v4/v4_0_release_candidate_packet_2026-06-24.md`
- Clean-commit rerun protocol: `future/v4/release_rerun_protocol_2026-06-24.md`
- Claude review: `future/v4/reviews/claude_v4_0_release_candidate_review_2026-06-24.raw.md`
- Claude amendment-closure review: `future/v4/reviews/claude_v4_0_release_candidate_amendment_closure_recorded_review_2026-06-24.md`
- Internal multihead amendments: `future/v4/reviews/internal_multihead_v4_release_candidate_amendments_2026-06-24.md`
- Internal amendment-closure review: `future/v4/reviews/internal_multihead_v4_release_candidate_amendment_closure_review_2026-06-24.md`
- Scope gate: `future/v4/evidence/v4_scope_gate_2026-06-24.json`
- Final GPU catalog gate, serious size: `future/v4/evidence/v4_final_release_scope_catalog_gate_gpu_32768_2026-06-24.json`
- Final GPU catalog gate, smoke size: `future/v4/evidence/v4_final_release_scope_catalog_gate_gpu_2026-06-24.json`
- Tier-3 PTX spike: `future/v4/evidence/v4_tier3_numba_ptx_probe_2026-06-24.json`
- Tier-3 module-link blocked spike: `future/v4/evidence/v4_tier3_optix_module_link_probe_2026-06-24.json`

## Non-Authorization

This debt record does not authorize V4 release, broad V4 speedup wording,
whole-application speedup wording, Tier-3 callback/PTX support claims, raw OptiX
callback support, CuPy performance claims, embedding/C-ABI claims, non-Python
host binding claims, or app-specific native engine kernels.
