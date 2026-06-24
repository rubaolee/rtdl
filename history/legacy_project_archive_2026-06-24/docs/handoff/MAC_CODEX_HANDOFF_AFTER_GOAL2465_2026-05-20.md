# Mac Codex Handoff After Goal2465

Date: 2026-05-20

Purpose: resume RTDL v2.x benchmark/runtime work from Mac Codex without losing
the current Windows/pod state.

## Start Here

1. Read `/Users/rl2025/rtdl_python_only/CODEX.md` or the project refresh file
   available on the Mac side if present. On Windows the durable refresh file is:
   `C:\Users\Lestat\Desktop\refresh.md`.
2. Work on `main`.
3. Pull the latest pushed state:

```bash
cd /Users/rl2025/rtdl_python_only
git fetch origin main
git pull --ff-only origin main
git log -5 --oneline
```

Expected latest commit after this handoff is committed:

```text
<handoff-commit> Mac handoff after Goal2465
aad3794f Goal2465 cull grouped union all-items intersections
03d6e140 Goal2463 add grouped union all-items path
80f10d01 Goal2461 add grouped stream self-query path
c98acbc1 Goal2459 threshold-cap grouped stream core flags
22a96c6f Goal2457 add grouped stream continuation
```

## Roadmap And Rules

- RTDL engine must remain app-agnostic. Do not add DBSCAN-native ABI or app
  vocabulary inside native engines.
- App/domain logic belongs in Python examples/adapters/benchmark code.
- Important performance or architecture claims require external AI review.
- Key release decisions require 3-AI consensus.
- Do not touch historical untracked tarball:
  `docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz`.
- Do not move release tags.
- Do not claim package-install support unless packaging metadata exists and is
  validated.
- Capture future-version ideas in
  `docs/research/future_version_to_do_list.md`.

## What Just Landed

### Goal2461

Commit: `80f10d01 Goal2461 add grouped stream self-query path`

Added a prepared self-query device path for generic fixed-radius grouped union:

- native symbol:
  `rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs`
- Python runtime method:
  `PreparedOptixFixedRadiusCountThreshold3D.apply_device_grouped_union_self(...)`
- Result: removed grouped-stream self-query host repack/upload.

RTX A5000 pod steady tail medians:

```text
32,768 clustered3d: 0.072831 -> 0.029680 sec
65,536 clustered3d: 0.218252 -> 0.095882 sec
```

Gemini review:

```text
docs/reviews/goal2462_gemini_review_goal2461_grouped_stream_self_query_2026-05-20.md
```

### Goal2463

Commit: `03d6e140 Goal2463 add grouped union all-items path`

Added a generic all-items-eligible mode for prepared fixed-radius self-query
grouped union. If the threshold-capped count pass proves every item is
predicate-true, Python passes null predicate/fallback pointers into the existing
generic native self-query symbol and native anyhit unions every `target > source`
hit.

Important boundary: this is generic all-items predicate mode, not DBSCAN native
logic.

RTX A5000 pod same-shape comparison:

```text
32,768 clustered3d: 0.029410 -> 0.029944 sec
  mixed predicate row, old predicated path correctly used
65,536 clustered3d: 0.096906 -> 0.085654 sec
  all-items path used
```

Evidence and review:

```text
docs/reports/goal2463_grouped_union_all_items_path_2026-05-20.md
docs/reports/goal2463_grouped_union_baseline_pod/summary.json
docs/reports/goal2463_grouped_union_all_items_pod/summary.json
docs/reviews/goal2464_gemini_review_goal2463_grouped_union_all_items_path_2026-05-20.md
tests/goal2463_grouped_union_all_items_path_test.py
```

Rejected experiment: path-compressing root lookup was tested before Goal2463 and
reverted because it slowed the 65,536 row (`~0.0969 -> ~0.1025 sec`).

### Goal2465

Commit: `aad3794f Goal2465 cull grouped union all-items intersections`

Moved the all-items `target > source` condition earlier into the OptiX
intersection program:

```cpp
const uint32_t source = params.query_index_offset + qidx;
if (params.all_predicate != 0u && prim <= source) {
    return;
}
```

This avoids reporting intersections that anyhit would ignore anyway.

RTX A5000 pod comparison against Goal2463:

```text
32,768 clustered3d: 0.029944 -> 0.029642 sec
65,536 clustered3d: 0.085654 -> 0.079455 sec
```

Evidence and review:

```text
docs/reports/goal2465_grouped_union_all_items_intersection_cull_2026-05-20.md
docs/reports/goal2465_grouped_union_all_items_intersection_cull_pod/summary.json
docs/reviews/goal2466_gemini_review_goal2465_all_items_intersection_cull_2026-05-20.md
tests/goal2465_grouped_union_all_items_intersection_cull_test.py
```

## Current Best RT-DBSCAN State

Current dense clustered row, after Goal2465:

