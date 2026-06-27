# Goal2513 Partner-Resident Group Capacity Contract

Date: 2026-05-22

## Summary

Goal2513 removes the fixed `65536` grouped workspace assumption from the
experimental OptiX partner-resident grouped-i64 path. The native kernel now
checks group keys against an explicit `group_capacity` runtime parameter, and
Python can pass that capacity through `group_capacity=...`.

Compatibility is preserved: the original experimental symbols still call the
legacy default capacity. New `_with_capacity` symbols provide the compact
workspace path.

## New Native Symbols

- `rtdl_optix_columnar_device_payload_grouped_count_i64_with_capacity`
- `rtdl_optix_columnar_device_payload_grouped_sum_i64_with_capacity`

## Contract

The explicit-capacity path supports the same narrow scope as Goal2511:

- partner-resident CUDA numeric columns;
- numeric predicates;
- one int64-compatible group key;
- grouped count or int64-compatible grouped sum;
- dense non-negative group keys;
- group keys must be `< group_capacity`;
- compact grouped rows are materialized back to Python.

The capacity must be in `1..1000000`, matching the current row-count guard for
this experimental device-column path.

## RayDB-Style App Integration

The experimental RayDB-style backend now infers the fixture's dense group
capacity and passes it explicitly. For the current synthetic fixture,
`region_id` values are `0, 1, 2`, so the app passes `group_capacity=3` instead
of relying on the legacy `65536` default.

## Claim Boundary

Allowed internal wording:

- The experimental partner-resident OptiX grouped-i64 path supports explicit
  dense group capacity.
- The RayDB-style reconstruction harness uses compact capacity for its
  synthetic dense-group fixture.

Blocked wording:

- arbitrary sparse/hash group keys;
- SQL or DBMS support;
- true zero-copy claim;
- public speedup claim;
- whole-app acceleration claim.

## Tests

Focused local validation:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest tests.goal2513_partner_resident_group_capacity_contract_test
```

Expected result:

```text
5 tests OK
```

RayDB-style local sequence through Goal2513:

```text
112 tests OK, 4 skipped
```

## Pod Evidence

Pod SSH used:

```text
ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new -i ~/.ssh/id_ed25519_rtdl_codex -p 22017 root@69.30.85.198
```

Build evidence:

- remote checkout: `/root/rtdl_python_only_goal2501`
- OptiX headers: `/root/vendor/optix-dev-9.0.0`
- CUDA prefix: `/usr/local/cuda`
- build log: `docs/reports/goal2513_make_build_optix_2026-05-22.txt`
- result: `make build-optix` completed successfully with only the CUDA
  deprecated-target warning.

The pod runner is:

```text
scripts/goal2513_partner_resident_group_capacity_pod.py
```

Expected artifact:

```text
docs/reports/goal2513_partner_resident_group_capacity_pod_2026-05-22.json
```

Observed artifact summary:

- status: `ok`
- group_capacity: `3`
- legacy_default_capacity: `65536`
- capacity_is_explicit: `true`
- count_matches_cpu: `true`
- sum_matches_cpu: `true`
- app_suite_group_capacity: `3`
- app_suite_all_match_cpu_reference: `true`
- capacity_error_matched: `true`
- expected `group_capacity=2` error:
  `device-column grouped execution requires dense non-negative group keys below group_capacity`

This proves the experimental app path is no longer relying on a fixed 65536
workspace for the synthetic dense-group fixture.

Pod-focused unittest validation after syncing the final source/report/test
slice:

```text
17 tests OK
```
