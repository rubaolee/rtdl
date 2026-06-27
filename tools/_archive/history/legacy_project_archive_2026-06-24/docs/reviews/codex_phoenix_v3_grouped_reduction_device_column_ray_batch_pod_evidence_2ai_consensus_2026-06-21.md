# Codex 2-AI Consensus: Phoenix V3 Grouped-Reduction Device-Column Ray-Batch POD Evidence

Date: 2026-06-21

Status: M7 review reopened for a new exact device-column grouped_sum candidate,
not M7 promotion and not V3 release authorization.

## Scope

Bounded goal:

```text
Decide whether the new POD evidence for cupy_device_columns prepared
grouped_sum is a real V3 generic-engine optimization and whether it can reopen
M7 review.
```

Primary packet:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_ray_batch_pod_evidence_2026-06-21.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_ray_batch_pod_evidence_2026-06-21.json
```

## Review Status

Claude review was requested but blocked by local tool access:

```text
docs/reviews/claude_blocked_phoenix_v3_grouped_reduction_device_column_ray_batch_pod_evidence_2026-06-21.md
```

This is not Claude approval.

Independent second review used for this provisional 2-AI consensus:

```text
docs/reviews/codex_subagent_phoenix_v3_grouped_reduction_device_column_ray_batch_pod_evidence_review_2026-06-21.md
```

Second-review verdict:

```text
approve-with-required-fixes
```

## P0 Fixes Applied

P0-1 source provenance:

- the packet now records that raw evidence JSONs have
  `git_head: fatal: not a git repository`;
- the packet binds the evidence to
  `docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_device_columns_20260621/source_manifest.sha256`;
- `source_manifest.sha256` is explicitly named as the source traceability
  record for this POD run.

P0-2 exact row identity:

- `grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups`
- `grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups`

Both candidate rows specify:

- `ray_batch_layout: cupy_device_columns`;
- `operation: prepared_grouped_sum_i64`;
- generated rows/groups;
- logical ray count;
- `warmup: 3`;
- `repeat: 100`;
- NVIDIA RTX 4000 Ada pod;
- existing M7 row retained, not replaced.

## P1 Fixes Applied

Phase attribution now states that the cold-prepare win includes
workload-build/input-path collapse, ray-batch preparation, native prepare, and
other measured cold setup. It must not be described as only ray-batch
preparation.

The packet now carries the pre-dedup hit-event explanation: Embree and OptiX
pre-dedup hit counts can differ, while all rows match the CPU reference after
grouped reduction.

Tests now assert source-manifest binding, missing git-head acknowledgement,
device-column row identities, phase attribution, and pre-dedup hit-event
interpretation.

## Accepted Facts

This evidence is accepted as a real V3 generic-engine optimization candidate.
RayDB is the benchmark harness; the reusable capability is the prepared
grouped_sum route using the generic prepared ray-batch device-column ABI.

Accepted measured facts:

- 262,144 rows / 1,024 groups / 38,043,648 logical rays:
  - OptiX host-packed over device-columns cold prepare: `6.022x`
  - OptiX host-packed over device-columns cold-plus-loop: `3.599x`
  - Embree over OptiX device-columns hot query: `203.492x`
  - Embree over OptiX device-columns cold-plus-loop: `100.019x`
  - OptiX device route `host_packed_ray_count: 0`
- 524,288 rows / 2,048 groups / 76,087,296 logical rays:
  - OptiX host-packed over device-columns cold prepare: `218.248x`
  - OptiX host-packed over device-columns cold-plus-loop: `73.586x`
  - Embree over OptiX device-columns hot query: `173.013x`
  - Embree over OptiX device-columns cold-plus-loop: `174.645x`
  - OptiX device route `host_packed_ray_count: 0`

## Consensus Decision

The M7 review may be reopened for the two exact device-column candidate rows.

This does not authorize immediate promotion. A final M7 packet must still
decide whether to promote one row, promote both rows, keep them internal, or
revise wording after another external review.

This does not supersede:

```text
grouped_reduction_sum_scalar_broadcast_repeat100_262144
```

That existing row remains the current grouped_reduction M7 row until an
explicit final review changes the public surface.

## Boundary

Current authorization remains:

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_authorized: false
m7_promoted: false
```

Do not claim:

- V3 release readiness;
- broad V3-over-V2 performance;
- whole-RayDB or whole-database acceleration;
- true zero-copy;
- all grouped_reduction rows are public claims;
- pure backend-only Embree/OptiX ratios without saying the OptiX route uses
  `cupy_device_columns` while Embree remains host-packed.

## Verification

Focused packet test:

```text
py -3 -m unittest tests.v3_phoenix_grouped_reduction_device_column_pod_evidence_test
8 tests OK
```

Focused gate/test set:

```text
py -3 -m unittest tests.v3_phoenix_next_engine_work_queue_test tests.v3_release_wording_gate_test tests.v3_phoenix_release_readiness_gate_test tests.v3_phoenix_grouped_reduction_device_column_pod_evidence_test
17 tests OK
```

Release wording gate:

```text
py -3 scripts/v3_release_wording_gate.py --pretty
status: pass
violations: []
```

Release readiness gate:

```text
py -3 scripts/v3_phoenix_release_readiness_gate.py --pretty
status: blocked_not_release
failed_checks: []
```

Full V3 rebuild matrix:

```text
py -3 scripts/run_test_matrix.py --group v3_rebuild
53 modules / 245 tests OK
```

## Goal-Level Decision Audit

Decision: authorize reopening M7 review for exact device-column grouped_sum
candidate rows after P0/P1 fixes, without promotion.

1. Was I foolish?
   No. The second review found material evidence and real gaps; fixing the gaps
   before consensus is the responsible path.
2. If yes, what actions made the decision foolish?
   It would have been foolish to call the rows M7 before binding source
   provenance, defining exact row identities, and preserving release boundaries.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: leave the current grouped_reduction row alone and move to another app.
   That would avoid risk but would fail to answer whether Phoenix V3 can deliver
   a stronger generic prepared-input-path optimization.
4. Can I now try a different path that actually solves the problem?
   Yes. The next path is a final M7 review packet for these exact
   `cupy_device_columns` rows, with Claude/Gemini review when available.
