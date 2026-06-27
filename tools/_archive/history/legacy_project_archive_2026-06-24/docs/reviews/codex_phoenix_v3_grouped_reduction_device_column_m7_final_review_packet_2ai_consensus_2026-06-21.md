# Codex 2-AI Consensus: Phoenix V3 Grouped-Reduction Device-Column M7 Final Review Packet

Date: 2026-06-21

Status: both exact device-column grouped_sum rows are approved as supplemental
row-scoped M7 evidence after subagent review and P1 wording fixes. This is not
V3 release authorization.

## Scope

Bounded goal:

```text
Decide whether the final grouped-reduction cupy_device_columns packet can
promote the two exact serious-size rows to supplemental Phoenix V3 M7.
```

Primary packet:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.md
docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.json
```

Review request:

```text
docs/reviews/call_for_review_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.md
```

External CLI note:

```text
docs/reviews/external_ai_blocked_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.md
```

Claude and Gemini CLI review did not complete in this shell. The recorded
second-AI review is therefore the independent Codex subagent review, not Claude
or Gemini approval.

Second-AI review:

```text
docs/reviews/codex_subagent_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_review_2026-06-21.md
```

Verdict:

```text
approve-with-required-fixes
row decision: promote_both_rows
P0 issues: none
```

## P1 Fixes Applied

The approved public wording now says that Embree remains host-packed while the
OptiX candidate uses `cupy_device_columns`; therefore the Embree/device-column
ratios are same-contract context, not pure backend-only ratios.

The `218.248x` number is not used as headline or public row wording. It remains
only a labeled cold-prepare phase ratio next to the workload-build/input-path
collapse attribution.

## Promoted Exact Rows

```text
grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups
grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups
```

Both rows remain exact row-scoped claims only:

```text
generic_capability: grouped_reduction
operation: prepared_grouped_sum_i64
ray_batch_layout: cupy_device_columns
warmup: 3
repeat: actual repeat=100
hardware: NVIDIA RTX 4000 Ada Generation POD
CPU reference parity: true
device route host_packed_ray_count: 0
existing scalar-broadcast M7 row retained: true
```

Accepted row-scoped measurements:

```text
262,144 rows / 1,024 groups / 38,043,648 logical rays
host-packed OptiX/device-column OptiX cold+loop: 3.599x
Embree/device-column OptiX cold+loop same-contract context: 100.019x

524,288 rows / 2,048 groups / 76,087,296 logical rays
host-packed OptiX/device-column OptiX cold+loop: 73.586x
Embree/device-column OptiX cold+loop same-contract context: 174.645x
```

## Consensus Decision

Codex accepts the second-AI review after applying the P1 wording fixes.

The two exact rows are supplemental M7-qualified, row-scoped evidence. They do
not replace:

```text
grouped_reduction_sum_scalar_broadcast_repeat100_262144
```

That existing row remains part of the grouped-reduction public surface.

## Boundary

Current authorization remains:

```text
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_authorized: false
```

Allowed row-scoped reading:

```text
row_scoped_public_speedup_claim_authorized: true
m7_promotion_authorized: true
m7_qualified_release_rows_from_this_packet: 2
```

Do not claim:

- V3 release readiness;
- broad V3-over-V2 performance;
- whole-RayDB or whole-database acceleration;
- true zero-copy;
- all grouped_reduction rows are public claims;
- the old scalar-broadcast grouped_sum M7 row has been replaced;
- pure backend-only Embree/OptiX ratios;
- `218.248x` as a V3 headline or public end-to-end speedup.

## Goal-Level Decision Audit

Decision: promote both exact `cupy_device_columns` grouped_sum rows as
supplemental row-scoped M7 evidence after second-AI review and P1 wording
fixes.

1. Was I foolish?
   No. The decision uses serious POD evidence, records blocked Claude/Gemini
   CLI attempts, uses a separate second-AI review, applies required P1 fixes,
   and keeps all broad release claims false.
2. If yes, what actions made the decision foolish?
   Not applicable for this decision. The foolish actions would be claiming V3
   release readiness, treating the Embree/device-column ratio as pure
   backend-only, or using `218.248x` as public headline wording.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes: keep these rows pending until Claude or Gemini CLI works. That is safer
   procedurally, but it would block a reviewed generic-engine improvement after
   both named CLI paths failed in the current shell.
4. Can I now try a different path that actually solves the problem?
   Yes. Promote only these exact rows, update the global M7 classification and
   gates, then continue the Phoenix generic-engine queue rather than calling V3
   complete.
