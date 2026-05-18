# Goal2332 RayJoin Same-Query Pod Evidence

Date: 2026-05-18

Status: `same-query-pod-evidence-partial-lsi-blocked`

## Purpose

Goal2331 prepared a patch that lets RayJoin's own `query_exec` export the exact
LSI/PIP query streams it times. Goal2332 used that bridge on an RTX pod so RTDL
could replay RayJoin-authored streams instead of RTDL-generated demo streams.

This is deliberately a reality-check report, not a victory report. It records
that the bridge works, that RTDL can replay the streams through the prepared
OptiX v2.0 routes, and that the current RTDL route is not yet competitive with
RayJoin's specialized implementation. It also records a one-hit LSI semantic
blocker that must be resolved before any same-contract RayJoin claim.

## Environment

| Item | Value |
| --- | --- |
| Pod command supplied | `ssh root@69.30.85.175 -p 22114 -i ~/.ssh/id_ed25519` |
| Windows key actually used | `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod` |
| Pod GPU | `NVIDIA RTX A5000, 570.211.01` |
| RTDL checkout | `/root/rtdl` |
| RTDL commit | `617b43aef389b91f8a9daa52e645c7a964fb9a1d` |
| RayJoin checkout | `/root/RayJoin_goal2331` |
| RayJoin upstream commit | `02bf622 Update README.md` |
| RayJoin patch | `docs/research/rayjoin_query_exec_export_patch.diff` |
| RayJoin compatibility edit | `#include <nvtx3/nvToolsExt.h>` in `src/util/markers.h` for CUDA 12.8 build compatibility |
| OptiX SDK | `/root/vendor/optix-sdk`, tag `v8.1.0` |
| CUDA | `/usr/local/cuda-12` |

RayJoin was built only for the required `query_exec` target. The full upstream
target set still has unrelated CUDA 12.8/overlay build issues, so this report
does not claim a full RayJoin repository reproduction.

## Commands

RTDL OptiX build:

```bash
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12
```

RayJoin CMake configuration:

```bash
export CUDA_HOME=/usr/local/cuda-12
export CUDACXX=/usr/local/cuda-12/bin/nvcc
export PATH=/usr/local/cuda-12/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12/lib64:/usr/local/cuda-12/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}

cmake -S /root/RayJoin_goal2331 -B /root/RayJoin_goal2331_build \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH=/root/vendor/optix-sdk \
  -DCUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda-12 \
  -DCMAKE_CUDA_COMPILER=/usr/local/cuda-12/bin/nvcc \
  -DCMAKE_CUDA_ARCHITECTURES=86

cmake --build /root/RayJoin_goal2331_build --target query_exec -j"$(nproc)"
```

RayJoin 65,536-query export runs:

```bash
BASE=/root/RayJoin_goal2331/test/dataset/br_county_clean_25_odyssey_final.txt
OUT=/root/rtdl/docs/reports/goal2332_rayjoin_same_contract_pod

timeout 900 /root/RayJoin_goal2331_build/bin/query_exec \
  -poly1="$BASE" -mode=rt -query=lsi -gen_n=65536 -gen_t=0.1 -seed=2327 \
  -warmup=3 -repeat=15 -check=false \
  -export_query_stream="$OUT/rayjoin_lsi_stream_65536.json" \
  2>&1 | tee "$OUT/rayjoin_lsi_65536.log"

timeout 900 /root/RayJoin_goal2331_build/bin/query_exec \
  -poly1="$BASE" -mode=rt -query=pip -gen_n=65536 -gen_t=0.1 -seed=2328 \
  -warmup=3 -repeat=15 -check=false \
  -export_query_stream="$OUT/rayjoin_pip_stream_65536.json" \
  2>&1 | tee "$OUT/rayjoin_pip_65536.log"
```

RTDL replay:

```bash
PYTHONPATH=src:. \
RTDL_OPTIX_LIBRARY=/root/rtdl/build/librtdl_optix.so \
STEP_TIMEOUT_SECONDS=900 \
WARMUPS=3 \
REPEATS=15 \
OUTPUT_DIR=docs/reports/goal2332_rayjoin_same_contract_pod/rtdl_replay \
LSI_STREAM=docs/reports/goal2332_rayjoin_same_contract_pod/rayjoin_lsi_stream_65536.json \
PIP_STREAM=docs/reports/goal2332_rayjoin_same_contract_pod/rayjoin_pip_stream_65536.json \
bash scripts/goal2327_rayjoin_pod_perf_runner.sh
```

## Artifacts

