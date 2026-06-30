# Goal2865: Current-Head Packet After Generic Front Doors

Status: current-head pod packet passed after Goal2861/Goal2863.

Date: 2026-05-31

## Purpose

Goal2861 changed the user-facing v2.5 generic partner front-door APIs, and
Goal2863 indexed that coverage in the internal readiness packet. This goal
reruns the canonical seven-harness packet at the new current head to ensure the
front-door and readiness changes did not regress the promoted benchmark
harnesses.

## Pod Run

Pod:

- host: `69.30.85.171`
- GPU: NVIDIA RTX A5000, driver 570.211.01
- source commit: `3c5efc3130829aced34abb34f5863d3f3b652ad5`
- compact child output: enabled
- output directory on pod: `/tmp/goal2865_packet_3c5efc31`

Command shape:

```text
python3 -u scripts/goal2855_v2_5_current_canonical_harness_packet_runner.py \
  --compact-child-output \
  --output-dir /tmp/goal2865_packet_3c5efc31 \
  --raw-output-dir /tmp/goal2865_packet_3c5efc31/raw \
  --stdout-dir /tmp/goal2865_packet_3c5efc31/stdout \
  --timeout-seconds 2700
```

## Result

Summary artifact:

- `docs/reports/goal2865_current_packet_after_front_doors_pod/goal2855_summary.json`

Preserved child artifacts:

- `docs/reports/goal2865_current_packet_after_front_doors_pod/goal2797_triangle_counting.json`
- `docs/reports/goal2865_current_packet_after_front_doors_pod/goal2798_librts.json`
- `docs/reports/goal2865_current_packet_after_front_doors_pod/goal2799_spatial_rayjoin.json`
- `docs/reports/goal2865_current_packet_after_front_doors_pod/goal2800_rtnn.json`
- `docs/reports/goal2865_current_packet_after_front_doors_pod/goal2801_hausdorff_xhd.json`
- `docs/reports/goal2865_current_packet_after_front_doors_pod/goal2802_rt_dbscan.json`
- `docs/reports/goal2865_current_packet_after_front_doors_pod/goal2803_barnes_hut.json`

Packet summary:

```text
status: pass
all_pass: true
artifact_count: 7
expected_artifact_count: 7
source_commit_consistent: true
source_dirty: []
dirty_artifacts: {}
claim_boundary_violations: {}
elapsed_sec: 429.05055393185467
```

Largest Barnes-Hut case:

```text
8192 bodies:
  Embree repeats: 101.165s, 96.295s, 96.572s
  OptiX repeats: 20.483s, 19.415s, 19.354s
  rows_match: true
  rt_core: true
  membership_speedup: 141.999x
```

The readiness packet now points `current_canonical_runner` at this Goal2865
summary.

## Boundary

This is current-head internal packet evidence. It is not a v2.5 release
authorization, not a public speedup claim, not a paper reproduction claim, not
package-install evidence, and not a true zero-copy claim. It confirms that the
canonical internal harness packet remains green after the generic front-door
API completion.

Short form: not a v2.5 release authorization.
