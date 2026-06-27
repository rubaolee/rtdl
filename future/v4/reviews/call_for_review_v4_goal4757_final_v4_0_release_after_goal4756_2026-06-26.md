# Call For Review: V4 Goal4757 Final V4.0 Release After Goal4756

Please review:

`future/v4/v4_goal4757_final_v4_0_release_packet_after_goal4756_2026-06-26.md`

## Context

The old V4 framing was too narrow: it had bounded operator scorecards but no
complete app-level V2.14/V3/V4 matrix. Goal4756 corrected that by running all
10 promoted benchmark apps across V2.14, V3.0.2, and V4.0 on the same NVIDIA
RTX A5000 RT-core POD, with no `n/a` rows and no Embree primary denominator.

The current candidate claim is not "all apps are faster." It is:

```text
RTDL V4.0 is a Python eDSL/operator-pushdown release candidate and V2/V3
superset with a complete 10-app NVIDIA RT-core matrix, two material hot-path
candidate wins over V2.14, parity/control elsewhere, and separate bounded V4
operator/workflow wins.
```

## Evidence To Inspect

- Release packet:
  `future/v4/v4_goal4757_final_v4_0_release_packet_after_goal4756_2026-06-26.md`
- Matrix evidence:
  `future/v4/evidence/v4_goal4756_serious_all30_generated_spatial_2026-06-26/`
- Matrix analysis:
  `future/v4/evidence/v4_goal4756_final_rt_core_matrix_analysis_2026-06-26.json`
- Matrix readout:
  `future/v4/v4_goal4756_final_rt_core_matrix_release_readout_2026-06-26.md`
- Full V4 local test log:
  `future/v4/evidence/v4_goal4759_full_v4_unittest_discover_with_review_manifest_2026-06-26.log`
- Goal4757 machine gate:
  `src/rtdsl/v4_goal4757_final_release_packet.py`
  `tests/v4_goal4757_final_release_packet_test.py`
- Goal4758 local completion audit:
  `future/v4/v4_goal4758_local_completion_audit_2026-06-26.md`
  `src/rtdsl/v4_goal4758_local_completion_audit.py`
  `tests/v4_goal4758_local_completion_audit_test.py`
- Final review evidence manifest:
  `future/v4/evidence/v4_goal4759_final_review_evidence_manifest_2026-06-26.json`
  `future/v4/v4_goal4759_final_review_evidence_manifest_2026-06-26.md`
- Public docs:
  `README.md`
  `docs/current_v4_status.md`
  `docs/app_level_benchmark_summary.md`
  `docs/learn/performance_wording.md`
  `future/v4/README.md`

## Questions

1. Is V4 correctly treated as a V2/V3 superset rather than a replacement that
   disables old routes?
2. Is the Goal4756 matrix complete and fair enough for V4.0 release wording?
3. Are the two material V4/V2.14 hot-path candidates, Triangle and Barnes-Hut,
   described honestly?
4. Is Barnes-Hut correctly blocked from being described as a new V4-over-V3
   speedup?
5. Is Spatial RayJoin correctly described as serious generated-input parity,
   not a speedup?
6. Do the docs clearly distinguish app-level matrix claims from operator
   scorecard claims?
7. Is the current public wording acceptable for a V4.0 public tag?

## Required Verdict

Please choose exactly one:

- `approve_v4_0_release_candidate_for_public_tag`
- `approve_with_required_wording_or_evidence_amendments`
- `block_release_pending_specific_fixes`
- `reject_release_reframe_required`

If the verdict is not approval, please list the exact blocking files, claims,
or evidence rows to fix.

## Non-Authorization

This review request does not itself authorize public tagging. It asks for the
external verdict required before public V4.0 release.
