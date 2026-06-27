# 3-AI Consensus: Goal 1600 v1.6 Python+RTDL Readiness Gate

## Verdict

Consensus is reached.

Goal 1600 is accepted as a mechanical readiness and blocked-claim guard for the
accepted `v1.6` Python+RTDL planning boundary.

This consensus does not authorize a `v1.6` release, stable
`COLLECT_K_BOUNDED` promotion, public speedup wording, whole-app speedup
wording, broad RTX/GPU acceleration wording, true zero-copy wording, partner
support claims, package-install claims, or release-tag action.

## Reviewed Artifacts

- Gate implementation:
  `src/rtdsl/v1_6_python_rtdl_readiness.py`
- Gate tests:
  `tests/goal1600_v1_6_python_rtdl_readiness_gate_test.py`
- Codex report:
  `docs/reports/goal1600_v1_6_python_rtdl_readiness_gate_2026-05-09.md`
- Claude review:
  `docs/reviews/goal1600_v1_6_readiness_gate_claude_review_2026-05-09.md`
- Gemini review:
  `docs/reviews/goal1600_v1_6_readiness_gate_gemini_review_2026-05-09.md`

## Consensus Positions

Codex position:

The Goal 1599 `v1.6` planning boundary is now encoded in a
machine-checkable gate. The gate keeps `v1.6` at
`planning_boundary_accepted_not_release_ready`, keeps `COLLECT_K_BOUNDED`
pending, and keeps all public claim and release-action authorization flags
false.

Claude position:

Claude returned `ACCEPT` as a mechanical readiness/blocked-claim guard only.
Claude confirmed that every required blocked claim has a constant entry and a
matching false authorization flag, that `COLLECT_K_BOUNDED` is triple-locked
as pending/not stable, and that the tests bind the gate to the accepted Goal
1599 report and consensus artifacts.

Gemini position:

Gemini approved the gate as accurately encoding the `planning_boundary_accepted_not_release_ready`
status. Gemini highlighted the backend scope, stable primitive boundary,
pending `COLLECT_K_BOUNDED` status, defensive false authorization flags, and
tests that validate both the Python gate and the foundational report text.

## Accepted Boundary

The accepted guard protects these facts:

- `v1.6` is not release-ready.
- The track is Python+RTDL, not Python+partner+RTDL.
- The supported closure backends are Embree and OptiX.
- The stable primitive boundary remains `ANY_HIT`, `COUNT_HITS`,
  `REDUCE_FLOAT(MIN|MAX|SUM)`, and `REDUCE_INT(COUNT|SUM)`.
- `COLLECT_K_BOUNDED` remains pending unless a separate reviewed gate promotes
  it.
- Public speedup, whole-app speedup, broad RTX/GPU acceleration, true
  zero-copy, partner support, package-install support, and release-tag action
  remain blocked.

## Validation

Windows focused gate test:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal1600_v1_6_python_rtdl_readiness_gate_test
```

Result:

- `Ran 4 tests`
- `OK`

Windows adjacent docs/classification slice:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal1600_v1_6_python_rtdl_readiness_gate_test `
  tests.goal1509_v1_5_4_app_technical_docs_test `
  tests.goal1510_v1_5_4_non_pod_app_classification_test
```

Result:

- `Ran 17 tests`
- `OK`

## Decision

Accept Goal 1600 as the local blocked-claim regression guard for `v1.6`
planning.

Proceed next to the formal `v1.6` release-surface proposal.

Do not publish `v1.6` yet.
