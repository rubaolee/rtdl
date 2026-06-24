# Phoenix V3 RayDB Grouped-Reduction Redo Alignment

Date: 2026-06-22
Status: `raydb_grouped_reduction_redo_aligned_reusable_capability_not_release`

This closes the Phoenix redo interpretation for the RayDB grouped-reduction
work. The conclusion is deliberately narrow:

```text
generic_capability: grouped_reduction
app_probe: raydb_style
closed_as_reusable_engine_capability: true
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_authorized: false
app_specific_native_engine_logic_allowed: false
```

RayDB grouped_reduction is real V3 engine evidence, but it is not V3 release authorization,
not a database product claim, not broad V3-over-V2.x evidence, and not proof
that the Gap-1 productized execution path is complete.

## Retained Rows

Exactly three grouped-reduction rows remain in the current internal
13-row / 9-capability Phoenix surface:

| Row | Packet | Status |
| --- | --- | --- |
| `grouped_reduction_sum_scalar_broadcast_repeat100_262144` | `docs/rebuild/v3/phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2026-06-21.json` | scoped row evidence after Claude/Codex consensus; not release authorization |
| `grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups` | `docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.json` | scoped row evidence after real Claude external review plus Codex supersession consensus; not release authorization |
| `grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups` | `docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.json` | scoped row evidence after real Claude external review plus Codex supersession consensus; not release authorization |

For all three rows:

- the generic capability is `grouped_reduction`;
- the contract is fixed and row-scoped;
- CPU-reference agreement is recorded;
- app-specific native engine logic is not allowed;
- native engine customization is recorded as false;
- release, whole-app, and broad V3-over-V2.x claims remain false.

Supersession note for the two device-column rows: the earlier
`subagent_codex_consensus_complete` record is historical only. Current closure
comes from
`docs/reviews/claude_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_review_2026-06-22.md`
and
`docs/reviews/codex_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_claude_supersession_consensus_2026-06-22.md`.
Claude required two P1 fixes: replace the subagent-status fields with real
Claude/Codex supersession status, and acknowledge that the source manifest does
not hash local orchestration wrappers. Both fixes are recorded in the updated
device-column packet.

## Why This Stays In V3

The rows are evidence for a reusable grouped-reduction engine capability, not
for a RayDB product. They carry exact row identities, source provenance records,
review/consensus closure, and explicit forbidden wording. Removing them would
throw away one of the strongest pieces of M0-M149 generic performance work.

## Why This Does Not Release V3

The serious same-hardware V2.14 vs Phoenix V3 paired run still controls the
major-version release decision:

```text
same_metric_comparison_count: 52
overall_geomean_v3_speedup_vs_v2_14: 1.0117790403434224
apps_with_geomean_gt_1_05: 1
apps_with_geomean_lt_0_95: 2
release_consideration_eligible: false
```

Those facts mean a grouped_reduction row win cannot be turned into a broad V3
claim. It remains row-scoped internal release-surface evidence.

## Gap-1 Boundary

The grouped_reduction rows do not complete Gap 1. They prove exact
grouped_reduction capability and device-column input-path improvements, but
they do not prove that the productized prepared execution/session runner
executes across multiple Set-A probes.

For the next all-app scorecard, bounded RayDB grouped_sum/count rows should be
treated as Set-B or row-scoped controls unless they are routed through a
productized multi-phase execution path shared by other Set-A probes. The
classification must be frozen before the run.

## Forbidden Readings

- Do not claim V3 is release-ready because RayDB grouped_reduction has large
  row-scoped wins.
- Do not claim RTDL is a database engine.
- Do not claim RayDB is accelerated end to end.
- Do not claim grouped_reduction proves broad V3-over-V2.x speedup.
- Do not claim the device-column rows prove true zero-copy.
- Do not claim grouped_reduction completes Gap 1.
- Do not describe Embree/device-column ratios as pure backend-only ratios.

## Next

Keep grouped_reduction in the current 13-row / 9-capability internal surface.
Do not spend more Phoenix time on RayDB-specific grouped_sum variants unless
the work lands in a shared grouped_reduction or productized runner primitive.
The next Phoenix engineering target should be a second Set-A runner-backed
family or a shared continuation path such as RTDBSCAN `component_union`.

## Goal-Level Decision Audit

Decision: close RayDB grouped_reduction for Phoenix redo as retained reusable
engine evidence, not as V3 release evidence or Gap-1 completion.

1. Was I foolish?

   No. The decision preserves the strongest exact grouped_reduction rows while
   refusing to over-read them as broad V3 success.

2. If yes, what actions made the decision foolish?

   It would be foolish to headline the large row-scoped speedups as V3 release
   performance, call RayDB a solved database product, or treat grouped_sum row
   closure as the productized execution path.

3. Was there another path?

   Delete or demote all RayDB grouped_reduction work. That would throw away real
   reusable engine evidence and repeat the mistake of ignoring M0-M149 work.

4. Can I now try a different path?

   Retain the exact rows, document the non-release boundary, and move Phoenix
   work to shared runtime paths that can affect multiple probes.
