# Goal2499: Columnar Aggregate Lowering Gap And Next Engine Target

Date: 2026-05-22

## Verdict

Goal2499 turns the RayDB-style benchmark slice into an explicit RTDL
language/runtime reconstruction decision:

```text
ColumnarRecordSet + ColumnarAggregatePlan
-> current compatibility wrapper
-> native count/sum parity
-> future direct columnar preparation target
```

The current Embree and OptiX paths are useful same-contract parity paths, but
they are not the final engine shape. They still pass through row-mapping
compatibility wrappers before reaching native columnar payload preparation.

## Added Runtime Surface

New generic runtime descriptor:

- `ColumnarAggregateLoweringPlan`
- `plan_columnar_aggregate_lowering(backend)`
- `NATIVE_COLUMNAR_COUNT_SUM_BACKENDS`

The descriptor records:

- supported aggregates;
- unsupported aggregates;
- transfer path;
- whether a compatibility wrapper is used;
- whether row mappings are materialized for that wrapper;
- whether a direct `ColumnarRecordSet` preparation API exists;
- whether true zero-copy wording is authorized;
- whether backend runtime validation is required;
- the next engine target.

## Current Matrix

| Backend | Supported modes | Current path | Direct columnar API | True zero-copy wording |
| --- | --- | --- | --- | --- |
| `cpu_python_reference` | `count`, `sum`, `min`, `max`, `avg_as_sum_count` | Python columnar oracle | Yes | No |
| `embree` | `count`, `sum` | Columnar payload through row-mapping compatibility wrapper | No | No |
| `optix` | `count`, `sum` | Columnar payload through row-mapping compatibility wrapper | No | No |

## Next Engine Target

The next engine target is:

```text
direct_columnar_record_set_preparation_without_row_mapping
```

This target should let Python pass a normalized columnar descriptor directly to
backend preparation, instead of first expanding the fixture into row mappings.
That is a language/runtime improvement independent of RayDB reproduction.

## Explicit Non-Claims

Goal2499 does not authorize:

- RayDB reproduction;
- authors-code comparison;
- SQL engine or DBMS behavior;
- min/max native support;
- true zero-copy wording;
- public speedup wording;
- whole-app wording;
- new app-specific native ABI.

## Why This Matters

The app forced a clearer boundary:

- app code owns schema/query meaning;
- RTDL owns a generic columnar aggregate contract;
- current native backends own count/sum parity through generic columnar payloads;
- the next improvement is direct columnar preparation, not app-specific native
  specialization.
