# Goal2806 v2.5 Internal Readiness Packet

Date: 2026-05-31

Status: implemented locally.

Verdict: accept-with-boundary.

## Purpose

Goal2806 turns the current v2.5 evidence state into a single machine-checked
internal readiness packet. This is a navigation and anti-overclaim gate: it
indexes the ten-app manifest, core v2.5 validators, Tier B clean artifacts,
external review files, and the broad clean pod regression gate.

This is not a v2.5 release authorization.

## Current Position

The packet validates the current v2.5 state as an internal evidence packet:

| Area | Result |
| --- | --- |
| Manifest coverage | 10 benchmark apps |
| Tier counts | A=3, B=4, C=3 |
| Core v2.5 validators | accept |
| Tier B clean artifacts | 4 pass artifacts with source metadata |
| External review paths indexed | present |
| Broad clean pod gate | Goal2805, 239 tests, OK |

The validated manifest remains:

| Tier | Apps |
| --- | --- |
| A | `raydb_style`, `triangle_counting`, `spatial_rayjoin` |
| B | `rt_dbscan`, `rtnn`, `barnes_hut`, `hausdorff_xhd` |
| C | `librts_spatial_index`, `contact_manifold`, `robot_collision` |

## Indexed Evidence

Goal2806 requires the key reports from Goal2773 through Goal2805, including:

- the Goal2773 v2.5 status and next-goals packet;
- grouped hit-stream support matrix, neutral seam, richer grouped reductions,
  partner-selection guidance, determinism policy, and tier-label reconciliation
  reports;
- canonical harness reports for triangle counting, LibRTS, Spatial RayJoin,
  RTNN, Hausdorff/X-HD, RT-DBSCAN, and Barnes-Hut;
- Goal2804 clean artifact metadata refresh;
- Goal2805 broad clean pod regression gate.

The Tier B clean artifacts indexed by the gate are:

| App | Clean artifact requirement |
| --- | --- |
| `rtnn` | `status: pass`, source commit, `source_dirty: []`, NVIDIA pod identity |
| `hausdorff_xhd` | `status: pass`, source commit, `source_dirty: []`, NVIDIA pod identity |
| `rt_dbscan` | `status: pass`, source commit, `source_dirty: []`, NVIDIA pod identity |
| `barnes_hut` | `status: pass`, source commit, `source_dirty: []`, NVIDIA pod identity |

## Machine Gate

New public internal helpers:

```python
rt.v2_5_internal_readiness_packet(repo_root=".")
rt.validate_v2_5_internal_readiness_packet(repo_root=".")
```

The validator composes:

- `validate_v2_5_tiered_benchmark_manifest`;
- `validate_v2_5_partner_continuation_contract`;
- `validate_v2_5_partner_preview_gate`;
- `validate_v2_5_partner_support_matrix`;
- `validate_v2_5_partner_selection_guidance`;
- `validate_v2_5_continuation_determinism_policies`;
- clean artifact metadata checks;
- required report and external-review path existence checks;
- false release and public-claim authorization flags.

## Boundary

Goal2806 is deliberately bounded. It is:

- not a v2.5 release authorization;
- not a public speedup claim;
- not a broad RT-core speedup claim;
- not a whole-app speedup claim;
- not a true-zero-copy claim;
- not package-install wording;
- not permission to auto-select Triton preview kernels;
- not permission to add app-specific logic to the native engine.

The accepted claim is narrower: the current v2.5 source-tree evidence packet is
internally coherent enough for external review and further engineering
hardening.

## Validation

Local focused validation:

```text
$env:PYTHONPATH='src;.'
py -3 -m unittest \
  tests.goal2806_v2_5_internal_readiness_packet_test \
  tests.goal2805_v2_5_broad_clean_pod_regression_gate_test \
  tests.goal2804_v2_5_clean_artifact_metadata_refresh_test
```

Result:

```text
Ran 11 tests in 0.046s
OK
```

The next useful step is external review of this packet, then a clean pod rerun
of the Goal2806/Goal2805/Goal2804 slice after the review/consensus files land.
