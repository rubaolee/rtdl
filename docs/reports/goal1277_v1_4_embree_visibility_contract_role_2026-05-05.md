# Goal1277 v1.4 Embree Visibility Contract Role

Date: 2026-05-05

Status: local v1.4 implementation checkpoint. This does not require a pod and
does not change public RTX wording.

## Change

The graph `visibility_edges` primitive contract now records explicit backend
roles:

- Embree: `cpu_rt_baseline_and_fallback`;
- OptiX: `nvidia_rt_target`;
- all other backends: `compatibility_or_inactive`.

The contract also records `same_contract_baseline_required=true` for Embree and
OptiX. This makes the v1.4 migration rule explicit: OptiX performance work must
continue to compare against the same logical `ANY_HIT` plus count contract that
Embree executes, rather than against a different app path.

## Boundary

This is metadata and test coverage only. It does not add a prepared Embree
visibility-count implementation, does not touch Vulkan/HIPRT/Apple RT, and does
not claim a new speedup.

The existing Embree visibility row path remains the compatibility baseline for
now. A prepared Embree count wrapper should be considered only if v1.5 parity
review needs a prepared-vs-prepared CPU RT comparison.

## Verification

Focused local verification should include:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1276_v1_4_graph_visibility_wrapper_metadata_test \
  tests.goal1275_v1_4_first_wrapper_slice_plan_test \
  tests.goal1274_v1_3_primitive_contract_test \
  tests.goal889_graph_visibility_optix_gate_test \
  tests.goal957_graph_hausdorff_native_continuation_metadata_test \
  tests.goal814_graph_optix_rt_core_honesty_gate_test \
  tests.goal1129_graph_phase_split_contract_test
```

Result: 45 tests passed.
