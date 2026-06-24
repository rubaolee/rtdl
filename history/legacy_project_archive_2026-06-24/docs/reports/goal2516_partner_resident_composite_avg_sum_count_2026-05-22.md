# Goal2516 Partner-Resident Composite Avg-As-Sum-Count

Date: 2026-05-22

## Summary

Goal2516 adds an app-agnostic composite aggregate lowering for the experimental
partner-resident columnar grouped path:

```text
avg_as_sum_count = sum + count
```

This is deliberately a Python+RTDL lowering rule, not a native engine ABI. The
native OptiX engine still only sees generic grouped reductions over partner
resident CUDA column descriptors.

## Language/Runtime Change

The generic columnar aggregate module now exposes:

- `COMPOSITE_COLUMNAR_AGGREGATE_LOWERINGS`
- `decompose_columnar_aggregate_plan(...)`
- `merge_columnar_grouped_sum_count_rows(...)`

For `avg_as_sum_count`, the plan decomposes into:

- grouped `sum(value_field)`
- grouped `count(group_key)`

The compact grouped outputs are merged by group key in Python. This preserves
the CPU oracle output contract: each row contains the group key, `sum`, and
`count`.

## App Harness Change

The RayDB-style benchmark harness now enables the experimental
`optix_partner_resident_experimental` backend for:

- `count`
- `sum`
- `min`
- `max`
- `avg_as_sum_count`

For `avg_as_sum_count`, metadata records:

- `composite_lowering: ["sum", "count"]`
- `native_launch_count: 2`
- `native_avg_abi_added: false`

## Claim Boundary

Allowed internal wording:

- experimental partner-resident composite aggregate parity for
  `avg_as_sum_count`;
- `avg_as_sum_count = sum + count`;
- no native average ABI;
- compact grouped rows are merged in Python.

Blocked wording:

- true zero-copy claim;
- SQL or DBMS support;
- full RayDB reproduction;
- public speedup claim;
- whole-app acceleration claim.

## Tests

Focused local validation:

```text
PYTHONPATH=src:. .venv-rtdl-scipy/bin/python -m unittest tests.goal2516_partner_resident_composite_avg_sum_count_test
```

Expected result:

```text
6 tests OK
```

Observed focused result:

```text
6 tests OK
```

## Pod Evidence

Pod SSH used:

```text
ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new -i ~/.ssh/id_ed25519_rtdl_codex -p 22017 root@69.30.85.198
```

No native rebuild is required for this goal because Goal2516 changes only the
Python lowering layer and pod runner/report/tests. The pod evidence uses the
Goal2515-built OptiX backend:

```text
RTDL_OPTIX_LIB=build/librtdl_optix.so
```

The pod runner is:

```text
scripts/goal2516_partner_resident_composite_avg_sum_count_pod.py
```

Observed artifact:

```text
docs/reports/goal2516_partner_resident_composite_avg_sum_count_pod_2026-05-22.json
```

Observed artifact assertions:

- status: `ok`
- native_avg_symbol_absent: `true`
- avg_matches_cpu: `true`
- app_suite_modes: `["count", "sum", "min", "max", "avg_as_sum_count"]`
- app_suite_all_match_cpu_reference: `true`
- avg_metadata.composite_lowering: `["sum", "count"]`
- avg_metadata.native_launch_count: `2`
- avg_metadata.native_avg_abi_added: `false`

Observed `avg_as_sum_count` rows:

- `region_id=0`, `sum=190`, `count=2`
- `region_id=1`, `sum=200`, `count=1`
- `region_id=2`, `sum=80`, `count=1`

This evidence remains experimental and does not authorize public performance or
zero-copy wording.
