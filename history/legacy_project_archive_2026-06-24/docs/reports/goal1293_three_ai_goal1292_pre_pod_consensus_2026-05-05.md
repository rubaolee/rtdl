# Goal1293 Three-AI Goal1292 Pre-Pod Consensus

Date: 2026-05-05

## Scope

This consensus reviews whether Goal1292 is ready to run on an NVIDIA RTX pod
before further v1.5 local engineering.

Reviewed packet:

- `docs/reports/goal1292_v1_5_generic_optix_evidence_packet_2026-05-05.md`
- `docs/reports/goal1292_v1_5_generic_optix_evidence_packet_2026-05-05.json`
- `scripts/goal1292_v1_5_generic_optix_evidence_packet.py`
- `scripts/goal1292_v1_5_generic_optix_evidence_runner.py`
- `tests/goal1292_v1_5_generic_optix_evidence_packet_test.py`

Project boundaries:

- Active v1.5 backends remain Embree plus OptiX.
- Vulkan, HIPRT, and Apple RT remain frozen for new implementation work before
  v2.1.
- NVIDIA RT performance is the priority, but public speedup wording remains
  forbidden until a separate evidence and wording review.
- Goal1292 is internal evidence plumbing only, not a public release gate.

## Review Inputs

- Codex implementation review: Goal1292 committed and pushed at `dd89f68`;
  focused test passed 4 tests OK; `py_compile` passed; combined v1.5/v1.4
  focused regression passed 120 tests OK.
- Gemini external review:
  `docs/reports/goal1293_gemini_external_review_goal1292_pre_pod_2026-05-05.md`
  with verdict `ACCEPT` and no blocking issues.
- Claude external review:
  `docs/reports/goal1293_claude_external_review_goal1292_pre_pod_2026-05-05.md`
  with verdict `ACCEPT_WITH_NON_BLOCKING_NOTES` and no blocking issues.

## Consensus

Codex, Gemini, and Claude agree that Goal1292 is safe and useful to run on an
RTX pod before further local engineering.

The packet is sufficient for the next internal evidence run because it captures:

- pod environment facts before failure interpretation;
- CPU oracle rows for the generic primitive fixture;
- Embree/OptiX direct generic `ANY_HIT` plus `COUNT_HITS` results when the
  backend is available;
- OptiX prepared `COUNT_HITS` timing with first/mean/min repeated query times;
- graph visibility wrapper repeated-query timing through the existing
  `--visibility-query-repeats 100` path;
- explicit non-public claim boundaries and frozen-backend boundaries.

## Notes

- Claude noted that the generated packet initially recorded the previous commit
  because it was generated before the Goal1292 commit. The packet was
  regenerated after review and now records current HEAD `dd89f68`.
- Gemini and Claude could not read `/Users/rl2025/refresh.md` from their
  restricted review workspaces. Codex verified the refresh anchor locally.
- Claude suggested future hardening for graph app JSON output via an explicit
  output-file option instead of shell redirection. This is non-blocking because
  the current graph CLI prints one JSON payload and Goal1292 only uses the
  OptiX visibility summary path.
- Claude noted that the graph CLI still lists `vulkan` as a backend. This is
  non-blocking for Goal1292 because the pod packet invokes only `--backend
  optix`, and the generic primitive API already rejects frozen backends before
  v2.1. A future cleanup may add a CLI-level freeze guard.

## Decision

`ACCEPT`

Goal1292 is accepted as the 3-AI pre-pod gate. The next action may be to run
the Goal1292 packet commands on an RTX pod and copy back:

`docs/reports/goal1292_v1_5_generic_optix_pod_results/`

This consensus does not authorize public speedup wording, public release
claims, whole-app speedup claims, or new Vulkan/HIPRT/Apple RT implementation
before v2.1.
