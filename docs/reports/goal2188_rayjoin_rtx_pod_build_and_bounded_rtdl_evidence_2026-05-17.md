# Goal2188 RayJoin RTX Pod Build And Bounded RTDL Evidence

Date: 2026-05-17

Status: RTX pod build/protocol/bounded evidence complete; paper-scale
RayJoin reproduction remains a separate blocked lane.

## Purpose

Goal2188 continues Goal2184 on an RTX pod. The purpose is to verify that:

1. The real RayJoin repository builds and runs on RTX-era CUDA/OptiX hardware.
2. RayJoin's own `grid`, `lbvh`, and `rt` modes produce sample evidence on the
   same pod.
3. RTDL v2.0 can run bounded RayJoin CDB-shaped PIP, LSI, and overlay-seed
   workloads on the same pod with CPU/Embree/OptiX parity.
4. No RTDL native engine code is customized for RayJoin.

This report is evidence for the Goal2184 pod phase. It does not claim full
paper reproduction, RTDL-vs-RayJoin victory, broad RT-core speedup, or v2.0
release readiness.

## Pod Environment

Pod SSH command supplied by the user:

- `ssh root@69.30.85.202 -p 22064 -i ~/.ssh/id_ed25519`

Actual key used by Codex after the copied `~/.ssh` key path failed:

- `id_ed25519_rtdl_codex` from the RTDL working tree.

Environment:

| Item | Value |
| --- | --- |
| Hostname | `7fd5fd40ae4b` |
| GPU | `NVIDIA RTX A5000` |
| Driver | `570.211.01` |
| GPU memory | `24564 MiB` |
| CUDA compiler | `cuda_12.8.r12.8/compiler.35583870_0` |
| OptiX SDK prefix | `/root/vendor/optix-sdk` |
| RTDL commit | `8af5f62d3062d757ede52ad4309f40ebcc6dcc6c` |
| RayJoin commit | `02bf6220d6d20b04af77ee20364eced75cc029c9` |

## RayJoin Build Notes

RayJoin was cloned into the disposable pod workspace:

- `/root/goal2184_pod/RayJoin`

The release build succeeded for:

- `release/bin/query_exec`
- `release/bin/polyover_exec`

External RayJoin compatibility patches were required for this pod toolchain:

1. `src/CMakeLists.txt`: use RTX A5000 SM target `86`.
2. `src/app/output_chain.h`: add a local vector hash/equality predicate for
   one `unordered_map` use rejected by the current GCC/CUDA toolchain.
3. `src/util/markers.h`: include `nvtx3/nvToolsExt.h` instead of the legacy
   `nvToolsExt.h`, because CUDA 12.8 otherwise includes both legacy NVTX and
   NVTX3 declarations during `rt_engine.cu` compilation.

These patches are external RayJoin build-compatibility patches. They are not
RTDL changes and are not RayJoin-algorithm changes.

RTDL pod setup notes:

- `make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12.8` succeeded.
- `make build-embree` required installing `libembree-dev` and `libgeos-dev`,
  then succeeded with Embree `4.3.0`.
- CuPy `14.0.1` detected the RTX A5000.

## RayJoin Native Evidence

Raw artifacts:

- `docs/reports/goal2188_rayjoin_native_pod_summary_2026-05-17.json`
- `docs/reports/goal2188_rayjoin_native_pod_sample_protocol_raw_2026-05-17.txt`
- `docs/reports/goal2188_rayjoin_native_pod_query_protocol_raw_2026-05-17.txt`

### Overlay Sample

RayJoin's checked-in sample overlay was run against:

- `test/dataset/br_county_clean_25_odyssey_final.txt`
- `test/dataset/br_soil_ascii_odyssey_final.txt`
- `test/dataset/br_countyXbr_soil_answer.txt`

All three modes diff-passed against the checked-in answer.

| RayJoin mode | Answer diff | Build index ms | Intersection edges ms | Locate map 0 ms | Locate map 1 ms | Compute output polygons ms | OptiX launches |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `grid` | pass | 14.4949 | 9.44805 | 3.6099 | 3.05605 | 14.818 | 0 |
| `lbvh` | pass | 6.248 | 2.62117 | 25.2049 | 15.45 | 17.251 | 0 |
| `rt` | pass | 1.98698 | 1.266 | 1.23692 | 0.916958 | 8.19516 | 5 |

The RayJoin `rt` sample path therefore really used OptiX launches on the pod.

### Generated 100k Query Sample

RayJoin `query_exec` was run with:

- `-poly1=<br_county sample>`
- `-query=lsi|pip`
- `-mode=grid|lbvh|rt`
- `-gen_n=100000`
- `-seed=2184`
- `-warmup=1`
- `-repeat=3`

| Query | RayJoin mode | Query phase ms | Build index ms | Adaptive grouping ms | Intersections | Built-in check | OptiX launches |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| `lsi` | `grid` | 4.61539 | 2.76518 | n/a | 8,921 | n/a | 0 |
| `lsi` | `lbvh` | 1.58866 | 14.081 | n/a | 8,921 | n/a | 0 |
| `lsi` | `rt` | 0.615358 | 0.754833 | 0.534058 | 8,921 | n/a | 4 |
| `pip` | `grid` | 16.7463 | 2.62284 | n/a | n/a | n/a | 0 |
| `pip` | `lbvh` | 10.5449 | 3.95584 | n/a | n/a | pass | 0 |
| `pip` | `rt` | 0.57737 | 4.91118 | 0.945807 | n/a | pass | 4 |

