# Goal3239: RayJoin Upstream Build and Same-Slice Smoke

Date: 2026-06-03

## Purpose

Goal3239 begins the direct cross-system RayJoin lane requested after the RTDL
public row-continuation evidence. It does not try to reproduce the RayJoin paper
yet. Instead, it asks a narrower question:

Can the upstream RayJoin repository be built on the current pod, and can its own
binaries run on the same bounded public CDB slices used by RTDL Goal3232?

## Artifact

- `docs/reports/goal3239_rayjoin_upstream_build_and_same_slice_smoke_2026-06-03.json`

RTDL evidence commit: `edc073446c45a078d36bf52b7fb322994eb8f2a0`

RayJoin checkout:

- Repository: `https://github.com/rubaolee/RayJoin`
- Commit: `02bf6220d6d20b04af77ee20364eced75cc029c9`
- Pod workdir: `/root/RayJoin`
- Build output: `/root/RayJoin/build/bin/query_exec` and
  `/root/RayJoin/build/bin/polyover_exec`

## Build Result

RayJoin builds on the pod after two local CUDA 12.8 compatibility shims:

| File | Local shim | Why |
| --- | --- | --- |
| `src/util/markers.h` | include `nvtx3/nvToolsExt.h` instead of legacy `nvToolsExt.h` | Avoid duplicate NVTX2/NVTX3 type definitions with CUDA 12.8. |
| `src/app/output_chain.h` | use local `Double2Hash` / `Double2Equal` for the output-chain point map | Avoid `std::equal_to<double2>` compile failure under GCC 13/CUDA 12.8 without adding global operator pollution. |

Both RayJoin executables built after these shims.

## Same-Slice Smoke Results

| Case | RayJoin Mode | Status | RayJoin Result | RTDL Goal3232 Result | Query/Phase Time |
| --- | --- | --- | --- | --- | ---: |
| `lsi_county256_soil256_count512` | `rt` | pass | 269 intersections | 269 rows | 0.229 ms query |
| `lsi_county256_soil256_count512` | `grid` | pass with count difference vs RT | 268 intersections | 269 rows | 0.695 ms query |
| `pip_county512` | `rt` | pass checker map 0 | count not printed | 1430 positive rows | 0.186 ms query |
| `pip_county512` | `grid` | pass | count not printed | 1430 positive rows | 2.451 ms query |
| `overlay_county128_soil128` | `rt` | blocked runtime failure | `cudaErrorInvalidDevice` in `PIPRT::Query` | 14,036 rows | n/a |
| `overlay_county128_soil128` | `grid` | pass with `-check=false` | 127 output chains / 89 faces | 14,036 dependency rows | 0.228 ms intersection-edge phase |

The LSI RT lane is the strongest same-slice signal so far: upstream RayJoin RT
and RTDL prepared OptiX row continuation agree on the 269-row public slice. The
RayJoin grid lane reports 268 intersections on the same slice, so the grid result
is tracked as a count difference rather than treated as an oracle.

The PIP lanes are runtime/check smokes only. RayJoin reports that map 0 passed
its checker in RT mode, but the executable does not print the positive-assignment
row count in the normal log.

The overlay lane is not yet comparable. RayJoin `polyover_exec` builds, and grid
overlay can run with checking disabled, but RT overlay fails on this pod with:

`thrust parallel_for failed: cudaErrorInvalidDevice: invalid device ordinal`

The failure occurs inside `rayjoin::PIPRT::Query` during
`MapOverlayRT::LocateVerticesInOtherMap`, even with `CUDA_VISIBLE_DEVICES=0` and
`-check=false`.

## Boundary

This report does not authorize release, public speedup claims, broad RT-core
speedup claims, true zero-copy claims, `RTDL beats RayJoin` claims, or RayJoin
paper-reproduction claims.

Next work should either fix or isolate the upstream RayJoin overlay runtime
failure, then turn this smoke into a repeated same-contract comparison with
explicit output contracts and parsed result counts.
