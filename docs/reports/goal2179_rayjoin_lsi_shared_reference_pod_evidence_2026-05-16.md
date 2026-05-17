# Goal2179 RayJoin LSI Shared-Reference Pod Evidence

Date: 2026-05-16

Status: implemented and pod-validated.

## Purpose

The overlay lane showed increasing OptiX-over-Embree gains as CDB slices grew.
Goal2179 checks a different RayJoin-style subproblem: line-segment
intersection on a larger nonzero county/soil slice, including a CuPy RawKernel
CUDA-core brute-force baseline.

The runner was repaired so LSI backends use the same shared CPU Python
reference-row strategy already added for overlay. This prevents repeated
reference recomputation inside each backend repeat and keeps pod time focused
on backend execution.

## Code Change

`scripts/goal2159_rayjoin_public_cdb_runner.py` now has:

- `_run_lsi_direct_backend(...)` for direct CPU/native-oracle, Embree, and OptiX
  LSI timing over loaded segment inputs
- shared LSI CPU Python reference rows reused by direct LSI, prepared OptiX
  LSI, and CuPy RawKernel LSI
- preserved generic RTDL kernel: `county_zip_join_reference`

No native ABI or engine behavior changed.

## Pod Evidence

Pod access:

- `root@157.157.221.29`
- SSH port: `24240`
- Accepted local key: `id_ed25519_rtdl_codex`

Runtime facts inherited from the active RayJoin pod lane:

- GPU: NVIDIA RTX 4000 Ada Generation
- Driver: 580.65.06
- CUDA: 12.8
- OptiX SDK: v8.1.0
- RTDL runner commit: `19a090702c0ea32eee247866743cd44afeb2ede1`

Collected artifact:

- `docs/reports/goal2179_lsi512_shared_reference_pod_2026-05-16.json`

The run used one warmup and three measured repeats on:

- case: `lsi_county256_soil256_count512`
- left segments: 19,987
- right segments: 6,825
- candidate segment pairs: 136,411,275
- emitted intersection rows: 269
- shared CPU Python reference rows: 269, built once in `51.323444` sec

## Result

| Backend | Median sec | Rows | Parity vs CPU Python reference |
| --- | ---: | ---: | --- |
| Embree | 0.201283 | 269 | pass |
| OptiX one-shot | 0.003222 | 269 | pass |
| OptiX prepared LSI | 0.021942 | 269 | pass |
| CuPy RawKernel brute force | 0.040767 | 269 | pass |

Derived ratios:

| Ratio | Value |
| --- | ---: |
| Embree vs OptiX one-shot | 62.472x |
| CuPy brute force vs OptiX one-shot | 12.653x |
| Prepared OptiX vs OptiX one-shot | 6.810x |
| Embree vs prepared OptiX | 9.174x |
| CuPy brute force vs prepared OptiX | 1.858x |

## Interpretation

This row explains an important part of the RayJoin performance story:

- The workload has many candidate segment pairs but only 269 true
  intersections.
- Brute-force CUDA cores still evaluate the broad Cartesian pair space.
- OptiX traversal can reject most non-intersecting geometry through the RT
  acceleration structure, so hot one-shot OptiX is much faster than the CuPy
  brute-force baseline on this sparse-intersection row.

The one-shot OptiX warmup was much slower than hot repeats because it paid
first-use costs. The report therefore treats the hot-repeat median as a
repeated-call measurement, not a cold-start claim.

Prepared OptiX remains faster than Embree and CuPy brute force, but it is not
the fastest path for this specific one-shot repeated measurement. That matches
the overlay scale lesson: prepared state should be selected by workload shape
and reuse pattern, not assumed to dominate every path.

## Claim Boundary

This goal authorizes:

- a narrow statement that `lsi_county256_soil256_count512` is parity-clean
  across Embree, one-shot OptiX, prepared OptiX, and CuPy RawKernel brute force
- a narrow statement that hot one-shot OptiX beats Embree by `62.472x` on this
  row
- a narrow statement that hot one-shot OptiX beats CuPy RawKernel brute force
  by `12.653x` on this sparse-intersection row
- a design conclusion that sparse true-hit geometry is where RT traversal can
  beat brute-force CUDA-core candidate evaluation

This goal does not authorize:

- full RayJoin paper reproduction
- broad RT-core speedup claims
- v2.0 release authorization
- whole-app RayJoin speedup claims
- claims against stronger CUDA/CuPy spatial-indexed baselines
- cold-start OptiX claims using the hot-repeat median

## Verdict

Goal2179 is accepted as a strong LSI subproblem evidence row. It shows that the
generic RTDL OptiX LSI path can sharply outperform both Embree and a brute-force
CuPy RawKernel baseline when the candidate pair space is large and the true-hit
set is sparse.
