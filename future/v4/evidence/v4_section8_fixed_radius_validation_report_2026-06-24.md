# V4 Section 8 Fixed-Radius Count-Threshold Validation Report

Date: 2026-06-24
Status: measured; strict gate failed; external review required before any V4 build decision

## Question

Does the existing fused native fixed-radius threshold-count primitive materially beat the separated RTDL row-materialization route on the same contract and RT hardware?

## Environment

- Pod: `root@213.173.108.14 -p 10993`
- GPU: NVIDIA RTX 4000 Ada Generation
- Driver: 550.127.05
- CUDA prefix: `/usr/local/cuda-12.8`
- OptiX headers: NVIDIA `optix-dev` `v8.0.0`
- Native library: `/root/rtdl_v4_section8/repo/build/librtdl_optix.so`

## Evidence Files

- Raw result JSON: `future/v4/evidence/v4_section8_fixed_radius_result_2026-06-24.json`
- Full rerun progress log: `future/v4/evidence/v4_section8_full_rerun_progress_2026-06-24.log`
- Phase profile JSON: `future/v4/evidence/v4_section8_summary_route_phase_profile_2026-06-24.json`
- Phase profile log: `future/v4/evidence/v4_section8_summary_route_phase_profile_2026-06-24.log`

## Measurement Correction

The first 8192 attempt exposed a measurement-boundary bug: `output_mode=full` used `brute_force_outlier_rows(...)` as the oracle, which makes the timed path include an O(N^2) correctness calculation. That is not the separated RTDL route. The app now uses the exact tiled oracle for this fixture across all output modes, with a regression test preventing a return to the quadratic oracle.

## Results

| copies | points | correctness | optix rows median | scalar fused median | scalar speedup | summary fused median | summary speedup |
| ---: | ---: | :---: | ---: | ---: | ---: | ---: | ---: |
| 8192 | 65,536 | pass | 0.763980s | 0.363886s | 2.100x | 0.540099s | 1.415x |
| 32768 | 262,144 | pass | 3.232958s | 1.498686s | 2.157x | 2.319243s | 1.394x |
| 131072 | 1,048,576 | pass | 14.987845s | 6.158623s | 2.434x | 10.010178s | 1.497x |

## Gate Outcome

Strict Section 8 gate:

- scalar fused route must be at least 2.0x on at least two serious sizes: pass, all three sizes passed.
- summary fused route must be at least 1.5x on at least two serious sizes: fail, no serious size passed in the final rerun.
- correctness must pass: pass.
- winning route must use native fixed-radius count-threshold continuation: pass for fused routes.

Overall strict gate: `fail`

Harness next-step field: `stop_v4_performance_release_and_revisit_architecture`

## Interpretation

The scalar fused primitive is real and material: it avoids neighbor-row materialization and clears the 2.0x gate on all measured serious sizes. The compact summary route is directionally faster than rows but does not clear the predeclared 1.5x gate on two sizes. This means the current evidence validates a scalar threshold-count fused primitive, but it does not yet validate the broader Section 8 Tier-2 thesis as written.

## Phase Profile Follow-Up

The phase profile separates route hot work from per-call prepare/setup:

| copies | rows total median | summary no-prepare median | summary with-prepare median | scalar native median | summary Python convert median |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 8192 | 0.602244s | 0.292527s | 0.402068s | 0.130798s | 0.050451s |
| 32768 | 2.539660s | 1.243263s | 1.725643s | 0.500738s | 0.218955s |
| 131072 | 12.316418s | 5.261208s | 7.103815s | 2.042837s | 1.252453s |

This suggests the fused summary primitive's hot path does beat the rows path by more than 2x when the prepared scene is reused, but the current Section 8 harness measures the app route with prepare/setup inside every repeat. The strict gate remains failed because the written protocol measured whole-call route medians. Revising the protocol to use prepared-session hot-path timings is a major design decision and requires external review; it is not assumed by this report.

No V4 release claim is authorized by this report.
