# Goal4765 - RT-BarnesHut Native RT-Core Candidate

Date: 2026-06-26

Status: **completed as an engineering candidate, pending external review debt**

## Purpose

Replace the Goal4764 native ABI host fallback with an author-compatible OptiX
RT-core traversal/force candidate behind the same 3D ABI, while preserving the
4096/8192 checksum gates.

This goal is about same-semantics native execution. It is **not** a public
RT-BarnesHut paper-reproduction claim and **not** a V2/V3/V4 speed table.

## What Changed

- `src/native/optix/rtdl_optix_api.cpp`
  - Added an author-compatible 3D OptiX custom-primitive pipeline for the
    RT-BarnesHut route.
  - Added DFS/rope metadata generation modeled on the authors'
    `treeToDFSArray` and `installAutoRopes` flow.
  - Added device point/node structs, control AABBs, and an OptiX launch path.
  - Added status code `3` for `rt_core_author_semantics_candidate_route`.
  - Kept the Goal4764 host fallback behind explicit
    `RTDL_RT_BARNESHUT_AUTHOR_FORCE_FALLBACK=1`.

- `src/rtdsl/v4_rt_barneshut_native_route.py`
  - Added RT-core candidate status detection and status-code mapping.
  - Records `host_fallback_used`, `rt_core_execution`, and
    `input_columns_downloaded_for_tree_build` explicitly.

- `scripts/v4_rt_barneshut_native_fallback_route_probe.py`
  - Defaults to Goal4765 RT-core candidate mode.
  - Adds `--force-fallback` for the Goal4764 fallback regression gate.
  - Emits `goal4765_rt_core_candidate_attempted`.

- `tests/v4_goal4765_rt_barneshut_native_rt_core_candidate_test.py`
  - Adds a static/status regression gate for the new RT-core candidate route.

## POD Evidence

POD:

```text
root@194.68.245.170 -p 22089
GPU: NVIDIA RTX A5000
V4 root: /root/rtdl_v4_candidate_pod
OptiX: /workspace/vendor/optix-dev-8.0.0
```

Build gate:

```bash
make build-optix OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0 CUDA_PREFIX=/usr/local/cuda
```

Result: build passed. The only compiler warning is the existing anonymous
namespace pointer linkage warning pattern.

POD unit gate:

```bash
/root/rtdl_v4_venv/bin/python -m unittest \
  tests.v4_goal4762_rt_barneshut_native_feasibility_test \
  tests.v4_goal4763_rt_barneshut_native_abi_first_slice_test \
  tests.v4_goal4764_rt_barneshut_native_fallback_route_test \
  tests.v4_goal4765_rt_barneshut_native_rt_core_candidate_test
```

Result: `Ran 16 tests ... OK`.

Checksum evidence:

| Evidence | Points | Status | Host fallback | RT-core execution | Checksum rel. error | Abs-checksum rel. error | Pass |
|---|---:|---|---:|---:|---:|---:|---:|
| `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4765_rt_core_candidate_4096_pod_2026-06-26.json` | 4096 | `native_3d_author_semantics_rt_core_candidate_available` | false | true | `1.1367656829416352e-13` | `1.1367656829416352e-13` | true |
| `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4765_rt_core_candidate_8192_pod_2026-06-26.json` | 8192 | `native_3d_author_semantics_rt_core_candidate_available` | false | true | `2.0096898862946577e-13` | `2.0096898862946577e-13` | true |
| `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4765_fallback_regression_4096_pod_2026-06-26.json` | 4096 | `native_3d_author_semantics_host_fallback_available` | true | false | `2.9873327390354115e-15` | `2.9873327390354115e-15` | true |

Warm-run diagnostic:

`future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4765_rt_core_candidate_warm_repeat_8192_pod_2026-06-26.json`

The first run in a process includes OptiX/NVRTC pipeline initialization. The
second run reuses the loaded pipeline:

| Run | Points | RT-force seconds | Execution seconds | Interpretation |
|---:|---:|---:|---:|---|
| 1 | 8192 | `0.782372891` | `0.788206481` | cold path includes pipeline initialization |
| 2 | 8192 | `0.001561678` | `0.006655984` | warm candidate hot path |

## Interpretation

Goal4765 materially improves the state from Goal4764:

- Goal4764: same ABI and checksum-valid author semantics, but force evaluation
  was a host fallback.
- Goal4765: same ABI and checksum-valid author semantics with
  `implementation_status_code=3`, `host_fallback_used=false`, and
  `rt_core_execution=true`.

This proves that the native V4 route can execute an author-semantics
RT-BarnesHut candidate through OptiX traversal and produce checksum-parity force
columns for the 4096/8192 gates.

The current route still builds the tree metadata from a host snapshot of device
columns. That is recorded as `input_columns_downloaded_for_tree_build=true`.
This is acceptable for the current correctness gate, but it is not a no-copy
claim.

## Non-Authorization

Goal4765 does **not** authorize:

- public RT-BarnesHut paper-reproduction wording;
- a V2.14/V3/V4 RT-BarnesHut speed table;
- public speedup claims;
- broad V4 high-performance claims;
- claim that this is identical to the authors' OWL implementation;
- claim that tree construction is device-resident or no-copy.

## Next Engineering Work

Goal4766 should make the same route benchmark-ready:

1. Split cold pipeline-init time from warm execution in the formal probe.
2. Add a 32768-point and 1M-point scale gate.
3. Compare against the authors' binary on the same POD and dataset only after
   the scale gates pass.
4. Decide whether the current custom-primitive approximation of the authors'
   triangle control geometry is sufficient for external paper-reproduction
   review.

## Goal-Level Decision Audit

1. Was I foolish?
   - Partly. I initially used `std::unique_ptr<PipelineHolder>` for the new
     global pipeline even though existing OptiX pipeline globals use raw
     pointers to avoid shutdown-order crashes.

2. What action made that foolish?
   - I copied the local C++ ownership style I wanted instead of following the
     surrounding OptiX runtime pattern. The POD probe passed checksum but
     segfaulted at process exit.

3. Was there another path?
   - Yes. Read the nearby `g_rayclosest3d` and related pipeline globals first,
     then match the raw-pointer pattern from the start.

4. What different path is now active?
   - The pipeline now uses the existing raw-pointer pattern. The rebuilt POD
     library runs the 4096/8192 probes cleanly with exit code 0 and no segfault.
