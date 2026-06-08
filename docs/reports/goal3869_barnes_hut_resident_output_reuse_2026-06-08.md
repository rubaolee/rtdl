# Goal3869 Barnes-Hut Resident Output-Column Reuse

Date: 2026-06-08

Status: implemented and A5000-validated.

## Purpose

Goal3869 improves the Barnes-Hut no-RawKernel partner reference path for
resident/repeated exact-force runs. The previous force-summary loop reused the
partner input columns, but each repeated force call still allocated fresh device
output vectors for `force_x` and `force_y`.

This goal adds an optional generic `output_columns` argument to
`pairwise_inverse_square_force_2d_partner_columns(...)` and wires the
Barnes-Hut `force_summary` repeated path to reuse those output vectors after
the first warmup allocation.

The boundary is unchanged:

- no Barnes-Hut logic in the native engine;
- no user RawKernel requirement for the Numba path;
- no RT-core claim for exact all-pairs force continuation;
- no hierarchical Barnes-Hut paper reproduction claim;
- no release or public speedup authorization.

## Implementation

Files:

- `src/rtdsl/app_adapters/barnes_hut.py`
- `examples/v2_0/apps/simulation/rtdl_barnes_hut_force_app.py`
- `scripts/goal3869_barnes_hut_resident_output_reuse_probe.py`

The adapter now accepts:

```python
output_columns: dict[str, object] | None = None
```

For CuPy and Numba, when `output_columns` is provided:

- `force_x` and `force_y` are validated against `source_count`;
- the existing device buffers are overwritten by the same force kernel;
- metadata records `output_columns_reused: true`.

The app-level `force_summary` loop keeps the first result's output buffers and
passes them back on later warmup/repeat iterations. Metadata records
`prepared_force_output_columns_reused: true`.

## Rejected Probe

A symmetric half-pair Numba kernel was probed on the A5000. It computes each
body pair once and applies equal/opposite updates with device atomics. It was
rejected for this goal because:

- it was slower than the current deterministic block-reduction kernel at 4096
  and 8192 bodies;
- atomic floating-point accumulation would create a determinism/tie-break
  policy problem for a public reference path;
- it is not a generic native-engine improvement.

The existing 512-thread block-per-source reduction remains the default Numba
kernel strategy.

## A5000 Evidence

Artifact:

`docs/reports/goal3869_barnes_hut_resident_output_reuse_a5000/summary.json`

Pod:

`ssh root@69.30.85.203 -p 22057 -i ~/.ssh/id_ed25519`

Repository commit:

`539d61ef`

GPU:

`NVIDIA RTX A5000, 580.126.09`

The artifact reports an empty `git_status_short`, scoped source dirty `false`,
all checksum pairs matching, and all claim-boundary flags false.

| Bodies | Partner | No reuse median sec | Reuse median sec | Reuse speedup |
| ---: | --- | ---: | ---: | ---: |
| 8,192 | Numba | 0.008947945 | 0.007698039 | 1.162x |
| 8,192 | CuPy | 0.005581500 | 0.005556141 | 1.005x |
| 16,384 | Numba | 0.029905482 | 0.029724700 | 1.006x |
| 16,384 | CuPy | 0.020477505 | 0.020459296 | 1.001x |

Summary:

- row count: `4`;
- all checksum pairs match: `true`;
- geomean reuse speedup: `1.0413222375434346x`;
- minimum reuse speedup: `1.000890044549569x`.

## Interpretation

This is a useful resident-repeat cleanup, especially for the current 8192-body
Numba scale row, where output reuse improves the warmed adapter timing by about
`1.16x`. It is not an RT-core claim.

It does not close the larger Barnes-Hut performance gap. At 16384 bodies the
all-pairs Numba force kernel remains compute-dominated, and output allocation
reuse only gives a small improvement. This is not a hierarchical Barnes-Hut acceleration path.
The next substantial Barnes-Hut step is not another local
allocation tweak; it is a larger generic runtime direction:

- reusable grouped/vector reduction primitives over resident partner columns;
- a hierarchical approximate-force contract instead of exact all-pairs force
  only;
- or later user-defined kernel/shader extension work.

## Claim Boundary

This goal does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, true-zero-copy wording, automatic
partner selection, paper-reproduction wording, or app-specific native-engine
logic.
