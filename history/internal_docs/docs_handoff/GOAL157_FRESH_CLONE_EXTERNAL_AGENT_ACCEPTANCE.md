# Goal 157 Fresh-Clone External Agent Acceptance

## Mission

You are acting as an independent external acceptance tester for RTDL v0.2.

Your job is to prove or disprove that current `main` is usable from a **fresh
Linux clone** by writing and running a small RTDL program of your own.

This is not a repo-review task.
This is a clean-room usability and execution task.

## Host And Repo

- Host: `lestat@192.168.1.20`
- Canonical repo URL: `https://github.com/rubaolee/rtdl.git`

You must use a **totally new directory** on the Linux host.

Example:

- `/tmp/rtdl_goal157_agent_<your_name>_<timestamp>`

Do **not** use the existing shared working tree under:

- `/home/lestat/work/rtdl_python_only`

## Hard Requirements

1. SSH to the Linux host.
2. Create a totally new directory.
3. `git clone` the repo into that directory.
4. Build what your task needs from that fresh clone.
5. Write your **own** RTDL program in the fresh clone.
6. Run it successfully.
7. Write a structured report.

## What Counts As "Your Own Program"

It is fine to import RTDL and follow existing style patterns, but your program
must be a new file that you author in the fresh clone.

It must not be just:

- running an existing example unchanged
- repeating a canned command with no authored logic

## Platform Honesty Rules

- Linux is the primary accepted validation platform.
- Do not claim this proves Mac closure.
- Do not claim native Jaccard Embree/OptiX/Vulkan kernels.
- If your chosen Jaccard workload runs through public Embree/OptiX/Vulkan
  surfaces, remember that current acceptance is still through documented native
  CPU/oracle fallback for that line.

## Choose One Task

Pick one of the following tasks and carry it through end-to-end.

### Task A: Points Wrapped By More Than Three Polygons

Author a small RTDL program that:

- takes points and polygons
- determines how many polygons cover each point
- emits only points covered by more than three polygons

Suggested output fields:

- `point_id`
- `cover_count`

This can be implemented by using current supported surfaces plus host-side
post-processing if needed, but the core query must still be expressed as an
RTDL program.

### Task B: Segment Hazard Rows

Author a small RTDL program that:

- takes road-like segments and hazard polygons
- emits one row per segment/polygon hit
- then computes a simple downstream summary such as:
  - how many hazards touched each segment
  - or which segments touched at least two hazards

Suggested workload basis:

- `segment_polygon_anyhit_rows`

### Task C: Pathology-Style Similarity Check

Author a small RTDL program that:

- constructs or derives two small polygon sets
- computes overlap rows or whole-set similarity
- prints an interpretable summary

Suggested workload basis:

- `polygon_pair_overlap_area_rows`
- or `polygon_set_jaccard`

### Task D: Your Own Small Spatial Program

You may define your own RTDL program if it stays within the currently accepted
v0.2 workload surface:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

If you choose this option, explain clearly why the program is meaningful as an
independent acceptance test.

## Minimum Execution Requirements

Your report must include:

1. the fresh Linux clone path
2. the commit checked out
3. the exact build commands you ran
4. the exact program file you authored
5. the exact run command you used
6. whether the program succeeded
7. the result rows or summary
8. whether any repair/workaround was needed
9. whether you believe this supports v0.2 release readiness

## Preferred Backend Use

Use at least:

- `cpu_python_reference`
- and one additional backend or run surface that is actually available in your
  fresh clone environment

Examples:

- `cpu`
- `embree`
- `optix`
- `vulkan`

If a backend is unavailable, say so explicitly instead of hiding it.

## Report Format

Return a report with exactly these sections:

1. `Task`
2. `Fresh Clone`
3. `Build`
4. `Authored Program`
5. `Execution`
6. `Result`
7. `Problems`
8. `Release Verdict`

## Success Standard

Success means:

- you really used a fresh Linux clone
- you authored a new RTDL program
- you ran it successfully
- your report is detailed enough that we can judge whether v0.2 is ready for
  release

If you fail, report the failure honestly.
