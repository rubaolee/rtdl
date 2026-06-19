# RTDL V2.x / V3 / V4 Large-Scale Performance Comparison

Status: fresh large-scale evidence packet plus historical comparison; not release authorization.

Date: 2026-06-19

## Bottom Line

RTDL does not yet have one fair, single-number performance comparison across
V2.x, V3, and V4 because the versions answer different product questions.

- V2.14 is the strongest public performance baseline: it has a row-scoped,
  same-contract RTDL/OptiX-vs-Embree matrix across the promoted benchmark apps.
- V3.0.2 is not a new broad speedup release. It closes the ten benchmark-app
  current-route surface and keeps route choice explicit. A fresh all-app
  scale-profile run on `192.168.1.20` passed 10/10 rows.
- V4.0 is not an all benchmark-app performance suite. It is one experimental
  Python GPU device-array operator route. A fresh 262K-row V4 M1 probe passed,
  but it still does not authorize public speedup, RT-core speedup, or
  true-zero-copy wording.

The serious reader should treat this as an evidence map:

1. Use V2.14 for published row-scoped speedup language.
2. Use V3.0.2 for current-route health and all-app route closure.
3. Use V4.0 for the new device-array operator direction only.

## Execution Surface

Remote RTX pod:

- `root@157.157.221.29 -p 22234` was attempted with the provided key.
- Result: `Permission denied (publickey,password)`.

Available Linux host:

- Host: `192.168.1.20`, hostname `lx1`.
- GPU: `NVIDIA GeForce GTX 1070`, driver `580.126.09`, 8192 MiB, compute
  capability 6.1.
- Important boundary: this is not RTX hardware and cannot prove RT-core speedup
  claims.
- Source commit: `6d2193af16f8269f3e901124593dacc43335255b`.
- `make build-optix`: passed.
- Source-tree doctor: passed with only optional Embree library warning.

Main fresh run:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
python3 scripts/goal3828_current_benchmark_scale_profile_runner.py \
  --materialize-rayjoin-public-cdb \
  --output-json docs/reports/v2_v3_v4_large_scale_performance_2026-06-19/lx1_current_benchmark_scale_profile_2026-06-19.json \
  --output-dir docs/reports/v2_v3_v4_large_scale_performance_2026-06-19/scale_outputs \
  --timeout-scale 2.0 \
  --heartbeat-sec 60 \
  --stdout-tail 12000 \
  --stderr-tail 8000
