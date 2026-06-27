# Goal876 Claude External Review

- reviewer: `Claude`
- date: `2026-04-24`
- verdict: `ACCEPT_WITH_CAVEATS`

## Initial Review

Claude accepted the architecture with caveats.

Accepted points:

- OptiX is used only for LSI/PIP candidate discovery.
- Exact area/Jaccard refinement remains CPU/Python.
- Matrix status is conservative:
  - `direct_cli_native_assisted`
  - `python_interface_dominated`
  - `needs_interface_tuning`
  - `rt_core_partial_ready`
- No cloud-run authorization or full RTX speedup claim is made.

Initial caveat:

- Top-level `rt_core_accelerated: true` for OptiX was too broad because the
  whole app is not accelerated end to end.

## Caveat Fix Review

After the fix, Claude re-reviewed:

- examples now keep `rt_core_accelerated: false`;
- examples add `rt_core_candidate_discovery_active: backend == "optix"`;
- tests assert both fields for mocked OptiX;
- boundary strings remain accurate.

Claude accepted the fix with one minor test-coverage caveat: CPU/non-OptiX
paths should explicitly assert `rt_core_candidate_discovery_active == false`.

## Follow-Up Applied

The test suite now asserts that CPU payloads report
`rt_core_candidate_discovery_active == false` for both polygon apps.

The remaining caveat is expected: real Linux/RTX execution is still required
before performance or end-to-end native OptiX claims.
