# Goal4768 - RT-BarnesHut Preprocessing Sort Bottleneck

Date: 2026-06-26

Status: **completed as bottleneck localization, pending external review debt**

## Purpose

Goal4768 followed Goal4767's 10M Treelogy result. The task was to determine
why the native V4 RT-BarnesHut author-semantics route has a competitive warm
RT-force region, but a much slower full workflow than the authors' binary.

The goal also corrected one important accounting issue: the authors' printed
`Preprocessing Time` in the current binary is not directly comparable to RTDL's
native `preprocessing_seconds`.

## Evidence

Primary evidence:

- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4768_benchmark_ready_10m_pod_2026-06-26.json`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4768_10m_phase_profile_pod_2026-06-26.jsonl`

POD:

```text
NVIDIA RTX A5000
V4 root: /root/rtdl_v4_candidate_pod
Dataset: /root/external/RT-BarnesHut-author/treelogy_synthetic_10M.txt
Author binary: /root/external/RT-BarnesHut-author/build/rtbarneshut
```

Probe:

```bash
RTDL_RT_BARNESHUT_AUTHOR_PROFILE_JSONL=\
future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4768_10m_phase_profile_pod_2026-06-26.jsonl \
scripts/v4_rt_barneshut_native_benchmark_ready_probe.py \
  --goal-label Goal4768 \
  --dataset /root/external/RT-BarnesHut-author/treelogy_synthetic_10M.txt \
  --file-type treelogy \
  --limit 10000000 \
  --repeat 2 \
  --author-binary /root/external/RT-BarnesHut-author/build/rtbarneshut
```

## Code Changes

`src/native/optix/rtdl_optix_api.cpp` now emits optional phase-level profiling
when `RTDL_RT_BARNESHUT_AUTHOR_PROFILE_JSONL` is set. The profile records:

- input download;
- point packing;
- z-order sort;
- grid and bucket construction;
- tree insertion;
- center-of-mass computation;
- DFS metadata;
- auto-ropes;
- OptiX pipeline initialization;
- device packing;
- AABB generation;
- upload;
- acceleration build;
- launch.

The native tree builder was also changed from `std::stable_sort` to
`std::sort`. This is safe because the RTDL comparator already includes
`original_id` as a tie-breaker, and the authors' source also uses `std::sort`.
The rerun showed that this change does not solve the 10M bottleneck.

## Correctness

The 10M checksum still matches the authors' RT checksum:

- native force checksum: `53.746751351154444`;
- author RT force checksum: `53.7468`;
- checksum relative error: `9.051486889720442e-7`;
- tolerance pass: true.

Native route status remains:

- `implementation_status_code=3`;
- `rt_core_execution=true`;
- `host_fallback_used=false`;
- `input_columns_downloaded_for_tree_build=true`.

## Timing Result

| Metric | Native V4 Candidate | Authors' Binary |
|---|---:|---:|
| Warm RT-force seconds | `0.886653679` | `1.0172` |
| Warm execution seconds | `7.432850354` | `1.68573` |
| Native preprocessing seconds | `6.503060236` | not directly reported |
| Author printed preprocessing seconds | not comparable | `0.587772` |

Important accounting correction:

- In the current author binary, `Preprocessing Time` is computed from
  `treeToDFSTime + installAutoRopesTime + intersectionsSetupTime`.
- It does **not** include the authors' input sort or tree-build time.
- Therefore `6.503060236s` native preprocessing vs `0.587772s` author printed
  preprocessing is not a fair phase ratio.
- The fair conclusion is still negative for the complete workflow:
  RTDL V4 warm execution is `7.432850354s` vs author execution `1.68573s`.

## Phase Profile

Warm run phase profile:

| Phase | Seconds |
|---|---:|
| input_download | `0.0804588` |
| point_pack | `0.123256` |
| sort | `6.16351` |
| grid | `0.0444316` |
| bucket_build | `0.122523` |
| insert | `0.030328` |
| compute_com | `0.00845067` |
| count_nodes | `0.0105522` |
| dfs_metadata | `0.0150561` |
| auto_rope | `0.0111561` |
| pipeline_init | `0.000006815` |
| device_pack | `0.144908` |
| aabb | `0.00954911` |
| upload | `0.0292855` |
| accel_build | `0.00803325` |
| launch | `0.647495` |

The bottleneck is unambiguous: z-order sorting is about `6.16s`, while tree
insert/center-of-mass/DFS/auto-rope/AABB/upload/accel-build are all much
smaller.

## Interpretation

Goal4768 does not make RT-BarnesHut release-ready. It makes the next work item
precise.

What is now proven:

- The native RT-core force route is real and checksum-valid at 10M.
- The warm RT-force region is competitive with the authors' RT-force region on
  the same input and same POD.
- The full workflow is not competitive.
- The dominant native bottleneck is host-side z-order sorting, not OptiX launch,
  DFS metadata construction, auto-ropes, or acceleration build.

What remains unproven:

- public RT-BarnesHut paper reproduction;
- V2/V3/V4 RT-BarnesHut public speed table;
- no-copy or device-resident tree build;
- full-workflow speedup over the authors' implementation.

## Next Engineering Target

Goal4769 should target the sort bottleneck, with one of two acceptable paths:

1. Build an author-equivalent sort/profile harness so RTDL and the authors'
   code report the same phase boundaries, ideally by rebuilding the author
   binary with sort/tree-build timing visible.
2. Implement a safe RTDL z-order sort improvement, such as precomputed sortable
   keys or an author-equivalent data layout, then rerun the 10M profile and
   checksum gate.

The exit condition for Goal4769 should be concrete:

- either reduce RTDL 10M `sort_seconds` materially without breaking checksum
  parity;
- or prove the sort gap is due to a reporting/accounting difference and
  produce an apples-to-apples author phase table.

## Goal-Level Decision Audit

1. Was I being stupid?
   - Partly, before Goal4768. Goal4767 compared RTDL preprocessing to the
     authors' printed preprocessing as if they were the same phase.

2. What action made it stupid?
   - I did not first inspect the authors' timing aggregation before using their
     printed `Preprocessing Time` as a denominator.

3. Is there another path that avoids a bad premise?
   - Yes. Use phase-level profiling and inspect the author source before
     making any phase-ratio claim.

4. Can I now try the different path that actually solves the problem?
   - Yes. Goal4769 should focus on the measured 10M z-order sort bottleneck and
     on apples-to-apples author phase accounting.
