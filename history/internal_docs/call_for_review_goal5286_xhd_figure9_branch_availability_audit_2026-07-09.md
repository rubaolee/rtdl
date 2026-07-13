# Call For Review - Goal5286 X-HD Figure 9 Branch Availability Audit

Date: 2026-07-09

## Review Scope

Please strictly review Goal5286, which audits all pinned X-HD author branches
for the Figure 9 `run_all/auto_tune` variants missing after Goal5285.

This is a source/log availability goal.  It is not a Figure 9 reproduction
claim, not a new RTDL route, and not a performance ratio.

## Files To Review

```text
history/internal_docs/goal5286_xhd_figure9_branch_availability_audit_result_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_figure9_branch_availability_audit.py
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5286_figure9_branch_availability_audit_2026-07-09.json
tests/goal5286_xhd_figure9_branch_availability_audit_test.py
```

Relevant prior evidence:

```text
history/internal_docs/goal5285_xhd_figure9_source_script_audit_result_2026-07-09.md
history/internal_docs/call_for_review_goal5285_xhd_figure9_source_script_audit_2026-07-09.md
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5285_figure9_source_script_audit_2026-07-09.json
```

## Evidence Summary

Goal5286 reports:

```text
status = missing_figure9_variants_not_found_on_pinned_branches__figure9_not_reproduced
any_branch_has_all_expected_figure9_variants = false
figure9_reproduced = false
```

Pinned branch heads:

```text
paper  = 8c3846866052e1e8755210021f23fac2cbe8c3d6
main   = 7bf41c8442d059c94f4178355c6d5a10571d9658
hybrid = 4d9046a9e55d87f35daf81dd718444029fab56ce
```

Branch evidence:

```text
paper:
  run_all/auto_tune records = 1814
  observed configs = false/false and true/true only
  checked-in expr/for_the_paper/auto-tune.pdf exists

main:
  run_all/auto_tune records = 0
  Figure-9-like script/PDF files absent

hybrid:
  run_all/auto_tune records = 0
  Figure-9-like script/PDF files absent
```

Critical boundary:

```text
checked-in PDF != reproducible Figure 9 denominator
```

## Review Questions

1. Does Goal5286 correctly audit all pinned branches listed in the X-HD
   provenance?
2. Is it correct that `paper` still has only two of the four expected variants?
3. Is it correct that `main` and `hybrid` do not contain the missing variants?
4. Is it correct to record the checked-in `auto-tune.pdf` as evidence but not
   promote it to Figure 9 reproduction?
5. Is `figure9_reproduced=false` still the right status after this audit?
6. Does the goal avoid RTDL core changes, RTDL route claims, and performance
   ratios?
7. Is the next step correct: regenerate/recover the missing author-side
   denominator or externally map training sweeps before any more RTDL route work?
8. Can Goal5286 be marked externally reviewed and approved, or are amendments
   required?

## Expected Answer Shape

```text
Verdict: approve / approve_with_required_amendments / block
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to questions 1-8:
Requested verdict label:
```

If approving, please use or adapt:

```text
approve_goal5286_xhd_figure9_branch_availability_audit__missing_variants_not_recovered
```
