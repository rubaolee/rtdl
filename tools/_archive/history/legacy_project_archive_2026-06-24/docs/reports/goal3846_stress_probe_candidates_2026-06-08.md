# Goal3846 Stress Probe Candidates

Date: 2026-06-08

Status: internal performance triage, not release authorization

## Purpose

Goal3846 uses the live A5000 pod after Goal3844 to stress a few rows that look
too small or too marginal in the default scale-profile packet. The goal is not
to produce a new ten-app public table. The goal is to decide where major
performance engineering should go next.

## Pod Evidence

Artifact directory:

- `docs/reports/goal3846_stress_probe_candidates_a5000/`

Execution context:

- GPU: NVIDIA RTX A5000
- commit: `9c5dcb29552c`
- env: `PYTHONPATH=.pydeps_goal3788_numba:src:.`,
  `RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so`,
  `RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so`

The pod initially held untracked Goal3844 artifacts from the prior run. They
were moved to `/root/rtdl_pod_untracked_backup_goal3846_*` before the
fast-forward. Nothing was deleted.

## Results

| Probe | Command shape | App-reported hot metric | Process observation |
| --- | --- | ---: | --- |
| `raydb_count_4m_repeat50` | 4,194,304 generated rows, 4,096 groups, 50 repeats | 0.004667s | completed in ~11s wall including setup/output |
| `raydb_sum_4m_repeat50` | 4,194,304 generated rows, 4,096 groups, 50 repeats | 0.028225s | completed in ~25s wall including setup/output |
| `librts_131k_repeat10` | 131,072 boxes and 131,072 queries, 10 hot repeats | 0.646093s median query | 6.463s summed query time |
| `triangle_native_8192_repeat5` | native graph triangle summary, 8,192 copies | 0.826945s raw native view | remains not an RT-core graph claim |

All four probes completed with return code 0 and empty row stderr files.

## Interpretation

RayDB is not the next best primitive-runtime target. At 4M generated rows, the
fused generic grouped-reduction primitive reports very small hot-query times for
both count and sum, with CPU-reference parity. The process wall is dominated by
fixture construction, validation, JSON, and startup. Improving RayDB from here
is mostly about better long-run harness accounting or full application
pipeline work, not a clear missing RTDL primitive.

LibRTS is more interesting. At 131k boxes/queries the generic prepared AABB
index query produces seconds-level hot work (`0.646s` median across the three
operations). That row is RT-core accelerated and therefore a plausible future
scale/perf target if we want another major primitive improvement.

Triangle counting remains a boundary row. The larger native route finishes, but
it still reports `rt_core_accelerated=false` and describes the route as a
host-indexed/native summary correctness path. If we want a major graph app
improvement, the next work is a genuine generic graph-cycle RT mapping rather
than another small benchmark knob.

Barnes-Hut remains a separate structural project. Goal3844 confirms the Numba
exact-force reference runs, but the real leap would require hierarchical
aggregate-frontier vector reductions, not this stress packet.

## Next Engineering Direction

Recommended priority after this probe:

1. Do not spend the next round on RayDB fused count/sum. The hot primitive is
   already fast at larger row count.
2. If using the current A5000 for more perf work, target LibRTS scale behavior
   or graph/triangle semantics.
3. Keep Barnes-Hut on the roadmap as a larger hierarchical vector-primitive
   effort.
4. Preserve the current Numba-reference story: RT-DBSCAN and Barnes-Hut have
   no-RawKernel Numba references; RayDB/LibRTS/triangle promoted rows are
   primitive-first.

## Boundary

Goal3846 does not authorize release action, public speedup wording, paper
reproduction wording, broad RT-core wording, true-zero-copy wording, automatic
partner/backend selection, or app-specific native-engine logic.
