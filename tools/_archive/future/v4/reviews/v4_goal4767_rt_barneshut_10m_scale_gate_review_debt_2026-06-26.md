# Review Debt: Goal4767 RT-BarnesHut 10M Scale Gate

Date: 2026-06-26

Status: **open review debt**

Goal4767 completed a 10M Treelogy same-POD native-vs-author run. It has not yet
received the required external 3-AI completion audit.

## Artifact Under Review

- `future/v4/v4_goal4767_rt_barneshut_10m_scale_gate_2026-06-26.md`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4767_benchmark_ready_10m_pod_2026-06-26.json`

## Key Facts

Correctness:

- native force checksum: `53.746751351154444`;
- author RT force checksum: `53.7468`;
- checksum relative error: `9.051486889720442e-7`;
- passes tolerance: true.

RT-force:

- native warm RT-force: `0.906343331s`;
- authors' binary RT-force: `1.01614s`.

Full execution:

- native warm execution: `7.130341762s`;
- authors' binary execution: `1.61694s`.

Dominant blocker:

- native preprocessing/tree build: `6.179594029s`;
- authors' preprocessing: `0.520493s`;
- native route still has `input_columns_downloaded_for_tree_build=true`.

Goal4768 accounting correction:

- The authors' printed `Preprocessing Time` excludes sort/tree-build time and
  is not directly comparable to RTDL native preprocessing.
- The complete execution gap remains real, but reviewers should use Goal4768's
  phase profile for the precise blocker: RTDL host z-order sort dominates at
  about `6.16s` on 10M.

## Questions For Reviewer

1. Is the report's interpretation honest: RT-force candidate succeeds, but full
   workflow is blocked by preprocessing?
2. Is it acceptable to call this a 10M RT-core force-path success while blocking
   paper-reproduction and speedup wording?
3. Should Goal4768 optimize current host preprocessing, move tree metadata
   construction toward device-resident staging, or port the authors'
   preprocessing more literally?
4. Is the custom-primitive control geometry still acceptable after the 10M
   checksum match, or does paper-facing wording require literal triangle
   geometry?
5. Does this evidence justify continuing RT-BarnesHut V4 engineering, or should
   the route be kept as an appendix/candidate until preprocessing is fixed?

## Requested Verdict Labels

Use one:

- `accept_goal4767_complete_target_preprocessing_next`
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
