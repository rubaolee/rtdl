# Call For Review - Goal5187 X-HD Full Public RTDL All-Source Route-Only Gate

Please strictly review Goal5187:

```text
history/internal_docs/goal5187_full_public_all_source_route_only_result_2026-07-08.md
```

Primary evidence:

```text
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
tests/goal5187_xhd_full_public_route_only_gate_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_route_only_goal5187_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_author_hd_exec_goal5186_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_author_gate_summary_goal5186_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
```

## Context

Goal5186 ran author `hd_exec` on the full public Stanford Dragon/HappyBuddha
Level-B candidate:

```text
source points = 437645
target points = 543652
author HDResult = 0.12572988867759705
```

Goal5187 runs the RTDL scalable route over the same full public source and
target, skips the impossible full exact oracle, and compares to the Goal5186
author `HDResult`:

```text
RTDL route distance = 0.12572988629271128
author abs diff = 2.3848857610975216e-09
author tolerance = 1e-6
matched = true
```

This is Level B all-source route-only author-comparison evidence. It is not
exact paper dataset identity, not exact-oracle validation, not full paper
reproduction, and not a performance ratio.

## Requested Review Questions

1. Does the artifact prove that RTDL consumed all `437645` source points and all
   `543652` target points, rather than a bounded source subset?
2. Does the route result match the Goal5186 author `HDResult` within the stated
   tolerance, with `author_abs_diff ~= 2.38e-9`?
3. Is it acceptable that the full all-source run is route-only and skips exact
   oracle validation, given the `237926579540` point-pair exact route estimate?
4. Does the script fail closed by requiring an author comparator when
   `--skip-exact-oracle` is used?
5. Are the claim flags correct: `full_all_source_route_run_claimed=true`,
   `exact_oracle_claimed=false`, `performance_ratio_claimed=false`,
   `exact_paper_dataset_reproduction_claimed=false`, and
   `full_paper_reproduction_claimed=false`?
6. Does the metadata avoid the old bounded-subset wording after the Goal5187
   correction (`status=full_public_candidate_all_source_route_only_checked`,
   `bounded_subset_scaling_claimed=false`)?
7. Are the route phase timings useful for future optimization while still not
   authorizing an author-vs-RTDL performance ratio?
8. Does this goal preserve the RTDL-as-generic-system principle, i.e. it uses
   generic cell-MBR/frontier/nearest APIs and does not add X-HD-specific core
   primitives?
9. Should Goal5187 be approved as the current strongest Level B
   Dragon/HappyBuddha route evidence, or is any amendment required?

## Expected Answer Shape

Please answer with:

```text
Verdict: <approve / approve_with_required_amendments / revise / block>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Question answers:
1. ...
2. ...
...
9. ...

Requested verdict label if approved:
approve_goal5187_full_public_all_source_route_only_author_match_level_b_only
```

## Non-Authorized Claims

Please fail the review if the package claims any of:

```text
exact oracle validation of the all-source result
exact paper dataset reproduction
full X-HD paper reproduction
Figure 5 reproduction
author-vs-RTDL speedup/parity/performance ratio
public Stanford files are byte-identical to author local files
```
