# Goal4886: RayJoin Numba Partner Acceleration Progress Report

Date: 2026-07-03

Status: `engineering_evidence_complete__bounded_numba_writer_skip_speedup__pending_claude_review_debt`

## Objective

Use Numba as the first serious RTDL partner for the RayJoin
paper-reproduction-engineering app.

The target app is the already-correct bounded RayJoin reproduction:

- Section 5.2 LSI;
- Section 5.3 PIP / point-location;
- Section 5.7 polygon overlay.

The goal is not to re-prove correctness from scratch and not to modify RTDL
core. The goal is to preserve correctness while accelerating the Python
application-layer continuation/assembly around public RTDL LSI/PIP primitives.

## Artifacts Added

```text
history/internal_docs/goal4886_rayjoin_numba_partner_acceleration_goal_2026-07-03.md
history/internal_docs/goal4886_rayjoin_numba_overlay_kernels.py
history/internal_docs/goal4886_section57_public_primitives_overlay_numba_harness.py
history/internal_docs/goal4886_numba_synthetic_parity_summary.json
history/internal_docs/goal4886_numba_synthetic_parity_linux_summary.json
history/internal_docs/goal4886_pod_numba_synthetic_parity.json
history/internal_docs/goal4886_pod_current_au_repeat_summary.json
history/internal_docs/goal4886_pod_numba_au_cold_summary.json
history/internal_docs/goal4886_pod_numba_au_warm_summary.json
history/internal_docs/goal4886_pod_numba_synthetic_parity_skip.json
history/internal_docs/goal4886_pod_numba_au_skip_summary.json
history/internal_docs/goal4886_pod_numba_au_skip_repeat_summary.json
history/internal_docs/goal4886_pod_numba_synthetic_parity_skip_v2.json
history/internal_docs/goal4886_pod_numba_au_skip_v2_summary.json
history/internal_docs/goal4886_authorofficial_wall_attempt_invalid_summary.json
history/internal_docs/goal4886_authorofficial_wall_attempt_freshser_cwd_invalid_summary.json
```

## Current Route

Current correct Section 5.7 public route:

```text
public RTDL planar-map LSI
-> Python app-layer continuation / midpoint / chain assembly
-> public RTDL planar-map point-location / PIP
-> Python output-chain writer
```

Goal4886 keeps:

- public RTDL LSI/PIP primitives unchanged;
- `AuthorOfficial` comparator unchanged;
- no `rtdsl.rayjoin_overlay` dependency;
- no `src/rtdsl/**` or `src/native/**` edits.

## Why Numba Is The Right First Partner Here

The current app has a real Python continuation layer. Goal4880's Australia
representative timing showed:

| Phase | Seconds |
| --- | ---: |
| load/pack left | 71.937 |
| load/pack right | 5.727 |
| public LSI rows | 5.694 |
| vertex PIP map0 in map1 | 10.737 |
| vertex PIP map1 in map0 | 1.556 |
| output-chain write | 17.259 |
| total elapsed | 118.497 |

Numba is not expected to accelerate:

- native RTDL LSI/PIP traversal;
- text CDB parsing by itself;
- raw file writes or string formatting.

Numba is appropriate for:

- midpoint generation;
- grouped intersection continuation;
- consecutive point dedupe;
- chain keep decisions;
- array compaction and face-classification support.

## Implemented Numba Kernel Layer

File:

```text
history/internal_docs/goal4886_rayjoin_numba_overlay_kernels.py
```

Implemented kernels:

1. `midpoint_pairs_numba`
   - sorted edge-local intersections -> scaled midpoint query points;
   - preserves author-compatible truncating divide-by-two behavior.
2. `dedupe_consecutive_points_numba`
   - exact consecutive point dedupe mask.
3. `chain_keep_numba`
   - precomputes output-chain keep decisions from left/right/other face ids.
4. `chain_has_xsects_numba`
   - precomputes whether a chain owns any intersected edge;
   - used to skip no-intersection chains that the current writer would drop
     anyway.
5. `writer_skip_decision_numba`
   - makes the explicit per-chain skip decision from:
     `has_xsects` and `terminal_keep`;
   - skips only no-intersection chains whose terminal point does not produce
     an output chain;
   - never skips chains with intersections.

Each Numba path has a Python reference implementation and falls back cleanly
when Numba is unavailable.

## Implemented Numba-Enabled Harness

File:

```text
history/internal_docs/goal4886_section57_public_primitives_overlay_numba_harness.py
```

It wraps the proven Goal4880 harness and replaces only selected app-layer helper
functions:

- `midpoint_points`;
- `dedupe_point_pairs`;
- `write_output_chains_streaming`, with a Numba-generated skip plan for
  no-intersection chains that current writer semantics would drop.

It does not alter:

- RTDL primitive calls;
- comparator;
- output format;
- dataset labels;
- correctness gates.

The summary is relabeled as:

```text
rtdl.goal4886.section57_public_primitives_overlay_numba_harness.v1
```

and records:

```json
"numba_on_app_continuation_path": true/false,
"numba_on_rtdl_primitive_path": false
```

## Verification Completed

### Windows local check

Command:

