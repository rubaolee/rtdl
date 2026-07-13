# Goal4941 Layer 2 Numba Columnar Continuations

Date: 2026-07-04

## Verdict

`completed_layer2_generic_numba_columnar_continuations__no_speedup_claim`

Goal4941 starts the Layer 1/2 line after stopping the Layer 3 Python path-split
writer route in Goal4940.

It implements the first Layer 2 slice: generic Numba CUDA continuations for
numeric columnar map/filter work that had previously existed only as RayJoin
paper-app private helpers.

## Historical Reuse Audit

The user's memory was correct: similar ideas existed before. Goal4941 does not
start from scratch.

Relevant prior work:

- v2.5 partner-continuation protocol and `numba_partner_continuation.py` already
  define the right front-door shape for explicit Numba continuations. Goal4941
  extends that existing mechanism instead of inventing a parallel API.
- Goal4897 / Goal4899 had RayJoin app-layer Numba helpers for midpoint
  generation, consecutive point dedupe, chain-intersection membership, and
  writer skip planning. Those were useful, but app-local and RayJoin-shaped.
- Goal4930 classified structure assembly as the dominant writer bottleneck and
  reprojection/sort/dedupe as a secondary Layer 2 target.
- Goal4939/4940 implemented and tested a generic path-split/output assembly
  prototype. Goal4940 proved that the host-columnar Python materializer is
  semantically correct but too slow, so this goal avoids continuing Layer 3.
- V3/V4-era device-column and hit-stream experiments exist historically, but
  this goal does not revive V3/V4 release claims. It uses only the current v2.x
  partner-continuation front door.

## Implementation

Added three generic Numba preview operations:

1. `adjacent_midpoint_candidates_i64x2_by_key`
   - Inputs: `keys:int64`, `values_x:int64`, `values_y:int64`
   - Outputs: `mid_x:int64`, `mid_y:int64`, `left_indices:int64`,
     `valid_mask:bool`
   - Contract: rows are already sorted by key; adjacent rows with the same key
     produce truncating integer midpoints.

2. `consecutive_dedupe_mask_f64x2`
   - Inputs: `values_x:float64`, `values_y:float64`
   - Output: `keep_mask:bool`
   - Contract: keep the first row and rows whose exact x/y pair differs from
     the previous row.

3. `range_has_sorted_values_i64`
   - Inputs: `range_starts:int64`, `range_lengths:int64`,
     `sorted_values:int64`
   - Output: `has_value:bool`
   - Contract: each range is half-open `[start, start + length)`; values must
     be sorted in nondecreasing order.

Files changed:

- `src/rtdsl/partner_continuation_protocol.py`
- `src/rtdsl/numba_partner_continuation.py`
- `src/rtdsl/__init__.py`
- `tests/goal4941_layer2_numba_columnar_continuations_test.py`

## Genericity Boundary

These operations are intentionally app-neutral:

- No RayJoin, overlay, polygon, face, author-output, or chain semantics.
- They operate only on typed columns and generic keys/ranges.
- They do not replace RT traversal.
- They do not require user raw kernels.
- They do not authorize speedup or public release claims.

The RayJoin mapping is allowed only as a consumer:

- midpoint generation maps to adjacent same-key midpoint candidates;
- output point dedupe maps to consecutive x/y dedupe;
- chain/intersection membership maps to range-has-sorted-values.

The RTDL core still must not contain RayJoin output-chain semantics.

## Verification

Local:

```text
py -m unittest tests.goal4941_layer2_numba_columnar_continuations_test
Ran 4 tests in 0.004s
OK (skipped=2)
```

Local compile:

```text
py -m py_compile src/rtdsl/numba_partner_continuation.py \
  src/rtdsl/partner_continuation_protocol.py src/rtdsl/__init__.py \
  tests/goal4941_layer2_numba_columnar_continuations_test.py
OK
```

POD:

- Host: `157.157.221.29:24344`
- GPU: NVIDIA RTX 4000 Ada Generation
- Numba installed during this goal because the POD initially lacked it.

```text
python3 -m unittest tests.goal4941_layer2_numba_columnar_continuations_test
Ran 4 tests in 0.841s
OK
```

Large synthetic POD smoke:

- `row_count`: 1,000,000
- `range_count`: 250,000
- artifact: `history/internal_docs/goal4941_pod_artifacts/layer2_numba_continuations_smoke.json`

Observed:

- midpoint valid candidates: `500000 / 500000 expected`
- dedupe keep count: `666667`
- range has-value count: `125000 / 125000 expected`

Representative timings from the synthetic smoke:

| Operation | Rows | Partner Time |
|---|---:|---:|
| `adjacent_midpoint_candidates_i64x2_by_key` | 1,000,000 | 0.251052s |
| `consecutive_dedupe_mask_f64x2` | 1,000,000 | 0.045331s |
| `range_has_sorted_values_i64` | 250,000 ranges | 0.058536s |

These are executable capability timings, not public performance claims.

## Regression Notes

A broad legacy test batch failed because some older tests still reference files
that were moved out of the public tree during the v2.14 cleanup
(`docs/reports/...`, `examples/v2_0/...`). That is an existing historical-test
path issue, not a Goal4941 runtime regression.

The focused Goal4941 tests and compile checks pass locally and on the CUDA POD.

## What This Solves

Goal4941 converts a real part of the RayJoin app-layer Numba work into a generic
RTDL Numba continuation surface.

It is a Layer 2 step:

- generic numeric map/filter work can now be expressed through RTDL's Numba
  continuation front door;
- the operations stay on CUDA device arrays once inputs are device-resident;
- the operations are reusable by non-RayJoin workloads.

## What This Does Not Solve

Goal4941 does not yet complete Layer 1.

It does not create a native RTDL producer that emits these columns device-
resident from LSI/PIP. If the current RayJoin app uploads host NumPy arrays to
call these operations, the transfer cost may erase the gain.

It also does not solve Layer 3 writer structure assembly or text formatting.
Goal4940 already showed that host-columnar Python path splitting is too slow.

## Next Honest Step

If continuing Layer 1/2, the next goal should be:

`Goal4942`: define and prove a generic device-column row-buffer carrier between
an RTDL primitive producer and these Layer 2 continuation operations, preferably
first on a non-RayJoin workload.

That is the real Layer 1 bridge. Without it, Goal4941 is useful capability, but
not a RayJoin hot-path speedup.
