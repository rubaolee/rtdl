# Goal4806 RayJoin Section 5.7 County x Zipcode Completion Slice

Date: 2026-06-30

## Scope

This report records the current Goal4806 result for RayJoin Section 5.7 Polygon
Overlay on the County x Zipcode pair.

The goal is not to change RayJoin into a different workload. The intended change
is implementation stack:

- author: C++ / CUDA / OptiX
- RTDL route: Python / RTDL / RTDL-native OptiX
- V4 candidate route: Python / RTDL / Numba continuation where measured

## Completed Correctness Result

The RTDL-native OptiX reproduction now emits a byte-equal full overlay output
for County x Zipcode against the RayJoin author program output.

Author output:

`/workspace/rtdl_goal4806_fast_min/artifacts/section57_author_output_debug/author_overlay_debug.overlay.txt`

RTDL output:

`/workspace/rtdl_goal4806_fast_min/artifacts/section57_same_source_county_zipcode_output_after_no_zero_length_correction_full/section57_overlay_county_zipcode_rtdl_after_no_zero_length_correction_full_optix.txt`

Observed equality:

```text
BYTE_EQUAL=1
  87758310 author_overlay_debug.overlay.txt
  87758310 section57_overlay_county_zipcode_rtdl_after_no_zero_length_correction_full_optix.txt
chain_count 29254027 face_count 115490 total_sec 459.2447640225291
midpoint_map1_corrections 0
```

## RTDL Timing Breakdown

From the RTDL JSON artifact:

| Phase | Seconds |
|---|---:|
| total | `459.2447640225291` |
| load/pack | `55.94454927742481` |
| compute without load/pack | `403.3002147451043` |
| output-chain assembly | `224.5616100281477` |
| output-chain write | `79.02145949751139` |
| LSI hot | `36.43369720131159` |
| vertex map0 hot | `4.490990467369556` |
| vertex map1 hot | `5.771099708974361` |
| midpoint map0 hot | `0.23856232315301895` |
| midpoint map1 hot | `0.24261629581451416` |

This timing does not authorize a speed claim against the author program. It
shows a correct but slower RTDL full-overlay route.

## Author Timing Reference

The author run's stderr/timer output recorded:

| Author phase | Time |
|---|---:|
| Read map 0 | `4509.42 ms` |
| Read map 1 | `11731.9 ms` |
| Create App | `4.71711 ms` |
| Load Data | `346.085 ms` |
| Init | `579.568 ms` |
| Build Index | `54.9879 ms` |
| Intersection edges | `17.858 ms` |
| Map 0 Locate vertices | `29.64 ms` |
| Map 1 Locate vertices | `53.1571 ms` |
| Compute output polygons | `99.3621 ms` |
| Write to file | `132119 ms` |

The fair conclusion is:

- byte-equal correctness: yes;
- author-code full-overlay speed parity: no;
- high-performance Section 5.7 claim: not authorized.

## Code Changes Behind Byte Equality

The correctness fix depended on three findings:

1. Endpoint output materialization must match the author path. For rational
   coordinates with denominator `1`, the internal integer numerator is used
   directly instead of being pushed through floating conversion.
2. Output-chain deduplication must use exact consecutive equality, matching the
   author `std::unique` behavior. Tolerance dedupe is wrong here.
3. The prior zero-length midpoint correction heuristic produced exactly five
   incorrect corrections and five extra one-point chains. The production path
   now assigns midpoint faces directly and records zero corrections.

Native OptiX support was also updated to make RayJoin CDB point-location tie
handling deterministic under OptiX traversal pruning.

## Failed Experiments Not To Reintroduce

- Pre-midpoint zero-length one-point chain suppression overfiltered the output.
- Vertex-PIP scaled route did not fix the observed classification differences
  and made full runs slower.
- Tolerance-based output-chain dedupe changes author semantics.

## V4+Numba Candidate Result

The initial Numba candidate run failed because the POD had CUDA 12.8 toolkit
libraries with a CUDA 12.4 driver, causing Numba to emit unsupported PTX 8.7.
Installing CUDA 12.4 NVCC/runtime Python packages and setting:

```bash
export CUDA_HOME=/tmp/rtdl_goal4806_venv/lib/python3.12/site-packages/nvidia/cuda_nvcc
export LD_LIBRARY_PATH=$CUDA_HOME/nvvm/lib64:$LD_LIBRARY_PATH
```

made Numba emit PTX 8.4 and run successfully.

The measured County x Zipcode candidate probe then completed:

```bash
python scripts/rayjoin_section57_numba_candidate_probe.py \
  --dataset-root /workspace/rayjoin_section57_same_source_cdb \
  --pairs county_zipcode \
  --warmup 1 \
  --repeat 3 \
  --topology-geometry-hash-match-confirmed \
  --output-json artifacts/goal4806_v4_numba_candidate_probe_after_byte_equal_cuda124/candidates_warmup1_repeat3.json
```

Remote artifact:

`/workspace/rtdl_goal4806_fast_min/artifacts/goal4806_v4_numba_candidate_probe_after_byte_equal_cuda124/candidates_warmup1_repeat3.json`

| Candidate | Correctness | Hot-path host materialization | Steady-state sec | Selector status |
|---|---:|---:|---:|---|
| `v4_numba_post_traversal_segmented_counts` | pass | false | `0.01628301292657852` | eligible |
| `v4_numba_post_traversal_mask_compact` | pass | true | `0.006718732416629791` | rejected for selector due host materialization |
| `v4_numba_post_traversal_lsi_stream_digest` | pass | false | `0.13609668612480164` | eligible but slower |

All measured candidates agree on:

- candidate row count: `965,844`
- expected LSI count: `965,844`
- topology/geometry hash match: confirmed
- device-column route: true
- measurement source: POD runtime

The selected candidate-stage V4+Numba primitive route is:

`v4_numba_post_traversal_segmented_counts`

## Planner Import Verification

The measured candidate JSON was imported through the real V4 planner on the POD
with the Section 5.7 dataset root and author binaries present:

```text
claim_classification: candidate_stage_measured_no_app_speedup_claim
selected_plan: v4_numba_post_traversal_segmented_counts
measurement_import.rejections:
  - pair_id: county_zipcode
    plan_id: v4_numba_post_traversal_mask_compact
    reason: host_materialization_in_hot_path_rejected
```

This verifies that the result is not only hand-read from JSON. The V4 planner
consumes the measurement, rejects the unsafe faster host-materializing row, and
selects the fastest no-host-hot-path measured candidate.

## Claim Boundary

This is a significant Goal4806 slice, but it is not the final paper-reproduction
claim:

- Full County x Zipcode RTDL native OptiX correctness is proven byte-equal.
- V4+Numba post-traversal candidate measurement is now real and unblocked.
- Full V4+Numba polygon overlay is not yet proven faster than author code.
- All eight Section 5.7 pairs are not yet measured in this slice.

## Next Work

1. Feed the selected candidate-stage row into the V4 planner decision path.
2. Decide whether Goal4806 closes as:
   - native OptiX byte-equal correctness plus measured Numba candidate, or
   - a larger all-eight-pair V4+Numba Section 5.7 campaign.
3. If continuing the larger campaign, rerun the same matrix across all eight
   Section 5.7 pairs with the CUDA 12.4 Numba environment pinned.
4. Send this report for external review before any public Section 5.7 claim.