```

Result: 10/10 rows passed, 10/10 row stdout files were parseable JSON, and no
claim-boundary flag violations were found.

## Artifact Index

- Raw all-app run:
  `docs/reports/v2_v3_v4_large_scale_performance_2026-06-19/lx1_current_benchmark_scale_profile_2026-06-19.json`
- Per-row stdout/stderr:
  `docs/reports/v2_v3_v4_large_scale_performance_2026-06-19/scale_outputs/`
- Large supplements:
  `docs/reports/v2_v3_v4_large_scale_performance_2026-06-19/large_supplements/`
- V4 M1 large route probe:
  `docs/reports/v2_v3_v4_large_scale_performance_2026-06-19/lx1_v4_m1_fixed_radius_cupy_262k_probe_2026-06-19.json`
- Historical V2.14 comparison:
  `docs/history/release_reports/v2_14/public_rt_vs_embree_comparison.md`
- Historical V2.14 phase explanations:
  `docs/history/release_reports/v2_14/benchmark_app_phase_explanations.md`
- Current V3.0.2 support matrix:
  `docs/release_reports/v3_0_2/support_matrix.md`
- V4 M8 release-candidate packet:
  `docs/engineering/rtdl_v4_0_m8_release_candidate_packet_2026-06-19.md`

## V2.x Baseline: V2.14 Row-Scoped Performance

V2.14 is the proper historical performance comparison point. It does not claim
universal RT-core acceleration; it publishes row-scoped, contract-scoped,
hardware-scoped statements with phase explanations.

| V2.14 row | Released readout | Boundary |
| --- | ---: | --- |
| RTNN ranked summary | Exact OptiX 10.14x-11.80x faster than Embree; separate float32 best path 47.36x-89.85x | RTNN-shaped row only; no paper-dataset claim. |
| RT-DBSCAN core flags | At 524,288 points, total 1.05x OptiX faster; threshold stage 1.37x faster | Narrow engineering row; Numba continuation dominates total. |
| Spatial RayJoin LSI | OptiX 29.93x faster | Scalar-count row, not full RayJoin reproduction. |
| Spatial RayJoin PIP | OptiX 1.10x faster | Modest scalar-count wording only. |
| Spatial RayJoin overlay | Available 2/8 exact-ready pairs: OptiX 2.61x and 1.88x faster | No full 8/8 Section 5.7 claim. |
| RayDB-style grouped count | OptiX 14.05x faster per iteration | Generated RayDB-style row. |
| LibRTS AABB | 1M boxes x 1K queries: hot query 13.39x faster; cold total 2.27x faster | Hot-query and cold-total split required. |
| Triangle counting | Largest row total 2.44x faster; hot query 107.61x faster | Large synthetic RT-Graph-shaped primitive. |
| Barnes-Hut node coverage | 1M bodies x 65,536 nodes: hot query 2.06x faster | Node coverage only, not force solve. |
| Hausdorff/X-HD threshold | 1,048,576 points per side: directed hot-query sum 1.58x faster | Threshold decision only. |
| Robot collision | 1,048,576 groups: total 1.86x faster; traversal 6.69x faster | Discrete sampled flags only. |
| Contact manifold | `jittered_grid_65536`: AABB query 1.23x faster; hot path 1.16x faster | Broadphase/contact-witness row only. |

Interpretation: V2.14 is where performance claims live, and every claim is
attached to a row, contract, backend pair, partner policy, and caveat.

## Fresh V3.0.2 Current All-App Scale Run

This run verifies that the current V3.0.2 all-app route surface still executes
at scale on Linux. It is not a replacement for the V2.14 same-contract speedup
matrix because this host lacks Embree and RTX hardware.

| App | Fresh scale evidence on `lx1` | Hot metric | Result | Reading |
| --- | --- | --- | ---: | --- |
| Hausdorff / X-HD | Supplement row: 1,048,576 points per side, threshold decision | `query_fixed_radius_threshold_reached_count_sec` | 3.640 s | Large threshold route passes; oracle decision matches. |
| Spatial RayJoin | Public CDB representative mixed route; PIP, LSI, overlay seed; PIP batch 100 requests | Mixed route medians | PIP Numba 0.731 ms vs RTDL 2.582 ms; LSI RTDL 0.117 ms vs Numba 49.575 ms; overlay RTDL 0.576 ms vs Numba 71.276 ms | Mixed explicit route remains correct: Numba wins one-shot PIP, RTDL/OptiX wins LSI and overlay seed. |
| RT-DBSCAN | 65,536 clustered 3D points, OptiX threshold plus Numba component signature | Prepared query median | 436.991 ms | Current mixed route passes; no full-app speedup slogan. |
| Robot collision | 1,024 poses, 128 obstacles, 4 links, 49,900 measured runs | Traversal total | 4.105 s total; 82.011 us median | High-repeat resident hot path meets internal timing floor. |
| Contact manifold | Current runner grid64 row passed; large 65K fresh rerun was stopped because the Python reference path dominated runtime | Use V2.14 65K row for serious performance wording | V2.14: 65K hot path 1.16x | Do not treat the grid64 row as serious performance evidence. |
| RayDB-style | 262,144 generated rows, 1,024 groups, 5,000 repeats | Native call wall total | 7.483 s total; 1.492 ms median native call | Resident grouped-count primitive passes high-repeat floor. |
| Barnes-Hut | 8,192 bodies, Numba exact-force partner route | Median force kernel | 18.802 ms | Current best route is partner/fused, not Barnes-Hut RT-core speedup. |
| LibRTS spatial index | 32,768 boxes and 32,768 queries, all operations | Query median | 268.459 ms | Prepared AABB-index route passes; not full mutable LibRTS. |
| RTNN | 65,536 search points, 65,536 query points, k=50 | Prepared ranked-summary median | 0.572 ms | Prepared ranked-summary aggregate route passes; no paper-row claim. |
| Triangle counting | Supplement row: 131,072 rays, 327,680 primitives, RT-Graph 2A1 | Query median | 3.200 ms | Large synthetic RT-Graph-shaped route passes; oracle count matches. |

Fresh V3 conclusion: all ten current benchmark-app rows are executable on the
available Linux GPU host, and the two targeted internal timing-floor rows
passed. The run supports V3 current-route health, not broad public speedup
wording.

## V4.0 Large Route Probe

V4.0 does not yet have all benchmark-app coverage. It has one M1 product route:

`fixed_radius_count_threshold_2d`

To avoid toy-scale results, the 1,024-row smoke was not used here. A larger
262,144-row probe was run:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
python3 scripts/v4_0_m1_fixed_radius_cupy_benchmark_probe.py \
  --count 262144 \
  --repeats 3 \
  --warmups 1 \
  --output docs/reports/v2_v3_v4_large_scale_performance_2026-06-19/lx1_v4_m1_fixed_radius_cupy_262k_probe_2026-06-19.json
```