```text
65,536 clustered3d grouped stream tail median: 0.079455 sec
native grouped-union tail median: 0.079016 sec
predicate mode: all_items_true_no_fallback_candidates
transfer mode: prepared_device_search_points_self_grouped_union_all_items_parent_workspace
tiny smoke: matches reference
```

Compared to Goal2461 baseline (`0.095882 sec`), this is about `1.21x` faster.
Compared to Goal2459 before self-query (`0.218252 sec`), this is about `2.75x`
faster.

## Validation Already Run

Windows local:

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest `
  tests.goal2465_grouped_union_all_items_intersection_cull_test `
  tests.goal2463_grouped_union_all_items_path_test `
  tests.goal2461_grouped_stream_self_query_device_path_test `
  tests.goal2459_grouped_stream_threshold_capped_core_flags_test `
  tests.goal2457_generic_grouped_stream_continuation_implementation_test `
  tests.goal2437_rt_dbscan_explicit_continuation_planner_test
```

Result:

```text
Ran 25 tests in 0.055s - OK
```

Python compile check:

```powershell
py -3 -m py_compile `
  src\rtdsl\partner_adapters.py `
  src\rtdsl\optix_runtime.py `
  examples\v2_0\research_benchmarks\rt_dbscan\rtdl_rt_dbscan_benchmark_app.py
```

Pod:

```text
GPU: NVIDIA RTX A5000
Driver: 570.211.01
CUDA: /usr/local/cuda-12, nvcc 12.8
OptiX SDK: /root/vendor/optix-sdk
```

Build command:

```bash
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk CUDA_PREFIX=/usr/local/cuda-12
```

Focused pod tests passed for Goal2465:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2463_grouped_union_all_items_path_test \
  tests.goal2461_grouped_stream_self_query_device_path_test
```

Result:

```text
Ran 9 tests in 0.008s - OK
```

## Current Windows Working Tree Dirt

Do not assume a clean tree on Windows. After pushing Goal2465, unrelated dirt
remained:

```text
 M docs/reviews/goal2061_gemini_review_goal2060_v2_pod_mixed_family_audit_2026-05-15.md
?? Lib/
?? docs/handoff/... older handoffs
?? docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz
?? multiple historical docs/reports and docs/reviews
?? id_ed25519_rtdl_codex
?? rtdl_v0_4.tar.gz
?? run_review_tests.py
?? scratch/
?? scripts/pip3.11.exe
?? scripts/pip3.exe
?? tests/goal2079_current_commit_optix_rt_perf_refresh_test.py
```

These were not part of Goal2463 or Goal2465 and should not be reverted or swept
into unrelated commits.

## Next Engineering Target

The next real performance problem is not more tiny root-lookup tuning. Evidence
points to global atomic pressure in grouped union.

Recommended next goal:

```text
Generic blocked/segmented grouped continuation for fixed-radius hit streams.
```

Design direction:

- Keep the primitive generic: fixed-radius hit stream -> grouped union or
  grouped continuation, not DBSCAN.
- Reduce global atomic pressure by staging hits by query block, cell block, or
  segment before global parent updates.
- Preserve direct device workspaces and explicit metadata:
  `native_execution_path`, `predicate_mode`, `transfer_mode`,
  `rt_core_accelerated`, claim boundaries.
- Maintain planner discipline: choose full adjacency, chunked adjacency,
  grouped-stream, all-items grouped-stream, or future blocked grouped-stream
  based on explicit evidence and memory budget.
- Keep pod measurements large enough to run for real seconds only when needed;
  otherwise develop on local/Linux/Mac with static tests and small smokes.

Possible Goal2467 starting point:

```text
Goal2467: design and test a generic blocked grouped-continuation plan.
Deliverables: report, static tests, maybe a prototype CuPy/OptiX-adjacent
simulation before native changes. Do not add DBSCAN-native ABI.
```

## Useful Commands On Mac

Static/focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2465_grouped_union_all_items_intersection_cull_test \
  tests.goal2463_grouped_union_all_items_path_test \
  tests.goal2461_grouped_stream_self_query_device_path_test \
  tests.goal2459_grouped_stream_threshold_capped_core_flags_test \
  tests.goal2457_generic_grouped_stream_continuation_implementation_test \
  tests.goal2437_rt_dbscan_explicit_continuation_planner_test
```

Broad test discovery if time allows:

```bash
PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'
```

Search:

```bash
rg "grouped_union|all_predicate|grouped_stream|radius_graph_components_3d" src tests docs
```

## One-Sentence Resume Prompt

Please read `docs/handoff/MAC_CODEX_HANDOFF_AFTER_GOAL2465_2026-05-20.md`, pull latest `main`, and continue RTDL v2.x RT-DBSCAN work toward a generic blocked/segmented grouped-continuation primitive without adding any DBSCAN-specific native ABI.
