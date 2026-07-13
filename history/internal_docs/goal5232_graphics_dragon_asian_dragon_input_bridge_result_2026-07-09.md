# Goal5232 Graphics Dragon -> AsianDragon Input Bridge Result

Date: 2026-07-09

## Verdict

```text
completed_graphics_dragon_asian_dragon_public_stanford_candidate_bridge__level_b_only
```

Goal5232 extends the existing X-HD Stanford graphics provenance bridge from
Dragon -> HappyBuddha to the next paper-log graphics target:

```text
graphics_dragon_asian_dragon
```

This target appears in the author paper-branch run_all logs and is the Figure 6
pruning-effectiveness target identified in Goal5177. Goal5232 only establishes
input provenance and same-source candidate readiness. It does not run the
author binary or RTDL route for this pair.

## Source Acquisition

New public Stanford source archive:

```text
URL:    https://graphics.stanford.edu/data/3Dscanrep/xyzrgb/xyzrgb_dragon.ply.gz
Bytes:  70527166
SHA256: 8AA449F1966CBB50E5896ECC32CF57AB5F0CDFD3C3E37D3E6F60B948997DA5C1
```

Extracted candidate PLY:

```text
File:   Paper-reproduction-apps/x-hd-paper/data/external/stanford/asian_dragon.ply
Bytes:  137162963
SHA256: 4A31C6B8951B0F9F4B351D183CB5D5D27E2D1A5916B27E6516ACFB9A91AD7F85
Format: binary_big_endian 1.0
Verts:  3609600
Faces:  7219045
```

Existing Dragon candidate:

```text
File:   Paper-reproduction-apps/x-hd-paper/data/external/stanford/dragon_recon/dragon_vrip.ply
Bytes:  33831477
SHA256: FEA87FF48F2ABA22FB53E7B67C3FF3F7B8C2A3B3A0653AF62C48BBA67C6D5744
Format: ascii 1.0
Verts:  437645
Faces:  871414
```

## Author Log Bridge

Output artifact:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5232_priority_input_bridge_graphics_dragon_asian_dragon_2026-07-09.json
```

Key facts:

```text
target: graphics_dragon_asian_dragon
author run_all record_count: 5
sections: auto_tune, eb_gpu, hybrid_gpu, rt_gpu
author HDResult set: [0.06536811590194702]
Dragon author point count:      437645
AsianDragon author point count: 3609600
public candidate point counts match author logs: true
strong_same_source_candidate: true
exact_paper_dataset_identity_proved: false
```

The same-source bridge is therefore strong enough to authorize a future
explicit Level-B Dragon -> AsianDragon run plan. It is not Level-C exact paper
dataset evidence because author logs provide only paths/statistics/HDResult,
not input bytes, input hashes, or deterministic reconstruction provenance.

## Code Changes

The existing bridge script was generalized:

```text
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_priority_input_bridge.py
```

Changes:

1. Added `graphics_dragon_asian_dragon` as a supported target.
2. Added the Stanford XYZ RGB AsianDragon archive URL.
3. Made PLY header parsing binary-safe, so `binary_big_endian 1.0` PLY files
   can be audited without decoding the binary payload as text.

Focused test updated:

```text
tests/goal5178_xhd_priority_input_bridge_test.py
```

The new test builds a tiny binary-header PLY fixture and verifies the
Dragon->AsianDragon bridge behavior without claiming exact paper identity.

## Validation

```text
py -m unittest tests.goal5178_xhd_priority_input_bridge_test

Ran 2 tests in 0.177s
OK
```

Compile validation:

```text
py -m py_compile \
  Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_priority_input_bridge.py \
  tests/goal5178_xhd_priority_input_bridge_test.py
```

Bridge generation:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_priority_input_bridge.py \
  --app-root Paper-reproduction-apps/x-hd-paper \
  --mapping Paper-reproduction-apps/x-hd-paper/results/xhd_paper_target_log_mapping_goal5177_2026-07-08.json \
  --log-index Paper-reproduction-apps/x-hd-paper/results/xhd_paper_branch_log_index_goal5176_2026-07-08.json \
  --target graphics_dragon_asian_dragon \
  --output Paper-reproduction-apps/x-hd-paper/results/xhd_goal5232_priority_input_bridge_graphics_dragon_asian_dragon_2026-07-09.json
```

## Claim Boundary

Allowed:

```text
Dragon -> AsianDragon has a public Stanford same-source candidate whose point
counts match the author paper-branch logs for this target.
```

Forbidden:

```text
Dragon -> AsianDragon exact paper input identity is proved.
Dragon -> AsianDragon author/RTDL HDResult is reproduced.
Figure 6 is reproduced.
Author-vs-RTDL performance ratio or parity is established.
Full X-HD paper reproduction is complete.
```

## Next Step

The next concrete goal should run a bounded feasibility gate for
Dragon -> AsianDragon. Because the target is 437,645 x 3,609,600 points, the
next gate should avoid naive pairwise materialization and should reuse the
existing scalable cell-MBR / inline-nearest route. A prudent first execution is
a source-subset capacity/profiling gate before any all-source route.
