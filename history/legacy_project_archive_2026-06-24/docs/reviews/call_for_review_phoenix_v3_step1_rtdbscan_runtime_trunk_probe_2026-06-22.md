# Call For Review: Phoenix V3 Step 1 RTDBSCAN Runtime-Trunk Probe

Date: 2026-06-22
Status: `request_external_review_not_release`

## Review Request

Please critically review the focused Step-1 RTDBSCAN runtime-trunk pod A/B:

- Report:
  `docs/reports/phoenix_v3_step1_rtdbscan_runtime_trunk_probe_pod_ab_2026-06-22.md`
- Evidence:
  `docs/rebuild/v3/evidence/phoenix_v3_step1_rtdbscan_trunk_probe_20260622_211934/summary.json`
- Controlling redesign:
  `docs/rebuild/v3/proposed_v3_redesign_build_the_runtime_trunk_first_2026-06-22.md`

## Facts To Check

```text
runner_vs_legacy_geomean: 0.9948584784435961
runner_vs_embree_geomean: 2.927728873898229
runtime_trunk_executes_all_runner_samples: true
internal_device_residency_all_runner_samples: true
hot_path_host_materialization_any_runner_sample: false
material_set_a_candidate: false
release_authorized: false
```

## Questions

1. Is the interpretation correct that this proves Step-1 execution/residency
   visibility, but not material performance?
2. Is `runner vs legacy OptiX grouped-stream` the correct incumbent comparison
   for material Set-A credit?
3. Should RTDBSCAN be stopped as the immediate material-probe candidate?
4. Which next Set-A family is the most honest Step-1/Step-2 target: RayJoin,
   Barnes-Hut, RTNN, Triangle, or Hausdorff?
5. Does this result trigger the redesign caveat that V3 may need capability /
   quality framing if another Set-A family also fails?

## Non-Authorization

This packet does not authorize release, public speedup wording, broad
V3-over-V2.x wording, true-zero-copy wording, external embedding wording, or
all-app pod spend.
