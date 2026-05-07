# Goal1461 v1.5.3 Reduced-Copy Contract

## Verdict

Defined the first v1.5.3 reduced-copy contract for the Python+RTDL track. The
typed contiguous host input-buffer path and wrapper-level copy-count measurement
are now present, while backend parity where claimed, external review, and public
claims remain pending.

## Scope

- Typed contiguous host buffers.
- Preallocated result buffers.
- Prepared host-buffer reuse.
- Prepared device or staging-buffer reuse.

## Required Evidence

- Python materialized rows baseline.
- Typed contiguous host-buffer path.
- Preallocated result-buffer reuse path.
- Copy-count or transfer-count measurement.
- Embree/OptiX same-contract parity where claimed.
- External AI review before public claims.

## Current Status

Satisfied evidence:

- Python materialized rows baseline.
- Typed contiguous host-buffer path.
- Preallocated result-buffer reuse path.

Missing evidence:

- Copy-count or transfer-count measurement.
- Embree/OptiX same-contract parity where claimed.
- External AI review before public claims.

## Boundary

This goal does not authorize true zero-copy wording, public speedup wording,
whole-app claims, stable primitive promotion, partner tensor handoff, or release
action. The allowed wording is limited to reduced-copy or reduced-transfer
candidate language until measurement and review exist.

## Validation

Run:

```bash
PYTHONPATH=src:. python -m unittest tests.goal1461_v1_5_3_reduced_copy_contract_test
```
