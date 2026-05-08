# Goal 1503: OptiX COLLECT_K_BOUNDED Local Status

## Verdict

Local follow-up after the final NVIDIA pod run is evidence-preserving only. It
does not add new NVIDIA measurements or new public claims.

## Current Measured Scope

- Primitive: experimental `COLLECT_K_BOUNDED`.
- Backend path: OptiX row_width=2 device-pointer bridge.
- Measured hardware: NVIDIA RTX 4000 Ada Generation.
- Final measured commit: `0ef25617af5ee656f9d7933794fc13a750095b9c`.
- Final evidence commit: `01d03a66`.
- Final scaling artifact:
  `docs/reports/goal1503_v1_5_4_optix_collect_k_scaling_probe_2026-05-08.md`.

The final 9-repeat artifact records parity-clean measured cases through
`131072` candidates. The highest measured median in that artifact is
`189.755149` ms for `131072` candidates.

## Local Hardening Added

`tests/goal1503_v1_5_4_optix_collect_k_scaling_evidence_test.py` now guards the
committed Goal1503 artifact. The gate checks:

- the report remains parity-clean;
- every claim flag remains false;
- the report still covers key bounded row_width=2 counts through `131072`;
- tiled cases keep the expected path label;
- the final artifact does not accidentally regress to fallback-shaped timings.

The timing guard is an internal evidence-shape check only. It is not public
speedup wording and does not authorize speedup, whole-app, true-zero-copy,
partner handoff, stable primitive, or release claims.

## Next Pod Work

When NVIDIA hardware is available again, the next useful pod-backed work is:

- run a dedicated overflow/fail-closed probe for the tiled row_width=2 path;
- decide whether to extend the same bounded merge-tree path beyond `131072`;
- measure any extension from an exact git commit and commit the generated
  evidence artifacts;
- request external review before changing the experimental status or public
  wording.