Result:

| Route | Count | Median one-shot prepare+query | Median prepared query | CuPy brute-force CUDA baseline median | Raw ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| V4 M1 fixed-radius CuPy route | 262,144 | 13.444 ms | 6.258 ms | 33.827 s | baseline/V4 prepared query 5405.56x |

This is useful engineering evidence, but it still does not authorize public
speedup wording:

- the baseline is a simple blocked all-pairs CuPy CUDA-core implementation, not
  a best-known tuned fixed-radius library baseline;
- the host is GTX 1070, not RTX;
- the report flags `public_speedup_claim_authorized`,
  `rt_core_speedup_claim_authorized`, `v4_true_zero_copy_claim_authorized`, and
  `async_claim_authorized` as false.

A 1,048,576-row V4 probe was attempted first and failed on the CuPy brute-force
baseline with GPU out-of-memory on the 8GB GTX 1070. That failure is not a V4
route failure; it is a limitation of the comparison baseline and host memory.

## Cross-Version Interpretation

| Question | Best evidence today | Answer |
| --- | --- | --- |
| Did V2.x establish serious performance rows? | V2.14 public RTDL/OptiX-vs-Embree matrix | Yes, row-scoped and caveated. |
| Did V3 improve the performance claim surface? | V3.0/V3.0.2 route closure plus fresh 10/10 scale-profile pass | Yes, as route maturity and app-author policy, not as a new broad speedup matrix. |
| Does V4 beat V3 on all apps? | No comparable evidence exists | No claim. V4 currently proves a new Python GPU device-array operator lane. |
| Do we have fresh all-app large-scale execution? | `lx1_current_benchmark_scale_profile_2026-06-19.json` | Yes, for current V3/V2.10+ inherited scale-profile rows. |
| Do we have RTX-class RT-core speed evidence from this run? | No, host is GTX 1070 and the RTX pod rejected SSH auth | No. |

## What This Packet Does Not Claim

This packet does not claim:

- V4.0 is faster than V3.0.2;
- V4.0 covers all benchmark apps;
- RTDL is broadly faster across all workloads;
- GTX 1070 timing proves RTX/RT-core speedup;
- the V4 CuPy brute-force baseline is a tuned library baseline;
- whole-application paper reproduction;
- automatic partner or backend selection;
- public true-zero-copy or async completion.

## Next Required Work For A Release-Grade Three-Generation Perf Paper

1. Restore or build Embree on the same Linux host so current V3 rows can be
   compared same-contract against CPU RT rows on identical hardware.
2. Re-run the all-app scale-profile packet on RTX-class hardware, preferably
   A5000, RTX 4000 Ada, A40, or better.
3. Add a V4 benchmark baseline that is not a simple O(N x block) CuPy brute
   force comparison, then rerun at 1M+ rows without baseline OOM.
4. Decide whether V4 should grow all-app benchmark coverage or remain a narrow
   operator-lane release for M1.
5. Produce one external-review packet that explicitly separates V2.14 speedup
   wording, V3 route maturity, and V4 operator-route evidence.
