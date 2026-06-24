# Phoenix V3 RayDB M28 Grouped-Reduction Pod Evidence

Status: internal grouped-reduction evidence, 2026-06-20.

This is not V3 release authorization and not public database acceleration
wording.

## Scope

This packet strengthens the RayDB-style `grouped_reduction` capability under
the Goal4392 M4/M7 rules. It uses the existing app-agnostic prepared grouped
i64 reduction primitive. It does not introduce a RayDB engine, SQL engine, query
planner, transaction system, or app-specific native code.

The `raydb_paper_triangle_scan_*` contract names are benchmark fixture-domain
labels; no RayDB engine, query planner, or transaction system is invoked.

## Artifacts

```text
docs/rebuild/v3/evidence/phoenix_v3_raydb_m28_grouped_reduction_20260620
```

Primary successful run:

```text
m28_raydb_grouped_reduction_524288.json
m28_raydb_grouped_reduction_524288.log
```

Preserved overlarge attempt:

```text
overlarge_1048576_attempt_status.txt
m28_raydb_grouped_reduction_1048576.log
```

The 1,048,576-row exploratory run was stopped after more than 20 minutes without
producing JSON. It is preserved as an overlarge attempt, not hidden.

## Result

Hardware:

```text
NVIDIA RTX 4000 Ada Generation, driver 550.127.05
```

Successful row:

```text
generated_rows: 524288
generated_groups: 2048
warmup: 2
repeat overrides:
  embree count: 100
  embree sum: 5
  optix count: 1000
  optix sum: 500
```

| Mode | Embree median | OptiX median | Embree / OptiX | CPU reference | Claim status |
| --- | ---: | ---: | ---: | --- | --- |
| count | 14.881 ms | 1.700 ms | 8.752x | pass | internal only |
| sum | 2104.065 ms | 13.316 ms | 158.010x | pass | internal only |

Repeat counts are asymmetric by design: count uses Embree 100 reps and OptiX
1,000 reps; sum uses Embree 5 reps and OptiX 500 reps.

All rows report:

- `matches_cpu_reference=true`;
- `prepared_steady_state=true`;
- `prepared_primitive_payload_reused=true`;
- `prepared_ray_batch_reused=true`;
- `partner_continuation_required=false`;
- `public_speedup_claim_authorized=false`.

## Timing Boundary

These are prepared hot-query ratios, not end-to-end application timings.

The large `sum` row has heavy setup costs:

- Embree `workload_build_sec`: 217.964 s
- Embree `cold_prepare_total_sec`: 218.028 s
- OptiX `workload_build_sec`: 213.265 s
- OptiX `cold_prepare_total_sec`: 215.843 s

The OptiX `sum` `cold_prepare_total_sec` includes both `workload_build_sec`
(213.265 s) and one-time ray-batch preparation (2.547 s). The hot-query
`elapsed_median_sec` (13.316 ms) excludes all of that setup.

Therefore the allowed reading is:

```text
Prepared grouped-reduction hot query is much faster on OptiX than Embree for
this generated row after the workload and prepared state exist.
```

The forbidden reading is:

```text
RayDB-style V3 is 158x faster end to end.
```

## Interpretation

This is the clean RayDB evidence lane:

- same generic grouped-reduction primitive;
- same generated data shape;
- same CPU reference parity;
- no partner continuation required;
- no app-specific native engine logic;
- prepared hot-query timing separated from cold build/prepare timing.

It complements, but does not replace, the all-app claim-grade candidate rows
that use partner-gated RayDB routes. Those rows have larger OptiX/Embree ratios
but more complicated metric-source and partner boundaries. This M28 row is
cleaner for a future M7 grouped-reduction packet.

## Boundary

No current public claim is authorized:

```text
release_authorized=false
public_speedup_claim_authorized=false
whole_app_speedup_claim_authorized=false
paper_reproduction_claim_authorized=false
true_zero_copy_authorized=false
Phoenix M7-qualified release rows=0
```

## Goal-Level Decision Audit

Decision: accept the 524,288-row RayDB M28 rerun as internal grouped-reduction
evidence and preserve the 1,048,576-row overlarge attempt.

1. Was I foolish?

   The corrected decision is not foolish. It keeps the serious successful row
   and preserves the overlarge attempt.

2. If yes, what actions made the decision foolish?

   The foolish action was starting the 1,048,576-row run with both scale and
   repeat counts increased, causing a single evidence point to exceed the
   bounded-goal time budget before producing JSON.

3. Was there another path?

   Yes. Start with 524,288 rows and a timeout, then decide whether a larger row
   is worth a separate overnight run.

4. Can I now try a different path that actually solves the problem?

   Yes. The 524,288-row run gives a non-toy same-contract grouped-reduction row,
   with timing boundaries explicit and all public/release flags false.
