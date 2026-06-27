# Goal2515 Partner-Resident Grouped Min/Max I64

Date: 2026-05-22

## Summary

Goal2515 extends the experimental OptiX partner-resident grouped-i64 path from
`count/sum` to `count/sum/min/max`. The change is generic to the columnar
grouped-reduction runtime surface. It does not add RayDB-specific native ABI,
SQL semantics, or app/domain vocabulary to the engine.

## Native Change

The OptiX device-column grouped-i64 module now supports:

- `RTDL_GROUPED_OP_COUNT`
- `RTDL_GROUPED_OP_SUM`
- `RTDL_GROUPED_OP_MIN`
- `RTDL_GROUPED_OP_MAX`

The min/max path uses signed int64 compare-and-swap helpers:

- `device_atomic_min_i64`
- `device_atomic_max_i64`

The reduction workspace is initialized on device by
`device_column_grouped_i64_init_values_kernel`, then the existing compact-output
kernel materializes only non-empty grouped rows at the Python boundary.

New experimental native symbols:

- `rtdl_optix_columnar_device_payload_grouped_min_i64_with_capacity`
- `rtdl_optix_columnar_device_payload_grouped_max_i64_with_capacity`

Both require explicit `group_capacity`. There is no legacy implicit-capacity
min/max wrapper.

## Python Surface

New experimental entrypoints:

- `run_optix_partner_resident_columnar_grouped_min_i64(...)`
- `run_optix_partner_resident_columnar_grouped_max_i64(...)`

Both require:

- `allow_experimental_native=True`
- exactly one group key
- an int64-compatible value field
- explicit dense non-negative `group_capacity`

The RayDB-style benchmark harness now uses the experimental partner-resident
backend for `count`, `sum`, `min`, and `max`. CPU reference remains the broader
oracle and still includes `avg_as_sum_count`; native Embree and stable OptiX
columnar payload paths remain count/sum-only.

## Claim Boundary

Allowed internal wording:

- experimental partner-resident grouped int64 `count/sum/min/max` parity over
  CUDA column descriptors;
- compact grouped rows are downloaded, not capacity-sized reduction workspaces;
- signed int64 min/max is handled by generic device-side atomic CAS helpers.

Blocked wording:

- true zero-copy claim;
- SQL or DBMS support;
- full RayDB reproduction;
- arbitrary sparse/hash group-key support;
- public speedup claim;
- whole-app acceleration claim.

## Tests

Focused local validation:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal2515_partner_resident_grouped_min_max_i64_test
```

Expected result:

```text
6 tests OK
```

RayDB-style local sequence through Goal2515:

```text
115 tests OK, 4 skipped
```

Full historical discover was also attempted:

```text
5513 tests run; 255 failures, 173 errors, 304 skipped
```

Those failures are not Goal2515-specific. The run is dominated by pre-existing
missing historical documents, examples, native proof files, and archived release
artifacts in this checkout.

## Pod Evidence

Pod SSH used:

```text
ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new -i ~/.ssh/id_ed25519_rtdl_codex -p 22017 root@69.30.85.198
```

Build command:

```text
make -C /root/rtdl_python_only_goal2501 build-optix OPTIX_PREFIX=/root/vendor/optix-dev-9.0.0 CUDA_PREFIX=/usr/local/cuda
```

The pod runner is:

```text
scripts/goal2515_partner_resident_grouped_min_max_pod.py
```

Build evidence:

- remote checkout: `/root/rtdl_python_only_goal2501`
- OptiX headers: `/root/vendor/optix-dev-9.0.0`
- CUDA prefix: `/usr/local/cuda`
- build log: `docs/reports/goal2515_make_build_optix_2026-05-22.txt`
- result: `make build-optix` completed successfully with only the CUDA
  deprecated-target warning.

Artifact:

```text
docs/reports/goal2515_partner_resident_grouped_min_max_pod_2026-05-22.json
```

Observed artifact assertions:

- status: `ok`
- app_suite_modes: `["count", "sum", "min", "max"]`
- app_suite_all_match_cpu_reference: `true`
- min_matches_cpu: `true`
- max_matches_cpu: `true`
- signed_min_matches_expected: `true`
- signed_max_matches_expected: `true`

Signed min/max probe:

- signed_min_rows: `region_id=0 -> -5`, `region_id=1 -> -20`,
  `region_id=2 -> 3`
- signed_max_rows: `region_id=0 -> 10`, `region_id=1 -> 7`,
  `region_id=2 -> 3`

This evidence remains experimental and does not authorize public performance or
zero-copy wording.

Pod-focused unittest validation after syncing the final source/report/test
slice:

```text
28 tests OK
```
