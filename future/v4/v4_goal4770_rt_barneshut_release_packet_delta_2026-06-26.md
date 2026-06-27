# Goal4770 - RT-BarnesHut Release Packet Delta

Date: 2026-06-26

Status: **completed as release-packet delta, pending external review debt**

## Purpose

Goal4770 updates the current V4 release evidence after Goal4769 corrected the
RT-BarnesHut phase denominator.

It does not rewrite the historical Goal4756 app matrix. Goal4756 remains the
complete V2.14/V3.0.2/V4.0 30-row matrix. Goal4770 is a delta: it adds the
newer 10M author-semantics RT-BarnesHut route evidence to the current release
packet and public docs.

## Evidence

Machine delta:

- `future/v4/evidence/v4_goal4770_rt_barneshut_release_packet_delta_2026-06-26.json`

Source evidence:

- `future/v4/v4_goal4768_rt_barneshut_preprocessing_sort_bottleneck_2026-06-26.md`
- `future/v4/v4_goal4769_rt_barneshut_author_phase_accounting_2026-06-26.md`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4768_benchmark_ready_10m_pod_2026-06-26.json`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4768_10m_phase_profile_pod_2026-06-26.jsonl`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4769_author_phase_print_false_10m_stdout.txt`

## Corrected Barnes-Hut Reading

The older aggregate-frontier Barnes-Hut row remains:

- V4/V2.14 hot: `286.142x`;
- V4/V3.0.2 hot: `0.993x`;
- reading: material V3/V4-over-V2.14 candidate, not a new V4-over-V3 speedup.

The newer author-semantics RT-core route adds this supplemental evidence:

| Metric | RTDL V4 native | Authors' binary | Reading |
|---|---:|---:|---|
| 10M checksum relative error | `9.051486889720442e-7` | reference | Passes same-input author-semantics tolerance. |
| z-order sort | `6.16351s` | `6.87096s` | RTDL about `1.115x` faster. |
| sort + tree basis | `6.503060236s` | `8.58458s` | RTDL about `1.320x` faster. |
| RT-force | `0.886653679s` | `1.12905s` | RTDL about `1.273x` faster. |
| internal program time | `~7.513s` | `10.4391s` | RTDL about `1.389x` faster. |

The key correction is that the authors' artifact-mode `Execution time` excludes
sort/tree build. It must not be used as the full-workflow denominator.

## Current Release Classification

Barnes-Hut should now be described as:

```text
The historical 10-app matrix keeps Barnes-Hut as a material V3/V4-over-V2.14
aggregate-frontier candidate, not a new V4-over-V3 speedup. Separately, the
newer native RT-BarnesHut author-semantics route is checksum-valid at 10M and
wins against the authors' binary on comparable internal program time after the
authors' full phase table is exposed.
```

This is a stronger and more accurate status than the earlier "full workflow
author loss" reading.

## Still Blocked

Goal4770 does not authorize:

- public RT-BarnesHut paper-reproduction wording;
- broad V4 speedup wording;
- V2/V3/V4 public RT-BarnesHut speed table;
- no-copy or device-resident tree-build wording;
- literal author triangle geometry wording;
- public V4 tag.

## Files Updated

- `README.md`
- `docs/current_v4_status.md`
- `docs/app_level_benchmark_summary.md`
- `future/v4/v4_goal4757_final_v4_0_release_packet_after_goal4756_2026-06-26.md`
- `future/v4/v4_goal4759_final_review_evidence_manifest_2026-06-26.md`
- `future/v4/V4_CURRENT_AGENT_REFRESH_RUNBOOK_2026-06-25.md`

## Goal-Level Decision Audit

1. Was I being stupid?
   - No for this delta. It would be stupid to overwrite the historical Goal4756
     matrix or to keep reporting the stale author-loss interpretation after
     Goal4769 corrected the denominator.

2. What action would make this stupid?
   - Using the Goal4769 internal-program win to claim public paper reproduction
     or no-copy tree build.

3. Is there another path?
   - Yes: rerun a full public V2/V3/V4 RT-BarnesHut table immediately. That is
     premature because paper-facing wording still needs external review of
     geometry and claim boundaries.

4. Can I now try the different path that actually solves the problem?
   - Yes. Keep Goal4770 as a release-packet delta, then send Goals4768-4770 to
     external review before public wording changes become release claims.