| Artifact | Role |
| --- | --- |
| `docs/reports/goal2332_rayjoin_same_contract_pod/rayjoin_lsi_65536.log` | RayJoin LSI timing and count log |
| `docs/reports/goal2332_rayjoin_same_contract_pod/rayjoin_lsi_stream_65536.json` | RayJoin-authored LSI query stream |
| `docs/reports/goal2332_rayjoin_same_contract_pod/rayjoin_pip_65536.log` | RayJoin PIP timing log |
| `docs/reports/goal2332_rayjoin_same_contract_pod/rayjoin_pip_stream_65536.json` | RayJoin-authored PIP query stream |
| `docs/reports/goal2332_rayjoin_same_contract_pod/rtdl_replay/same_query_prepared_comparison.json` | RTDL prepared OptiX replay timings |
| `docs/reports/goal2332_rayjoin_same_contract_pod/debug_4096/` | Smaller 4,096-query debug rerun |

Both stream files use schema `rtdl.rayjoin.same_query_stream.v1`, producer
`rayjoin_query_exec_export_patch`, and `query_count=65536`.

## 65,536-Query Results

| Workload | RayJoin query time | RayJoin visible count | RTDL v2.0 route | RTDL median query time | RTDL count | Current result |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| LSI | 0.460211 ms | 5,809 | prepared segment/segment candidates plus exact refine | 4.807 ms | 5,808 | blocked: one-hit mismatch and slower |
| PIP | 0.389942 ms | not printed by `query_exec` | prepared point/closed-shape membership | 5.737 ms | 5,783 | timing captured; RayJoin count not visible |

The LSI timing ratio is approximately `10.4x` slower for RTDL's current route
on this same stream. The PIP timing ratio is approximately `14.7x` slower for
RTDL's current route, but PIP still needs a RayJoin-visible result count before
claiming semantic parity against `query_exec`.

## One-Time Setup Timing

| Workload | RayJoin measured setup phases | RTDL measured setup phases | Interpretation |
| --- | ---: | ---: | --- |
| LSI | Load Data + Create App + Init + Adaptive Grouping + Build Index = about 181 ms | left pack 68.8 ms + prepare 1,022.1 ms | RTDL's general prepared route is much heavier than RayJoin's specialized app/index path |
| PIP | Load Data + Create App + Init + Adaptive Grouping + Build Index = about 150 ms | point pack 66.8 ms + shape pack 181.5 ms + prepare 368.4 ms | RTDL setup is again heavier, though less dramatically than LSI |

This is not an exact whole-application comparison because RayJoin and RTDL time
different host responsibilities. It is enough to show the current bottleneck:
RTDL is paying for generality, Python orchestration, and a less specialized
candidate/refine path.

## 4,096-Query Debug Run

The smaller rerun reproduced the same LSI shape:

| Workload | RayJoin visible count | RTDL raw candidates | RTDL emitted count | RTDL median query time | Note |
| --- | ---: | ---: | ---: | ---: | --- |
| LSI | 342 | 342 | 341 | 0.410 ms scalar / 0.422 ms rows | RTDL exact refine drops one candidate that RayJoin counts |
| PIP | not printed by `query_exec` | n/a | 339 | 1.186 ms scalar / 1.202 ms rows | RTDL is internally stable, but RayJoin-visible count is missing |

The 4,096 all-backend CPU reference attempt was not completed because the
Python CPU reference over the full 326,193-edge RayJoin map exceeded the
600-second timeout. That is an expected scale limit of the debug oracle, not a
pass/fail result for the OptiX path.

## What This Proves

- The RayJoin export patch successfully produces RTDL-readable, RayJoin-authored
  query streams.
- RTDL can replay those streams on the prepared OptiX v2.0 path on an RTX A5000.
- RTDL output is internally deterministic across repeated runs.
- The current RTDL route is not yet same-contract clean for LSI against
  RayJoin's visible count.
- The current RTDL route is not yet performance-competitive with RayJoin's
  specialized C++/CUDA/OptiX implementation.

## What This Does Not Prove

This report does not authorize:

- an RTDL-beats-RayJoin claim;
- a RayJoin paper reproduction claim;
- a broad RTX speedup claim;
- a whole-app speedup claim;
- a v2.0 release decision.

## Design Diagnosis

The useful design signal is the same one that has been emerging across the
RayJoin tuning work: another app-shaped trick is not the right answer. RTDL
needs a more generic device-resident row-stream/continuation story so a user can
keep grouped ray results on device, apply exact filters/reductions there, and
avoid the current Python/CuPy/host orchestration overhead.

For this RayJoin-specific project, the immediate technical blocker is narrower:
add or temporarily maintain a RayJoin result-export patch that dumps LSI result
identities from `query_exec`, then compare the exact missing candidate. Until
that one-hit difference is explained, the LSI same-contract column stays red.

## Next Work

1. Add a clean RayJoin result-export patch for LSI result ids, separate from the
   already validated query-stream export patch.
2. Identify the exact query/base-segment pair that RayJoin counts and RTDL exact
   refine rejects.
3. Decide whether the difference is precision policy, boundary-touch semantics,
   duplicate handling, or a bug in one side.
4. Add a same-contract regression fixture once the policy is understood.
5. Only after correctness is settled, resume performance tuning toward a
   reusable device-resident continuation primitive.