The query evidence shows RayJoin's own RT path behaving as expected on the pod:
fast query phases and explicit OptiX launches. For LSI, the current RayJoin
source does not run a `CheckPIPResult`-style built-in checker; the LSI row is
recorded as completed timing evidence, not as a separate answer-diff check.

## RTDL Same-CDB Bounded Evidence

RTDL was cloned from `origin/main`, reset to
`8af5f62d3062d757ede52ad4309f40ebcc6dcc6c`, and run against CDB files copied
from RayJoin's checked-in sample dataset.

Artifacts:

- `docs/reports/goal2188_pod_rtdl_rayjoin_pip_county512_2026-05-17.json`
- `docs/reports/goal2188_pod_rtdl_rayjoin_lsi_count512_2026-05-17.json`
- `docs/reports/goal2188_pod_rtdl_rayjoin_overlay_count512_2026-05-17.json`

The artifacts were produced by the older Goal2159 runner. Their copied
metadata was corrected from `"goal": "2159"` to `"goal": "2188"` and records
`"source_runner_goal": "2159"`; row counts, timings, parity flags, commit,
dataset paths, and claim-boundary flags were not changed.

### PIP

Case: `pip_county512`

| Backend | Median app seconds | Rows | Parity |
| --- | ---: | ---: | --- |
| `cpu` | 0.018638 | 1,430 | true |
| `embree` | 0.004631 | 1,430 | true |
| `optix` | 0.004597 | 1,430 | true |

### LSI

Case: `lsi_county256_soil256_count512`

| Backend | Median app seconds | Rows | Parity |
| --- | ---: | ---: | --- |
| `cpu` | 0.036568 | 269 | true |
| `cupy_lsi_bruteforce` | 0.040761 | 269 | true |
| `embree` | 0.407584 | 269 | true |
| `optix` | 0.004452 | 269 | true |
| `optix_prepared_lsi` | 0.025803 | 269 | true |

For this bounded 512-slice LSI case, one-shot RTDL OptiX is the fastest RTDL
backend. The prepared path remains useful as a reusable-index protocol surface,
but this artifact does not show an amortization win at this slice size.

### Overlay Seed

Case: `overlay_county512_soil512`

| Backend | Median app seconds | Rows | Parity |
| --- | ---: | ---: | --- |
| `cpu` | 42.499070 | 233,766 | true |
| `embree` | 1.014213 | 233,766 | true |
| `optix` | 0.328156 | 233,766 | true |
| `optix_prepared_overlay_seed` | 0.333014 | 233,766 | true |

This is the strongest bounded RTDL pod result in this report: the generic
shape-pair RTDL OptiX path runs the overlay dependency-row seed with full parity
and a large win over the Python CPU reference.

## Interpretation

What is now proven:

- RayJoin itself can be built and run on an RTX A5000 pod.
- RayJoin `rt` paths emit real OptiX launches and are faster than RayJoin
  `grid`/`lbvh` query phases in the generated 100k query protocol.
- RTDL v2.0 can ingest RayJoin CDB-shaped sample data and run bounded PIP, LSI,
  and overlay-seed workloads with parity across the tested CPU/Embree/OptiX
  backend matrix.
- RTDL did this without adding RayJoin-specific native symbols, RayJoin-only
  kernels, or app-customized engine code.

What is not yet proven:

- Full RayJoin paper reproduction.
- RTDL beating the RayJoin implementation.
- End-to-end overlay equivalence to RayJoin's full output-chain construction.
- Broad RT-core speedups across all spatial workloads.
- v2.0 release readiness.

The RayJoin-native timings and RTDL timings in this report are adjacent
evidence, not a direct same-contract performance fight. RayJoin's generated
query protocol and RTDL's bounded CDB-slice protocol are not identical
experiments. The next serious reproduction step must align the query generator,
dataset scale, output contract, and timing boundaries before making public
comparison claims.

## Next Work

1. Reconstruct the RayJoin paper's dataset/protocol matrix from the repository,
   paper, and scripts rather than only the checked-in sample.
2. Add an RTDL-side same-query adapter so RTDL can consume the same generated
   query streams used by RayJoin `query_exec`.
3. Separate exact subpath timings: index build, adaptive grouping, RT launch,
   post-processing, output materialization, and file I/O.
4. Extend the overlay contract from dependency-row seed parity toward full
   output-chain parity, or explicitly document that RTDL is comparing the RT
   primitive phase rather than full RayJoin overlay construction.
5. Obtain external Gemini and Claude review before any public RayJoin
   performance claim.

## Verdict

Goal2188 upgrades Goal2184 from local-only evidence to real RTX pod evidence.
It is `accept-with-boundary`.

The boundary is important: this is successful build/protocol/bounded RTDL
evidence, not a final RayJoin paper reproduction and not a public release claim.