```text
py history/internal_docs/goal4886_rayjoin_numba_overlay_kernels.py --summary history/internal_docs/goal4886_numba_synthetic_parity_summary.json
```

Result:

- Numba unavailable on this Windows Python;
- fallback reference path used;
- all synthetic parity checks passed.

### Linux local check

Host:

```text
192.168.1.20
```

Environment:

```text
Python 3.12.3
Numba 0.65.1
GPU: NVIDIA GeForce GTX 1070
```

Command:

```text
python3 goal4886_rayjoin_numba_overlay_kernels.py --summary goal4886_numba_synthetic_parity_linux_summary.json
```

Result:

```json
"numba_available": true,
"midpoint_pairs_match": true,
"dedupe_mask_match": true,
"chain_keep_match": true
```

This early local Linux artifact predates the explicit writer-skip decision
kernel. The later POD synthetic parity artifacts below cover
`chain_has_xsects_numba` and `writer_skip_decision_numba` with Numba available.
The first Numba timings include JIT compile time and are not performance
evidence.

## What Is Proven So Far

Proven:

- Numba is available on local Linux and on the POD.
- The five app-layer continuation/assembly kernels preserve Python-reference
  semantics on controlled synthetic cases.
- The Numba-enabled harness preserves the public RTDL route structure:
  public LSI, public PIP, no `rtdsl.rayjoin_overlay`, no core/native edits.
- On the Australia representative Section 5.7 route, RTDL+Numba produced
  byte-identical output to the established comparator.
- A bounded app-layer speedup exists when Numba is used for the real bottleneck:
  the writer skip decision.

Not proven:

- broad RayJoin speedup;
- full eight-pair paper speedup;
- AuthorOfficial wall-time speedup;
- RTDL LSI/PIP primitive speedup from Numba.

## POD Execution

POD:

```text
root@157.157.221.29 -p 23132
key: ~/.ssh/id_ed25519_rtdl_codex_current_pod
GPU: NVIDIA RTX 4000 Ada Generation
driver: 550.127.05
```

The POD default Python did not have `rtdsl` or Numba. The established RTDL
runtime path was:

```text
PYTHONPATH=/workspace/rtdl_goal4859_exec/src
LD_LIBRARY_PATH=/workspace/rtdl_goal4859_exec/build
```

Numba was installed into an isolated environment:

```text
/workspace/goal4886_numba_venv
Numba 0.66.0
NumPy 2.4.6
```

No RTDL source/native files were edited for this goal.

The POD work directory was:

```text
/workspace/goal4886_numba_au
```

### POD Synthetic Parity

Artifact:

```text
history/internal_docs/goal4886_pod_numba_synthetic_parity.json
history/internal_docs/goal4886_pod_numba_synthetic_parity_skip_v2.json
```

Result:

```json
"numba_available": true,
"midpoint_pairs_match": true,
"dedupe_mask_match": true,
"chain_keep_match": true,
"chain_has_xsects_match": true,
"writer_skip_decision_match": true
```

The explicit skip-decision cases include:

- chain has intersections -> do not skip;
- chain has no intersections and terminal keep is false -> skip;
- chain has no intersections but terminal keep is true -> do not skip.

### Australia Representative Full Harness

Inputs:

```text
/workspace/goal4848_rep/current_osm_au/lakes_Australia_current_osm_Point.cdb
/workspace/goal4848_rep/current_osm_au/parks_Australia_current_osm_Point.cdb
```

Comparator output:

```text
/workspace/goal4875_section57_au_representative/author_contract_full/author_contract_au_overlay.txt
sha256: a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e
```

All current RTDL / Numba outputs below were byte-equal to that comparator.

| Route | Artifact | Byte-equal | Elapsed sec | Output-chain sec |
| --- | --- | ---: | ---: | ---: |
| Current RTDL repeat | `goal4886_pod_current_au_repeat_summary.json` | yes | 117.258 | 16.525 |
| RTDL+Numba cold | `goal4886_pod_numba_au_cold_summary.json` | yes | 119.773 | 16.919 |
| RTDL+Numba warm/cache | `goal4886_pod_numba_au_warm_summary.json` | yes | 121.647 | 17.256 |
| RTDL+Numba writer skip | `goal4886_pod_numba_au_skip_summary.json` | yes | 101.832 | 1.818 |
| RTDL+Numba writer skip repeat | `goal4886_pod_numba_au_skip_repeat_summary.json` | yes | 100.531 | 1.811 |
| RTDL+Numba explicit skip decision | `goal4886_pod_numba_au_skip_v2_summary.json` | yes | 103.786 | 2.040 |

AuthorOfficial comparator timing from the final comparator log:

| AuthorOfficial logged phase | Time |
| --- | ---: |
| Read map 0 | 134.688 s |
| Read map 1 | 9.574 s |
| Load Data | 3.801 s |
| Build Index | 0.032 s |
| Intersection edges | 0.00495 s |
| Map 0 locate vertices | 0.0211 s |
| Map 1 locate vertices | 0.00739 s |
| Compute output polygons | 0.00866 s |
| Write to file | 0.802 s |

