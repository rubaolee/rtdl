# Goal4767 - RT-BarnesHut 10M Scale Gate

Date: 2026-06-26

Status: **completed as 10M scale evidence, pending external review debt**

## Purpose

Run the native V4 RT-BarnesHut author-semantics RT-core candidate at 10M
Treelogy scale against the authors' binary on the same POD, or produce a
concrete blocker if 10M cannot complete.

Goal4767 completed the 10M run. It found both a real positive result and a real
remaining blocker.

## Evidence

`future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4767_benchmark_ready_10m_pod_2026-06-26.json`

POD:

```text
NVIDIA RTX A5000
V4 root: /root/rtdl_v4_candidate_pod
Dataset: /root/external/RT-BarnesHut-author/treelogy_synthetic_10M.txt
Author binary: /root/external/RT-BarnesHut-author/build/rtbarneshut
```

Probe:

```bash
scripts/v4_rt_barneshut_native_benchmark_ready_probe.py \
  --goal-label Goal4767 \
  --dataset /root/external/RT-BarnesHut-author/treelogy_synthetic_10M.txt \
  --file-type treelogy \
  --limit 10000000 \
  --repeat 2 \
  --author-binary /root/external/RT-BarnesHut-author/build/rtbarneshut
```

## Result

Correctness:

- native force checksum: `53.746751351154444`;
- author RT force checksum: `53.7468`;
- checksum relative error: `9.051486889720442e-7`;
- passes tolerance: true.

Native route status:

- `implementation_status_code=3`;
- `rt_core_execution=true`;
- `host_fallback_used=false`;
- `input_columns_downloaded_for_tree_build=true`.

Timing:

| Metric | Native V4 Candidate | Authors' Binary |
|---|---:|---:|
| Warm RT-force seconds | `0.906343331` | `1.01614` |
| Warm execution seconds | `7.130341762` | `1.61694` |
| Native preprocessing seconds | `6.179594029` | n/a |
| Author preprocessing seconds | n/a | `0.520493` |
| Author wall seconds | n/a | `23.374203827232122` |

## Interpretation

Goal4768 correction:

- The authors' printed `Preprocessing Time` is not directly comparable to
  RTDL's native `preprocessing_seconds`.
- The authors' binary reports `treeToDFSTime + installAutoRopesTime +
  intersectionsSetupTime` for that field; it does not include the authors'
  sort/tree-build phase.
- The complete-workflow conclusion below remains true, but the precise
  bottleneck statement is refined by Goal4768: RTDL's dominant measured
  bottleneck is host-side z-order sorting.

The RT-force kernel path is real and competitive:

- At 10M, the native V4 RT-force region is slightly faster than the authors'
  binary RT-force region on the same POD and same input.
- The checksum matches the authors' RT checksum within tolerance.

The complete workflow is **not yet competitive**:

- Native V4 full execution is much slower than the authors' binary execution at
  10M.
- The dominant blocker is native preprocessing/tree build:
  `6.179594029s` native preprocessing versus `0.520493s` author preprocessing.
- This is caused by the current V4 route building author-style tree metadata
  from a host snapshot of device columns. The route is an RT-core candidate, but
  not a device-resident or no-copy tree-build implementation.

## What This Means For V4

Goal4767 is a serious-scale success for the RT-core force candidate, not a full
paper-reproduction release success.

Allowed internal statement:

> At 10M Treelogy scale on the RTX A5000 POD, RTDL V4's native
> author-semantics RT-core candidate matches the authors' RT checksum and has a
> slightly faster warm RT-force region, but the full workflow is still blocked
> by slower host-side preprocessing/tree construction.

Still unauthorized:

- public RT-BarnesHut paper-reproduction claim;
- public speedup claim;
- V2/V3/V4 RT-BarnesHut speed table;
- no-copy or device-resident tree-build claim;
- broad V4 release/high-performance claim based on this route.

## Next Engineering Work

Goal4768 should target the actual 10M blocker:

1. Profile and reduce the V4 preprocessing/tree-build path.
2. Compare the native tree-build algorithm and data movement to the authors'
   preprocessing path.
3. Decide whether to:
   - optimize the current host preprocessing path;
   - move tree metadata construction toward device-resident staging;
   - or bind/port the authors' exact preprocessing path more literally.
4. Re-run 10M only after preprocessing changes, using the same checksum and
   cold/warm split.

## Goal-Level Decision Audit

1. Was I foolish?
   - No for the main decision. Running 10M was the right test because 1M still
     left open whether the route was only a small/medium-scale success.

2. What action would have made it foolish?
   - Claiming success from the RT-force number alone would be foolish, because
     full execution is currently slower than the authors' binary.

3. Was there another path?
   - Yes: stop at 1M and ask for review. That would have missed the
     preprocessing bottleneck that appears clearly at 10M.

4. What different path is now active?
   - Treat the RT-force path as real, but make preprocessing/tree construction
     the next bottleneck target before any public paper-reproduction or speed
     wording.
