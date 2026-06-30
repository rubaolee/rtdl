# Goal 1515: Embree Native Linux Validation

## Verdict

Native Embree is available on the local Linux validation host, and the focused
Embree app smoke/parity slice passed.

This is CPU-backend validation only. It does not add NVIDIA evidence, does not
authorize public speedup wording, does not authorize broad RTX wording, does not
authorize whole-app claims, does not authorize true zero-copy wording, and does not promote `COLLECT_K_BOUNDED`.

## Environment

- Host: `192.168.1.20`
- Checkout: `/home/lestat/work/rtdl_codex_local_check`
- Branch: `main`
- Validated pushed commit: `6a3739b1`
- Native Embree library: `/home/lestat/work/rtdl_codex_local_check/build/librtdl_embree.so`
- Library load result: `embree_library_loaded=yes`

## Command

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal715_embree_fixed_radius_summary_test \
  tests.goal717_embree_prepared_fixed_radius_summary_test \
  tests.goal720_embree_prepared_knn_rows_test \
  tests.goal723_event_hotspot_embree_summary_test \
  tests.goal724_service_coverage_embree_summary_test \
  tests.goal736_robot_collision_embree_scaled_test
```

## Result

```text
Ran 17 tests in 0.175s
OK
```

## Scope

The slice validates native Embree coverage for fixed-radius summary behavior,
prepared fixed-radius summary behavior, prepared KNN rows, event hotspot Embree
summary behavior, service coverage Embree summary behavior, and robot collision
Embree scaled behavior.

It complements the Goal1514 CPU promotion lane. It does not replace OptiX pod
validation for GPU performance, native path/topology evidence, or stage
profiling.

## Claim Boundary

Goal1515 is native Embree correctness/smoke validation. It does not authorize
public speedup wording, broad RTX wording, whole-app claims, true zero-copy
wording, stable primitive promotion, experimental public promotion, partner
tensor handoff, release action, or NVIDIA performance claims.
