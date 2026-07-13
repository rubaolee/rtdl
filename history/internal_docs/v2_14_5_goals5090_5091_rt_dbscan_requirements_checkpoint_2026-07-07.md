# v2.14.5 Goals5090-5091 RT-DBSCAN Requirements Checkpoint

Date: 2026-07-07

## Verdict Label

```text
completed_v2_14_5_rt_dbscan_requirements_checkpoint_goals5090_5091
```

## Scope

This checkpoint covers:

```text
Goal5090 RT-DBSCAN requirements audit and first bounded target
Goal5091 RT-DBSCAN AuthorOfficial build/run plan
```

It advances the third paper app from scaffold-only to a concrete first local
gate and a POD-ready author-comparator plan.

## Goal5090 Summary

Created:

```text
Paper-reproduction-apps/rt-dbscan-paper/scripts/run_core_count_smoke.py
history/internal_docs/goal5090_rt_dbscan_requirements_audit_and_first_target_2026-07-07.md
history/internal_docs/call_for_review_goal5090_rt_dbscan_requirements_audit_and_first_target_2026-07-07.md
```

Updated:

```text
Paper-reproduction-apps/rt-dbscan-paper/README.md
Paper-reproduction-apps/rt-dbscan-paper/data/manifest.json
Paper-reproduction-apps/rt-dbscan-paper/scripts/README.md
```

Main result:

- Located candidate author artifact:
  - repository: `https://github.com/vani-nag/OWLRayTracing`
  - branch: `rt-dbscan`
  - commit: `92749fe82ed001e5b7303265d4a2a73aa1bbf529`
  - sample path: `samples/cmdline/s02-rtdbscan`
- Selected first bounded target:
  - fixed-radius `core_count` smoke.
- Added a local RTDL/oracle smoke wrapper.
- Ran it successfully:
  - `core_count=7`
  - `oracle_core_count=7`
  - `matches_oracle=true`
  - `author_comparator_used=false`

## Goal5091 Summary

Created:

```text
history/internal_docs/goal5091_rt_dbscan_authorofficial_build_run_plan_2026-07-07.md
history/internal_docs/call_for_review_goal5091_rt_dbscan_authorofficial_build_run_plan_2026-07-07.md
```

Updated:

```text
Paper-reproduction-apps/rt-dbscan-paper/README.md
Paper-reproduction-apps/rt-dbscan-paper/results/README.md
```

Main result:

- Inspected the author sample command shape:

```text
./sample02-rtdbscan [inFile] [size] [eps] [minPts] [outFile]
```

- Identified the comparator gap:
  - the author sample writes timing output,
  - cluster output exists in source but is commented out,
  - therefore a minimal AuthorOfficial comparator patch is required before
    same-input correctness can be claimed.
- Chose `core_count` as the first AuthorOfficial comparator target.
- Deferred component signatures and cluster labels until after the core-count
  gate.

## Verification

Commands:

```text
py Paper-reproduction-apps/rt-dbscan-paper/scripts/run_core_count_smoke.py --summary Paper-reproduction-apps/rt-dbscan-paper/results/core_count_smoke_summary.json
py -m json.tool Paper-reproduction-apps/rt-dbscan-paper/data/manifest.json
py -m json.tool Paper-reproduction-apps/rt-dbscan-paper/results/core_count_smoke_summary.json
py -m py_compile Paper-reproduction-apps/rt-dbscan-paper/scripts/run_core_count_smoke.py
```

All passed. The local Python launcher printed its known prefix warning, but
returned success.

Public paper-app leak scan returned:

```text
0 matches
```

for:

```text
Goal[0-9]+
call_for_review
Antigravity
Claude
Gemini
review debt
verdict
```

## Claim Boundary

This checkpoint does not claim:

- author artifact build success,
- AuthorOfficial comparator success,
- exact paper input recovery,
- RT-DBSCAN paper reproduction,
- whole-program DBSCAN speedup,
- native DBSCAN engine ABI,
- automatic route selection,
- full cluster-label parity.

## Next Recommended Goal

Goal5092 should create a POD-ready AuthorOfficial core-count patch/run packet:

1. generate a tiny 3D input fixture,
2. patch author `hostCode.cpp` to emit `core_count`,
3. build `sample02-rtdbscan`,
4. run author and RTDL on the same input,
5. compare integer `core_count`,
6. record compatibility patches and non-claims.
