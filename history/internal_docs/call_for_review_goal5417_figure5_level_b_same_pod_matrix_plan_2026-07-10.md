# Call For Review — Goal5417 Figure 5 Level-B Same-POD Matrix Plan

Please strictly review Goal5417:

```text
Goal5417 — Figure 5 Level-B same-POD matrix plan
```

Files to inspect:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5417_figure5_level_b_same_pod_matrix_plan.json
tests/goal5417_figure5_level_b_same_pod_matrix_plan_test.py
history/internal_docs/goal5417_figure5_level_b_same_pod_matrix_plan_2026-07-10.md
history/internal_docs/goal5416_xhd_full_reproduction_blocker_priority_refresh_2026-07-10.md
```

Supporting evidence to spot-check:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5298_author_graphics_precheck_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5291_figure5_dragon_happy_candidate_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5299_thai_happy_level_b_rtdl_comparison_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5300_thai_asian_level_b_rtdl_comparison_matrix_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5305_county_zcta_rtdl_triton_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5307_water_bg_author_rtdl_partner_gate_summary_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5290_figure5_graphics_author_value_precheck_2026-07-09.json
```

Context:

- Goal5416 chose Figure 5 Level-B matrix planning as the next practical
  full-reproduction mainline.
- Goal5417 does not execute the matrix.  It defines candidate inclusion,
  exclusion, denominator columns, tools, and forbidden claims.
- Exact paper datasets remain unavailable, so this is Level-B only.

Review questions:

1. Are the three primary graphics candidates correctly included?
2. Is `dragon_asian_scaled` correctly excluded because author rerun does not
   match the paper-branch author-log value?
3. Are the bounded geo candidates correctly labeled as secondary bounded rows,
   not full geo Figure 5?
4. Does the denominator column list keep author internal time, author process
   wall, RTDL route wall, RTDL process wall, load time, witness exactness, and
   cold/warm process separate?
5. Is it correct that Goal5417 does not authorize any ratio?
6. Is the planned use of `run_xhd_goal5298_author_graphics_precheck.py`,
   `run_xhd_rtdl_hd_exec.py`, and `run_xhd_rtdl_hd_exec_summary_batch.py`
   sufficient for a subsequent Goal5418 execution?
7. Does the plan correctly require `scripts/current_pod_ssh.py` and forbid
   naked SSH?
8. Does the plan avoid Figure 5 reproduction, exact dataset, performance
   parity, and full paper overclaims?

Expected answer shape:

```text
Verdict: approve / approve_with_required_amendments / reject

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
...
8. ...
```

Requested verdict label if approved:

```text
approve_goal5417_figure5_level_b_same_pod_matrix_plan
```
