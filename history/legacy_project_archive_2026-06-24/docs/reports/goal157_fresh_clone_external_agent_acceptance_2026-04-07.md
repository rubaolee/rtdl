# Goal 157 Fresh-Clone External Agent Acceptance

## Verdict

Frozen RTDL v0.2 passed a meaningful fresh-clone external acceptance check on
the primary Linux platform.

The strongest result is not just that existing examples run.
It is that independent agents were able to:

- create totally new Linux clone directories
- `git clone` current `main`
- author new RTDL programs of their own
- run those programs successfully
- report usable results

## Acceptance Packet

Fresh Linux host:

- `lestat@192.168.1.20`

Commit under test:

- `ec1174e`

Successful fresh-clone acceptance runs:

### Task A: Points Covered By More Than Three Polygons

Fresh clone:

- `/tmp/rtdl_goal157_uJG0vr/agent_a`

Authored program:

- `examples/rtdl_goal157_point_cover_over_three.py`

Approach:

- used a `point_in_polygon` / `contains` style RTDL kernel
- emitted positive point/polygon hits
- counted hits per point on the host
- filtered to points covered by more than three polygons

Backends run successfully:

- `cpu_python_reference`
- `cpu`

Observed result:

- total emitted hit rows: `7`
- hit counts by point:
  - point `1`: `4`
  - point `2`: `3`
- points covered by more than three polygons:
  - `[1]`

Important honesty note:

- this was an accepted existing RTDL surface plus host-side aggregation
- not a new first-class workload family

### Task B: Segment Hazard Summary

Fresh clone:

- `/tmp/rtdl_goal157_task_b.DP1iD3/repo`

Authored program:

- `task_b_road_hazard_summary.py`

Approach:

- used `segment_polygon_anyhit_rows`
- computed a downstream segment hazard summary

Backends run successfully:

- `cpu_python_reference`
- `optix`

Observed result:

- `rows_match = True`
- `summary_match = True`
- any-hit rows found: `5`
- segment hit counts:
  - segment `1`: `2`
  - segment `2`: `1`
  - segment `3`: `2`
- hot segments:
  - `[1, 3]`

Additional build evidence:

- `make build-optix` succeeded in the fresh clone before execution

Important note:

- one earlier comparison mismatched only at whole-payload metadata level
- the meaningful RTDL rows and summary still matched, and the final check was
  done on those result surfaces directly

### Task C: Pathology-Style Similarity Check

Fresh clone:

- `/tmp/rtdl_goal157_taskc_20260407_093157/repo`

Authored program:

- `examples/goal157_pathology_similarity_check.py`

Approach:

- used `polygon_pair_overlap_area_rows`
- and `polygon_set_jaccard`
- printed pair rows and a whole-set similarity summary

Backends run successfully:

- `cpu_python_reference`
- `cpu`

Observed result:

- matching pair rows across both backends
- matching Jaccard summary across both backends
- `jaccard_similarity = 0.25925925925925924`

One real development note:

- the first authored attempt returned a dict directly from the RTDL kernel
- this was corrected by rewriting into two single-`rt.emit(...)` kernels
- the rerun then succeeded

## Build Evidence

From the fresh clones:

- `python3 -m compileall ...` worked for the authored scripts
- `PYTHONPATH=src:. python3 -c "import rtdsl as rt; print(rt.oracle_version())"`
  returned `(0, 1, 0)`
- the native oracle library was created in the fresh clone:
  - `build/librtdl_oracle.so`
- `make build-optix` also succeeded in a fresh Linux clone for Task B

No shared working tree under `/home/lestat/work/rtdl_python_only` was used for
the acceptance runs.

## Interpretation

This is strong release evidence because it is closer to real user behavior than
our internal example and audit loop:

- fresh clone
- new authored program
- end-to-end execution
- honest reporting of one small rewrite when the first Jaccard attempt used the
  wrong kernel return shape

It does **not** prove every backend/workload combination equally.
But it does support the more important release question:

- can a fresh Linux user/agent actually pick up RTDL v0.2 and make it do
  something new?

For the tested accepted surfaces, the answer here is:

- **yes**

## Release Verdict

This increases confidence that frozen RTDL v0.2 is ready for release.

The acceptance packet shows that multiple independent authored-program tasks can
be completed successfully from fresh Linux clones on current `main`.
