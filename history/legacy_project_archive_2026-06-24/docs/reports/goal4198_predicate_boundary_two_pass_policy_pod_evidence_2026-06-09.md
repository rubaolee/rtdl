# Goal4198: Predicate Boundary Two-Pass Policy Pod Evidence

Date: 2026-06-09

## Purpose

Goal4197 added an explicit `boundary_assignment_policy` knob for the generic
OptiX+Numba fixed-radius grouped-stream continuation. Goal4198 records the first
RTX pod evidence that the new `lowest_component_root_two_pass` policy executes
against the rebuilt OptiX library and reports the intended native policy
metadata.

## Pod Environment

- Host: `157.157.221.29:24101`
- GPU: NVIDIA RTX 4000 Ada Generation, driver 550.127.08
- Commit under test: `96e63e37`
- OptiX SDK root: `/root/vendor/optix-sdk`
- CUDA runtime prefix: `/usr/local/cuda-12.8`
- Numba CUDA NVCC package prefix:
  `/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc`
- Native library: `build/librtdl_optix.so`

The first build attempt used the Makefile default `/opt/optix` path and failed
because this pod stores the SDK under `/root/vendor/optix-sdk`. The evidence run
rebuilt with:

```bash
make build-optix OPTIX_PREFIX=/root/vendor/optix-sdk
```

The focused pod test passed:

```text
python3 -m unittest \
  tests.goal4197_predicate_boundary_lowest_root_two_pass_policy_test \
  tests.goal4194_predicate_aware_boundary_union_reference_test

Ran 10 tests in 0.002s
OK
```

## Hardware Smoke

Two artifacts were copied back from the pod:

- `docs/reports/goal4198_predicate_boundary_two_pass_policy_pod_rtx4000ada/two_pass_smoke.stdout.json`
- `docs/reports/goal4198_predicate_boundary_two_pass_policy_pod_rtx4000ada/two_pass_clustered_smoke.stdout.json`

The first road-shaped fixture was too sparse at `8192` points and produced all
noise, so it is execution smoke only. The clustered fixture is the meaningful
policy evidence:

| Field | Default policy | Two-pass policy |
| --- | ---: | ---: |
| Dataset | `clustered3d` | `clustered3d` |
| Points | 16,384 | 16,384 |
| Radius | 0.035 | 0.035 |
| Component threshold | 16 | 16 |
| Native policy | `lowest_candidate_then_root` | `lowest_component_root_two_pass` |
| Native pass count | 1 | 2 |
| Native symbol | `rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs` | same |
| Flag-true count | 16,314 | 16,314 |
| Negative-label count | 2 | 2 |
| Component count | 4 | 4 |
| Largest component size | 4,096 | 4,096 |
| Counts-only signature match | yes | yes |

The two-pass metadata confirms that the preview policy selected a second native
prepared RT pass. Both routes keep `public_speedup_claim_authorized=false` and
`true_zero_copy_claim_authorized=false`.

## Timing Boundary

The artifact includes elapsed times, but Goal4198 does not use them as
performance evidence. The default policy ran first and paid setup/JIT costs,
while the two-pass policy ran after warmup. A fair timing comparison would need a
separate randomized-order, repeated, warmed benchmark.

## Release Boundary

Goal4198 does not authorize release, public speedup claims, broad RT-core speedup
claims, whole-app speedup claims, true-zero-copy claims, automatic partner
selection, or app-specific native engine logic. It only proves that the generic
two-pass boundary policy can execute on RTX hardware and records the expected
policy metadata.

## Next Work

The remaining RT-DBSCAN performance/design target is still the larger one:
promote a generic predicate-aware boundary-union continuation only after
same-contract parity on dense and sparse fixtures and fair repeated timing. The
counts-only shortcut from Goal4190 remains an explicit user option, not the
default policy-bound route.
