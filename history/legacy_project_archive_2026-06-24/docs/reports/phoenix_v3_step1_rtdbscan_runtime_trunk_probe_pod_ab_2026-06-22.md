# Phoenix V3 Step 1 RTDBSCAN Runtime-Trunk Probe Pod A/B

Status: `step1_trunk_executes_but_not_material_not_release`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
full_all_app_rerun_authorized_by_this_packet: false
material_set_a_candidate: false
```

## What Was Tested

Focused same-RT-hardware pod A/B for the redesigned Step 1 trunk candidate:
fixed-radius self-query to grouped-stream component-signature continuation.

- Pod: RTX 4000 Ada Generation, driver `550.127.05`
- Evidence directory:
  `docs/rebuild/v3/evidence/phoenix_v3_step1_rtdbscan_trunk_probe_20260622_211934/`
- Dataset: `clustered3d`
- Point counts: `65536`, `262144`
- Repeat/warmup: `7 / 2`
- Samples: `3` per variant per scale
- Variants:
  - legacy OptiX grouped-stream Numba column-signature branch
  - productized runner OptiX grouped-stream Numba column-signature branch
  - Embree prepared-grid column-signature control

## Result

| Metric | Result |
| --- | ---: |
| Runner vs legacy OptiX grouped-stream geomean | `0.994858x` |
| Legacy vs Embree control geomean | `2.942860x` |
| Runner vs Embree control geomean | `2.927729x` |
| Runtime trunk executes all runner samples | `true` |
| Internal device residency all runner samples | `true` |
| Hot-path host materialization in runner samples | `false` |
| Claim flags all false | `true` |
| Legacy parity recovered | `true` |
| Material Set-A candidate | `false` |

The important comparison is runner vs legacy OptiX grouped-stream, not runner
vs Embree. Embree is a useful control, but the current incumbent for this
RTDBSCAN route is already the legacy OptiX grouped-stream path. The legacy path
already reaches `2.942860x` vs the Embree control, while the runner reaches
`2.927729x`; therefore the runner preserves the old OptiX-over-Embree class
advantage but does not create it. Against the real incumbent, the productized
runner is parity/slightly slower, not a material speedup.

## Interpretation

This probe proves the Step-1 route can be made visible as a productized runtime
trunk candidate:

- `runtime_trunk_executes_all_runner_samples: true`
- `internal_device_residency_all_runner_samples: true`
- `hot_path_host_materialization_any_runner_sample: false`
- `prepared_execution_session_runner_used: true`
- `runtime_trunk_family: fixed_radius_self_query_to_grouped_stream_component_signature_3d`

It does **not** prove the Phoenix V3 performance premise. The runtime wrapper
currently mostly makes the existing route auditable and repeatable; it does not
create a faster physical path than the old grouped-stream route.

## Consequence

Do not count RTDBSCAN Step 1 as the missing second material Set-A probe. Do not
authorize an all-app paired run from this result. Do not continue this exact
route as a cache/runner-hygiene thread unless a specific design change creates
a new performance source.

The next decision should be explicit:

1. Try a second Step-1 family whose old route is not already equivalent to the
   productized trunk, likely RayJoin topology/overlay or Barnes-Hut frontier.
2. Or accept that Phoenix V3's runtime trunk may be a capability/quality line
   unless another Set-A family demonstrates material runtime-sourced gain.

## Goal-Level Decision Audit

1. Was I foolish?
   No for running this focused probe; yes would be claiming success from it.
2. If yes, what actions would make the decision foolish?
   Counting `2.93x vs Embree` as a material V3 win, ignoring `0.995x vs legacy`,
   or spending all-app pod time after this result.
3. Was there another path?
   Yes: keep doing cache/prepared-query hygiene. That path was already stopped
   because it reaches parity, not major-version performance.
4. Can I now try a different path that solves the problem?
   Yes, but only if the next path has a real new performance source. The next
   candidate should be a different Set-A family through the same runner, not
   another RTDBSCAN wrapper micro-tune.

## Non-Authorization

This report authorizes no release, no broad V3-over-V2.x wording, no true
zero-copy wording, no external device-buffer/embedding claim, and no full
all-app rerun. Release remains `redo_required`.