The final `author_contract_full` log did not record `/usr/bin/time` wall time.
The older `author_patch_au_overlay.log` recorded `AUTHOR_WALL_SEC=146`, but
that older output was not the final comparator output and is not promoted as
the AuthorOfficial wall baseline.

Two Goal4886 attempts were made to recover AuthorOfficial wall time:

| Attempt | Artifact | Wall sec | Byte-equal to final comparator | Result |
| --- | --- | ---: | ---: | --- |
| Reuse final serialized maps | `goal4886_authorofficial_wall_attempt_invalid_summary.json` | 3.453 | no | invalid baseline |
| Fresh serialize from text CDB, correct `release/bin` cwd | `goal4886_authorofficial_wall_attempt_freshser_cwd_invalid_summary.json` | 148.363 | no | invalid baseline |

The fresh-serialize attempt is the closest operational run, but its output was:

```text
sha256: 9d82b38aac634c76738e6c2552cbac6255a30460377ceb66e66b13450d223639
lines: 276407
```

The final comparator is:

```text
sha256: a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e
lines: 276320
```

Therefore neither AuthorOfficial wall attempt is used as a denominator for a
performance claim. Goal4886's valid wall comparison is current RTDL vs
RTDL+Numba on the same final comparator output.

## Performance Interpretation

Goal4886 proves two things:

1. Numba can be attached as a partner on the RayJoin app-layer continuation
   path without breaking correctness.
2. Numba is useful only when it is aimed at the real Python bottleneck.

The first midpoint/dedupe-only wrapper was a negative result:

```text
Current RTDL: 117.258 s
RTDL+Numba warm: 121.647 s
speed ratio: 0.964x (Numba route slower)
```

The corrected writer-skip pass is a real bounded win. The best measured
writer-skip run was the first repeat:

```text
Current RTDL: 117.258 s
RTDL+Numba writer skip repeat: 100.531 s
overall speedup: 1.166x

Current output-chain write: 16.525 s
Numba writer skip repeat output-chain write: 1.811 s
writer-phase speedup: 9.12x
```

The later explicit-skip-decision run is slightly slower but clearer and better
specified:

```text
Current RTDL: 117.258 s
RTDL+Numba explicit skip decision: 103.786 s
overall speedup: 1.130x

Current output-chain write: 16.525 s
Numba explicit skip-decision write: 2.040 s
writer-phase speedup: 8.10x
```

The skip plan did not change output:

```text
byte_equal_to_author: true
sha256: a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e
```

The skip plan moved real work:

```text
skipped_no_xsect_chains: 399419
skipped_no_xsect_points: 14996199
processed_chains: 9621
```

Interpretation:

- Numba did not accelerate RTDL LSI/PIP primitives.
- Numba did accelerate an application-layer continuation/assembly decision:
  deciding which no-intersection chains can be skipped before entering the
  Python per-point writer loop.
- The remaining dominant RTDL route cost is now load/pack (~75 s) plus vertex
  PIP (~12 s). The writer bottleneck was reduced from ~16.5 s to ~1.8 s.
- AuthorOfficial phase timings remain useful for understanding algorithmic
  structure, but AuthorOfficial wall time remains unavailable for the final
  comparator output.

## Decision Audit

1. **Was there a stupid failure mode here?**
   Yes: claiming Numba acceleration from synthetic parity, from first-call JIT
   timings, or from the midpoint/dedupe-only run would be stupid.

2. **What action would make the decision stupid?**
   Hiding the negative `0.964x` midpoint/dedupe result, or pretending the
   writer-skip win accelerates RTDL core LSI/PIP. It does not. It accelerates
   app-layer continuation/assembly.

3. **Is there another path that avoids being stuck?**
   Yes: keep moving Numba down the app-layer assembly path, but keep each step
   byte-equality-gated. The next likely targets are binary CDB cache/packing and
   further writer vectorization, not LSI/PIP.

4. **Can we start a better path now?**
   Yes. Goal4886 now has a correctness-preserving Numba partner win and a clear
   next bottleneck map.

## Next Step

Recommended next goal:

1. make the writer-skip plan clearer and smaller if it is promoted beyond
   internal evidence;
2. add focused regression tests for:
   - skipped no-intersection exterior chains;
   - kept no-intersection interior chains;
   - chains with intersections never skipped;
3. investigate binary CDB load/pack caching as a separate data-ingestion
   optimization, because load/pack now dominates the RTDL route.

## External Review Status

Antigravity review:

```text
history/internal_docs/antigravity_goal4886_rayjoin_numba_partner_acceleration_review_2026-07-03.md
verdict: approve_goal4886_numba_writer_skip_speedup_bounded_australia
```

Antigravity re-review after AuthorOfficial wall-boundary amendment:

```text
history/internal_docs/antigravity_goal4886_authorofficial_wall_boundary_rereview_2026-07-03.md
verdict: approve_goal4886_authorofficial_wall_boundary_honest
```

This is not a full 3-AI goal-completion consensus. Claude / additional review
debt remains open under the project's goal-level review rule.

## Exit Label For This Phase

```text
completed_numba_partner_writer_skip_speedup__byte_equal__bounded_australia_representative
```
