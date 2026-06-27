# Review Debt: Goal4768 RT-BarnesHut Preprocessing Sort Bottleneck

Date: 2026-06-26

Status: **open review debt**

Goal4768 completed a focused 10M profiling pass for the native V4
RT-BarnesHut author-semantics route. It has not yet received the required
external 3-AI completion audit.

## Artifact Under Review

- `future/v4/v4_goal4768_rt_barneshut_preprocessing_sort_bottleneck_2026-06-26.md`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4768_benchmark_ready_10m_pod_2026-06-26.json`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4768_10m_phase_profile_pod_2026-06-26.jsonl`

## Key Facts

Correctness:

- native force checksum: `53.746751351154444`;
- author RT force checksum: `53.7468`;
- checksum relative error: `9.051486889720442e-7`;
- tolerance pass: true.

Native route status:

- `implementation_status_code=3`;
- `rt_core_execution=true`;
- `host_fallback_used=false`;
- `input_columns_downloaded_for_tree_build=true`.

Timing:

- native warm RT-force: `0.886653679s`;
- authors' binary RT-force: `1.0172s`;
- native warm execution: `7.432850354s`;
- authors' binary execution: `1.68573s`.

Dominant measured native phase:

- warm `sort_seconds`: `6.16351s`;
- warm `launch_seconds`: `0.647495s`;
- warm `accel_build_seconds`: `0.00803325s`;
- warm `dfs_metadata_seconds`: `0.0150561s`;
- warm `auto_rope_seconds`: `0.0111561s`.

Accounting correction:

- The authors' printed `Preprocessing Time` in the current binary excludes
  sort/tree-build time.
- Therefore the earlier direct comparison between RTDL native preprocessing
  and author printed preprocessing is not a fair phase comparison.
- The complete workflow gap remains real because total execution is still
  `7.432850354s` native vs `1.68573s` author.

## Questions For Reviewer

1. Is the Goal4768 interpretation honest: native RT-force succeeds, but the
   complete workflow is blocked by host z-order sort?
2. Is the accounting correction sufficient to prevent misuse of the authors'
   printed `Preprocessing Time`?
3. Is `std::sort` replacing `std::stable_sort` acceptable given the explicit
   `original_id` comparator tie-break and checksum parity?
4. Should Goal4769 prioritize author-equivalent phase accounting or RTDL sort
   optimization first?
5. Does this evidence still justify continuing RT-BarnesHut V4 engineering, or
   should the route remain candidate-only until sort is fixed?

## Requested Verdict Labels

Use one:

- `accept_goal4768_complete_target_sort_next`
- `accept_with_required_amendments`
- `reject_requires_rework`
- `blocked_need_more_evidence`

## Non-Authorization

This review debt does not authorize:

- V4 release;
- public RT-BarnesHut paper-reproduction wording;
- public speedup claims;
- V2/V3/V4 RT-BarnesHut speed tables;
- no-copy/device-resident tree-build claims;
- broad V4 high-performance release claims.

