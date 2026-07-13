# Goal5178 Priority Input Bridge: Graphics Dragon-HappyBuddha

Date: 2026-07-08

## Verdict

```text
completed_priority_input_bridge_graphics_dragon_happy_buddha__level_b_only__implemented_review_pending
```

Goal5178 bridges the Goal5177 priority subset
`graphics_dragon_happy_buddha` to locally acquired public Stanford
Dragon/HappyBuddha files.

This is a strong Level B same-source candidate. It is not exact paper dataset
reproduction, figure reproduction, full paper reproduction, or a performance
ratio.

## Why This Goal Exists

Goal5177 identified `graphics_dragon_happy_buddha` as the most practical first
paper-log-to-route rehearsal target:

- it is a named paper-branch `run_all` pair;
- it is small enough to reason about before the larger geospatial/MRI inputs;
- it is close to the existing Level B Stanford graphics route work.

Goal5178 checks whether the local public Stanford files can be tied to the
author paper-branch log target without pretending to have the author's exact
input bytes.

## Implementation

New script:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_priority_input_bridge.py
```

Command:

```text
py Paper-reproduction-apps\x-hd-paper\scripts\build_xhd_priority_input_bridge.py \
  --app-root Paper-reproduction-apps\x-hd-paper \
  --mapping Paper-reproduction-apps\x-hd-paper\results\xhd_paper_target_log_mapping_goal5177_2026-07-08.json \
  --log-index Paper-reproduction-apps\x-hd-paper\results\xhd_paper_branch_log_index_goal5176_2026-07-08.json \
  --target graphics_dragon_happy_buddha \
  --output Paper-reproduction-apps\x-hd-paper\results\xhd_priority_input_bridge_goal5178_graphics_dragon_happy_buddha_2026-07-08.json
```

## Evidence Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_priority_input_bridge_goal5178_graphics_dragon_happy_buddha_2026-07-08.json
```

Schema:

```text
rtdl.paper_reproduction.xhd.priority_input_bridge.v1
```

Status:

```text
graphics_dragon_happy_buddha_public_stanford_candidate_bridged__level_b_only
```

## Author Log Evidence

The author `paper` branch contains 5 `run_all` records for:

```text
dragon.ply -> happy_buddha.ply
```

Sections:

```text
auto_tune
eb_gpu
hybrid_gpu
rt_gpu
```

Author log fields:

```text
HDResult: 0.12572969496250153

dragon.ply:
  author path: /local/storage/shared/HDDatasets/graphics/dragon.ply
  author logged points: 437645

happy_buddha.ply:
  author path: /local/storage/shared/HDDatasets/graphics/happy_buddha.ply
  author logged points: 543652
```

## Public Stanford Candidate Evidence

Local public Stanford full-resolution candidates:

```text
dragon_recon/dragon_vrip.ply:
  bytes: 33831477
  vertices: 437645
  faces: 871414
  SHA256: FEA87FF48F2ABA22FB53E7B67C3FF3F7B8C2A3B3A0653AF62C48BBA67C6D5744
  point_count_matches_author_log: true

happy_recon/happy_vrip.ply:
  bytes: 42619420
  vertices: 543652
  faces: 1087716
  SHA256: 2283371216D748A08376A3C88698E283CC8F18D10CED348D6D133051BCF217AB
  point_count_matches_author_log: true
```

Source archives:

```text
dragon_recon.tar.gz:
  bytes: 11197764
  SHA256: 74AC1D90989C9B1732EDEE82D57E9CE71452144CF4355F108D8C9C616D28D02F

happy_recon.tar.gz:
  bytes: 14456495
  SHA256: 409CD294EFBFD8244E15A382B95A9423F153B7776E736C9B09F19EC9D3C10ED0
```

The source URLs are recorded in the artifact:

```text
https://graphics.stanford.edu/pub/3Dscanrep/dragon/dragon_recon.tar.gz
https://graphics.stanford.edu/pub/3Dscanrep/happy/happy_recon.tar.gz
```

## Bridge Assessment

```text
all_full_public_candidates_present: true
full_public_candidate_point_counts_match_author_logs: true
strong_same_source_candidate: true
exact_paper_dataset_identity_proved: false
```

The evidence is strong enough for Level B same-source candidate status because
the local public Stanford full PLY vertex counts match the author logs exactly.

It is not strong enough for Level C exact paper dataset status.

## Why Exact Identity Is Not Proved

The artifact records:

```text
author logs provide paths and point counts but not input file hashes
local public files use Stanford archive names, not the author's
  /local/storage/shared/HDDatasets/graphics file bytes
no author conversion script/hash proves byte identity
```

Count matching is useful but not sufficient. This follows the standing X-HD
decision: statistics and counts do not prove exact dataset identity.

## Representative Res4 Context

The artifact also records existing Level B res4 fixtures:

```text
stanford_dragon_res4_full.ply:
  vertices: 5205
  SHA256: 6379312DBCA39B3D1C9858A632512B23F483A99CF9E42727AC61D914C72C25DE

stanford_happy_res4_full.ply:
  vertices: 7108
  SHA256: FDF8E9EA42C02A1A6C385024B18D5A925E2D6633E6E0D7B889EAAE7549CE8DD3
```

Those fixtures explain the existing Level B route profile. They are not the
author paper-branch full-resolution `dragon.ply` / `happy_buddha.ply` inputs.

## Manifest Update

Updated:

```text
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

The manifest now includes the Goal5178 artifact under `evidence.result_artifacts`.

## Validation

Commands:

```text
py -m unittest tests.goal5178_xhd_priority_input_bridge_test tests.goal5177_xhd_paper_target_log_mapping_test
py -m json.tool Paper-reproduction-apps\x-hd-paper\results\xhd_priority_input_bridge_goal5178_graphics_dragon_happy_buddha_2026-07-08.json > $null
py -m json.tool Paper-reproduction-apps\x-hd-paper\data\manifest.json > $null
```

Result:

```text
Ran 2 tests in 0.112s
OK
```

Known local noise:

```text
Could not find platform independent libraries <prefix>
```

The command exits successfully despite this Windows Python noise.

## What This Proves

Goal5178 proves:

```text
the Dragon-HappyBuddha author paper-branch workload is now connected to local
public Stanford full-resolution candidate files;
the candidate files exist locally;
their vertex counts match the author logs exactly;
their SHA256 hashes and archive hashes are recorded;
the project has a concrete Level B large-input target.
```

## What This Does Not Prove

Goal5178 does not prove:

```text
the local public files are byte-identical to the author's /local/storage files;
full X-HD paper reproduction;
exact paper dataset reproduction;
Figure 5 graphics reproduction;
author-vs-RTDL performance ratio;
that the existing RTDL route can process 437645 x 543652 directly without a
scalable route plan.
```

## Next Recommended Goal

Do not run the old exact pairwise route at full `437645 x 543652` scale.

Next, choose one of:

1. Build a scalable Level B large-input feasibility plan for
   Dragon-HappyBuddha full public Stanford candidates using the current seeded
   route components, or
2. seek stronger author provenance for exact input identity before trying to
   promote this from Level B to Level C.

The first option is more actionable; the second is stronger but depends on
external data not currently present.
