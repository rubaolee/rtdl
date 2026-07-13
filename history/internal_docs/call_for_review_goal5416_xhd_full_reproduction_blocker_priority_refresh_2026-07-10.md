# Call For Review — Goal5416 X-HD Full Reproduction Blocker Priority Refresh

Please strictly review Goal5416:

```text
Goal5416 — Full reproduction blocker priority refresh after stopping current -lb line
```

Files to inspect:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5416_full_reproduction_blocker_priority_refresh.json
tests/goal5416_full_reproduction_priority_refresh_test.py
history/internal_docs/goal5416_xhd_full_reproduction_blocker_priority_refresh_2026-07-10.md
history/internal_docs/goal5415_xhd_stop_or_bounded_trace_gate_decision_2026-07-10.md
history/internal_docs/xhd_comprehensive_midterm_status_after_goal5414_2026-07-10.md
```

Context:

- Goal5415 stops the current explicit `-lb` row-identity line.
- Full X-HD paper reproduction remains incomplete.
- Exact paper input provenance remains the primary full-paper blocker.
- Figure 5 has the strongest author-log coverage and current Level-B
  value-matched candidates.

Goal5416 chooses the next mainline:

```text
1. exact input provenance remains first in principle;
2. the next executable planning focus is Figure 5 Level-B same-POD matrix;
3. Figures 7/8/9/10/11 stay blocked/closed without new author denominators;
4. generic system extraction continues only with non-X-HD evidence.
```

Review questions:

1. Does Goal5416 correctly keep full X-HD paper reproduction open/incomplete?
2. Does it correctly keep exact input provenance as the primary blocker?
3. Is Figure 5 the right next practical focus given current author-log and
   Level-B candidate evidence?
4. Does it correctly keep Figure 7 closed after Goal5415 and avoid restarting
   `-lb` row-identity probing?
5. Does it correctly mark Figures 8/9/10/11 as blocked/closed under current
   evidence?
6. Does it avoid author-vs-RTDL performance ratios and require separated
   denominators?
7. Is Goal5417 correctly scoped as a matrix plan/spec before any POD execution?
8. Are any claims still too broad?

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
approve_goal5416_xhd_full_reproduction_priority_refresh_figure5_level_b_next
```
