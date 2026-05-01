# Goal1061 Claude External Review

Date: 2026-04-28
Reviewer: Claude (Sonnet 4.6)

## Verdict

**ACCEPT**

The candidate wording for `event_hotspot_screening / prepared_count_summary` is
numerically accurate, correctly bounded, passes both project timing floors, and
carries no pre-existing public authorization that would need to be unwound.

## Evidence Traced

| Check | Source | Result |
| --- | --- | --- |
| RTX phase value | `prepared_count_summary.json` → `scenario.timings_sec.optix_query` | `0.16599858924746513` s — rounds correctly to `0.165999` s |
| Phase key in wording | Goal1061 packet vs. artifact JSON | `scenario.timings_sec.optix_query` matches exactly |
| Fastest baseline | Goal1060 audit JSON row for `event_hotspot_screening` | `embree_summary_path` at `0.2566157499095425` s; confirmed this is the minimum of all three timed baselines |
| Ratio | `0.2566157499095425 / 0.16599858924746513` | `1.5458911...` → `1.55x` is correct at two significant figures |
| 100 ms floor | RTX phase = 165.99 ms | Passes |
| 1.20x margin floor | Ratio = 1.546 | Passes |
| Sub-10 ms warning | Goal1060 audit JSON, row warnings field | Empty (`[]`) — no small-scale repeat-evidence flag on this row |
| Correctness parity | All three timed baselines in Goal1060 JSON | `correctness_parity: true` for `cpu_oracle_summary`, `embree_summary_path`, `scipy_ckdtree` |
| Prior public authorization | Goal1060 JSON `public_speedup_claim_authorized: false`, `public_speedup_claim_authorized_count: 0` | None; wording status is `public_wording_not_reviewed` (not blocked) |

## Reviewer Questions — Answers

**Is the wording strictly limited to the prepared count-summary query phase?**
Yes. The wording names `optix_query` specifically and excludes `input_build`,
`optix_prepare`, and `python_postprocess`. The source artifact boundary statement
("separates input construction, OptiX preparation, prepared query, and Python
postprocess") is faithfully reflected.

**Does the wording avoid whole-app, default-mode, broad RT-core, and
Python-postprocess claims?**
Yes. The candidate wording explicitly excludes whole-app, default-mode,
neighbor-row output, Python-side postprocessing, validation, and unrelated
application stages. These exclusions match the artifact's `cloud_claim_contract`
`non_claim` field verbatim.

**Is the use of `1.55x` defensible from the Goal1060 ratio and source artifact?**
Yes. The computed ratio is `1.5458911492734937`. Rounding to two significant
figures gives `1.55`. The comparison is against the single fastest timed
same-semantics non-OptiX baseline (`embree_summary_path`), which is the correct
denominator per project wording gate rules.

**If accepted, should `rtdsl.rtx_public_wording_matrix()` promote only this
sub-path to `public_wording_reviewed` while keeping
`public_speedup_claim_authorized_count` at `0`?**
Yes. Accepting this wording review changes only the wording status for
`event_hotspot_screening / prepared_count_summary` from `public_wording_not_reviewed`
to `public_wording_reviewed`. The gate `public_speedup_claim_authorized_count`
stays at `0` until a separate authorization step is taken. Facility and robot
remain `public_wording_blocked` and are unaffected.

## Observations and Caveats

1. **Artifact directory naming**: The source artifact lives in
   `docs/reports/goal1052_post_goal1048_cloud_batch/` but is referred to as a
   "Goal1058 artifact" in the packet and consensus. This is a naming convention
   established in Goal1060 and confirmed by the two-AI consensus; it is not a
   data integrity issue.

2. **Single-run evidence**: The source artifact represents one RTX A5000 run at
   20 000 copies. The 165 ms phase is comfortably above the 100 ms floor, and no
   sub-10 ms warning applies, so this passes the current gate. Repeat-run
   evidence would strengthen a future full public speedup claim authorization
   beyond the wording review stage.

3. **Ratio rounding direction**: `1.5459` rounds to `1.55`, not `1.54`. Rounding
   at two significant figures is conservative in the sense that it is a faithful
   representation; a reader who computed the ratio independently would arrive at
   the same figure. No overclaim risk.

## Boundary Confirmation

This review covers only:
- Accuracy and boundedness of the candidate wording for
  `event_hotspot_screening / prepared_count_summary`

This review does **not**:
- Authorize a public RTX speedup claim
- Change `public_speedup_claim_authorized_count`
- Review or unblock `facility_knn_assignment` or `robot_collision_screening`
- Authorize whole-app, default-mode, or release-facing speedup wording
