# V4 Goal4635 Component-Union Promotion Decision

Status: `goal4635_component_union_measured_pod_gate_pass_not_release`

Decision: `promote_component_union_to_measured_tier2_operator_coverage_not_release`

## Result

Goal4635 promotes `fixed_radius_graph_component_union_3d` from a predeclared
target to measured V4 Tier-2 operator coverage.

This is a generic component-union continuation, not a DBSCAN-native kernel.
The measured scope is Numba on OptiX 8.0 / RTX A5000. Torch and CuPy
component-union performance remain unmeasured.

## Evidence

Raw POD evidence:

- `future/v4/evidence/v4_goal4635_component_union_pod_gate_embree_2026-06-25/summary.json`
- `future/v4/evidence/v4_goal4635_component_union_pod_gate_embree_2026-06-25/README.md`

Target protocol review:

- `future/v4/reviews/claude_v4_goal4635_component_union_target_protocol_review_2026-06-25.md`

## Gate

Dataset and run:

- dataset: `clustered3d`
- point count: `262144`
- radius: `3.0`
- min neighbors: `4`
- repeat: `5`
- warmup: `1`
- GPU: NVIDIA RTX A5000
- driver: `570.195.03`
- Python: `3.12.3`
- Numba: `0.65.1`

Measured comparisons:

- runner vs Embree hot speedup: `1.3930791165731065x`
- runner vs Embree wall speedup: `1.6001250028719352x`
- runner vs legacy OptiX hot speedup: `1.0009063305938157x`
- runner vs legacy OptiX wall speedup: `1.2080037787208602x`
- failed checks: `0`
- all variant canonical component signatures match: `true`

The gate floors were:

- runner vs Embree hot: `>=1.20x`
- runner vs Embree wall: `>=1.20x`
- runner vs legacy wall: `>=0.98x`

## Coverage Effect

`rt_dbscan` moves from `partial_measured_operator_coverage` to
`strong_measured_operator_coverage` because it now maps to both:

- `v4_fixed_radius_count_threshold_2d_device_arrays`
- `v4_fixed_radius_graph_component_union_3d_device_arrays`

This remains operator coverage only. It does not authorize whole-app RTDBSCAN
speedup wording.

## Goal-Level Decision Audit

1. Was this decision stupid?
   No. The prior target was explicitly predeclared and reviewed; the POD gate
   passed all checks after the missing Embree control dependency was fixed.

2. If yes, what actions made it stupid?
   Not applicable. The one risky action would have been promoting from the
   earlier failed run where Embree was missing. That was not done.

3. Was there another path that avoided fixation?
   Yes: stop at the failed environment run and choose a different target. That
   would have avoided installation work but would have thrown away an otherwise
   valid, reviewed same-contract gate.

4. Can we now try a different path that truly solves the problem?
   Yes. Keep this as one measured coverage gain, then continue release
   hardening by expanding measured operator coverage and running the eventual
   all-app release scorecard. Do not claim release from this single gate.

## Non-Authorization

This decision does not authorize:

- V4 release
- V4 release candidate
- broad V4 speedup wording
- whole-application speedup wording
- all-benchmark speedup wording
- public true-zero-copy wording
- Tier-3 callback support
- raw OptiX callback support
- CuPy component-union performance
- Torch component-union performance
- C ABI / embedding / non-Python host claims
- application-specific native kernels
