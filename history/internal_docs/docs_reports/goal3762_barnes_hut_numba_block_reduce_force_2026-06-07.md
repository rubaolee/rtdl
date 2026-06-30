# Goal3762 Barnes-Hut Numba Block-Reduce Exact-Force Probe

Date: 2026-06-07

## Purpose

Goal3762 hardens the Barnes-Hut benchmark's no-RawKernel Numba reference.
The earlier Goal3746 Numba exact-force implementation was correct, but it was
too close to a direct translation of the CuPy RawKernel shape: one CUDA thread
owned one source body and scanned every target body serially.

This goal tests a more serious Numba partner design while keeping the v2.x
boundary:

- no app-specific native-engine logic;
- no custom CUDA/C++ source required from the user;
- same exact all-pairs force-vector contract as the CuPy RawKernel reference;
- explicit claim boundary: no public speedup, no RT-core, no hierarchical
  Barnes-Hut acceleration, and no release authorization.

## Implementation

`pairwise_inverse_square_force_2d_partner_columns(..., partner="numba")` now
uses a block-per-source target-stride reduction when both source and target
columns have at least 512 rows.

The selected kernel shape is:

- one CUDA block per source body;
- 512 threads per block;
- each thread strides over the target body columns;
- per-thread force partials are reduced in shared memory;
- output is the exact force vector for the source body.

The fallback kernel is retained for tiny cases where a block-reduction launch
shape is not appropriate. The metadata records the selected strategy as
`block_source_target_stride_512_reduce_fastmath_true`.

## Rejected Variants

Exploratory pod probes rejected two simpler ideas before the final packet:

- A shared target-tile serial-source kernel improved some large rows but
  regressed the small row and stayed clearly behind CuPy.
- A 1024-thread block-reduce variant increased parallelism but lost enough
  occupancy and reduction efficiency to underperform the 512-thread variant.

The committed path therefore uses the 512-thread block-reduction strategy.

## A5000 Evidence

Artifact:
`docs/reports/goal3762_barnes_hut_numba_block_reduce_force_a5000/summary.json`

Clean source evidence:

- source commit: `afda1b83`
- GPU: NVIDIA RTX A5000, driver 580.126.09
- scoped source dirty: `false`
- repeat / warmup: 20 / 3
- correctness body count: 256
- correctness: CPU oracle match, max relative error `5.489235176361001e-15`

| Bodies | CuPy RawKernel median sec | Numba block-reduce median sec | Numba vs CuPy |
| ---: | ---: | ---: | ---: |
| 1,024 | 0.005063 | 0.005922 | 0.855x |
| 2,048 | 0.009919 | 0.010402 | 0.954x |
| 4,096 | 0.019897 | 0.020210 | 0.985x |
| 8,192 | 0.039565 | 0.040361 | 0.980x |
| 16,384 | 0.079204 | 0.102273 | 0.774x |

Summary:

- all force row counts match;
- geomean Numba vs CuPy: `0.9056496077835507x`;
- minimum Numba vs CuPy: `0.77444210365911x`.

## Interpretation

This is a real improvement in the Numba reference architecture, not a final
performance victory. The important change is that the Numba reference now
expresses the reduction structure explicitly. That brings the 4096 and 8192
rows near parity with the CuPy RawKernel while preserving the user's
no-RawKernel path.

The remaining gap is also clear: CuPy's hand-written RawKernel still wins
overall, especially at 16384 bodies. For this app, v2.x can provide a credible
Numba reference, but matching or beating custom CUDA consistently likely needs
one of the following future directions:

- a reusable generic grouped vector-reduction primitive in the RTDL runtime;
- a hierarchical force approximation contract rather than exact all-pairs
  force only;
- later v3.x user-defined shader/kernel extension work.

## Claim Boundary

This goal does not authorize release action, public speedup wording, whole-app
acceleration wording, broad RT-core wording, true-zero-copy wording, automatic
partner selection, Barnes-Hut paper reproduction wording, or app-specific
native-engine logic.
