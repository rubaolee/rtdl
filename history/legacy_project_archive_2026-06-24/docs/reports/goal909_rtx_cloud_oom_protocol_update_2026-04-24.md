# Goal909: RTX Cloud OOM Protocol Update

Date: 2026-04-24

## Incident Summary

An RTX A5000 pod was started for the v0.9.8/v1.0 NVIDIA RT-core app batch.

Observed environment:

- GPU: NVIDIA RTX A5000, 24564 MiB VRAM
- Driver: `550.127.05`
- CUDA: `12.4`
- Python: `3.11.10`
- Source commit staged to pod: `b2190ab`

## What Worked

- SSH worked with `~/.ssh/id_ed25519_rtdl_codex`.
- Clean source sync to `/workspace/rtdl_python_only` worked.
- OptiX SDK header compatibility was resolved by using `optix-dev` tag `v8.0.0`.
- With OptiX 8.0 headers and CUDA 12.4, `make build-optix` passed.
- The focused OptiX bootstrap test suite passed:

```text
Ran 30 tests in 2.547s
OK
```

## Issues Found

### 1. Real OptiX DB Compile Bug

`make build-optix` initially failed:

```text
src/native/optix/rtdl_optix_workloads.cpp:695:78:
error: 't_start_trav' was not declared in this scope
```

Root cause: the prepared DB OptiX path recorded traversal end time but missed
the traversal start timestamp. The cloud compile diagnostic line number came
from the pod copy of the file; local line numbers can differ after subsequent
edits. The relevant function is
`db_collect_candidate_row_indices_optix_prepared`.

Local fix applied:

```cpp
CUstream stream = 0;
auto t_start_trav = std::chrono::steady_clock::now();
OPTIX_CHECK(optixLaunch(...));
```

Additional local guard:

- `tests/goal829_rtx_cloud_single_session_runbook_test.py` now statically
  verifies that `db_collect_candidate_row_indices_optix_prepared` has
  `t_start_trav` before `optixLaunch` and `t_end_trav` after `optixLaunch`.

### 2. OptiX ABI Compatibility

The pod driver rejected OptiX 9.0 and 8.1 headers with:

```text
OptiX error: Unsupported ABI version
```

Header ABI versions observed:

- OptiX 9.0: ABI `105`
- OptiX 8.1: ABI `93`
- OptiX 8.0: ABI `87`

OptiX 8.0 worked with driver `550.127.05`.

### 3. Full Active+Deferred Batch Is Too Risky

The full 17-entry active+deferred batch ran for about 59 minutes without
completion output. New SSH probes timed out during banner exchange. The user
confirmed an out-of-memory event happened on the cloud side.

Conclusion: the full batch is not acceptable for paid cloud execution. It is
too opaque and too fragile. A single high-memory workload can hang the pod and
hide all progress. The new protocol reduces blast radius and preserves
artifacts; it does not prove that every individual workload is memory-safe at
large scale until each group is actually run on cloud.

## Protocol Change

`docs/rtx_cloud_single_session_runbook.md` now requires:

- bootstrap first;
- one OOM-safe group at a time;
- immediate artifact copy after each group;
- smaller initial scale for prepared decision apps;
- no blind full active+deferred manifest run.

The new groups are:

| Group | Workloads |
| --- | --- |
| A | Robot flagship |
| B | Outlier + DBSCAN fixed-radius summaries |
| C | Database analytics |
| D | Spatial prepared summaries |
| E | Segment/polygon + road gates |
| F | Graph gate |
| G | Hausdorff, ANN, Barnes-Hut prepared decision apps at smaller initial scale |
| H | Polygon overlap/Jaccard native-assisted gates |

## Boundary

This report documents a cloud execution failure and protocol update. It does not
authorize any NVIDIA RT-core performance claim.

The only positive cloud result so far is environment/bootstrap evidence:

- RTX A5000 present,
- OptiX 8.0 compatible with driver 550,
- focused OptiX tests passed after the local compile fix.

Benchmark artifacts from the OOMed full batch must not be used as performance
evidence.
