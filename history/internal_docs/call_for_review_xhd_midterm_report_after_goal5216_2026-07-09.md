# Call For Review: X-HD Midterm Report After Goal5216

Date: 2026-07-09

Please strictly review the X-HD midterm report and current project status after
Goal5216.

Primary document under review:

```text
history/internal_docs/xhd_midterm_report_after_goal5216_2026-07-09.md
```

Supporting result documents:

```text
history/internal_docs/goal5211_global_bound_early_break_result_2026-07-09.md
history/internal_docs/goal5212_all_source_no_copy_selection_result_2026-07-09.md
history/internal_docs/goal5213_global_bound_initial_state_matrix_no_go_result_2026-07-09.md
history/internal_docs/goal5214_exact_dataset_availability_refresh_result_2026-07-09.md
history/internal_docs/goal5215_public_artifact_availability_sweep_result_2026-07-09.md
history/internal_docs/goal5216_level_b_representative_consolidation_result_2026-07-09.md
```

Machine-readable evidence:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5216_level_b_representative_consolidation_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5214_exact_dataset_availability_refresh_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5215_public_artifact_availability_sweep_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5212_all_source_no_copy_fresh_graphics_dragon_happy_buddha_2026-07-09.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5212_all_source_no_copy_warm_protocol_graphics_dragon_happy_buddha_2026-07-09.json
```

## Context

The project goal is full X-HD paper reproduction, but current evidence supports
only a Level-B same-source representative reproduction packet:

```text
Workload: public Stanford Dragon -> HappyBuddha
Author HDResult: 0.12572988867759705
RTDL HDResult:   0.12572988629271128
RTDL fresh route wall: ~0.852s
RTDL full gate including input load: ~1.531s
RTDL explicit-warm measured route: ~0.288s
```

Exact paper input datasets remain unavailable:

```text
/local/storage/shared/HDDatasets is missing in the current POD;
public source repository provides scripts/logs but no input bytes/hashes;
no deterministic reconstruction provenance proves byte identity.
```

## Requested Verdict Labels

Choose one:

```text
approve_xhd_midterm_level_b_status_and_plan
approve_with_required_amendments
revise_xhd_midterm_report_before_level_b_closeout
block_due_to_overclaim_or_missing_evidence
```

## Review Questions

1. Does the report correctly distinguish Level-B same-source representative
   reproduction from Level-C exact paper dataset reproduction?

2. Does it avoid claiming full X-HD paper reproduction, exact paper dataset
   identity, author parity, or denominator-aligned author-vs-RTDL performance
   ratio?

3. Are the current headline numbers stated with the correct regime labels:
   fresh route, full gate including input load, and explicit-warm measured route
   with warmup reported separately?

4. Is the exact dataset blocker described correctly and strongly enough? In
   particular, does the report avoid treating matching point counts, same public
   source family, or matching HDResult as proof of byte-identical paper input
   identity?

5. Is the system/app boundary correct? That is, does the report correctly state
   that RTDL owns generic nearest/frontier/reduction/traversal machinery while
   X-HD app code owns paper inputs, author wrappers, tolerance policy, and
   comparators?

6. Does the report fairly characterize Goal5211 global-bound early break as a
   generic max-nearest / directed-Hausdorff optimization with approximate
   per-source witnesses on early-aborted sources, rather than a default exact
   nearest-witness primitive?

7. Does the next-step plan correctly prioritize review, Level-B stabilization,
   and exact-dataset provenance over more route micro-optimization?

8. Is the proposed optional same-POD performance matrix useful and sufficiently
   careful about denominator alignment?

9. Are there any missing required documents or evidence files that should be
   reviewed before accepting the midterm status?

10. Should the project be allowed to close the current phase as "Level-B
   representative reproduction plus system extraction" if exact paper datasets
   remain unavailable?

## Specific Claims To Scrutinize

Please attack these claims harshly:

```text
Claim A:
  The current X-HD status is Level-B representative reproduction, not full paper
  reproduction.

Claim B:
  The current route matches author HDResult on public Stanford
  Dragon -> HappyBuddha, but exact paper dataset identity remains unproved.

Claim C:
  The current route is built from generic RTDL system components rather than an
  X-HD-specific RTDL primitive.

Claim D:
  The reported performance numbers are not author-vs-RTDL ratios and should not
  be interpreted as parity or speedup.

Claim E:
  The next meaningful blocker for full paper reproduction is exact input
  provenance, not another route micro-optimization.
```

## Expected Answer Shape

Please answer in this format:

```text
Verdict:
<one requested verdict label>

Blocking findings:
- <finding or "None">

Required amendments:
- <amendment or "None">

Non-blocking notes:
- <note or "None">

Answers to review questions:
1. ...
2. ...
...
10. ...

Allowed final summary:
<the strongest wording that may be used after this review>

Forbidden summaries:
- <any phrases/claims that must not be used>
```

## Non-Authorization Boundary

This review must not authorize:

```text
full X-HD paper reproduction complete;
exact paper dataset reproduction complete;
author-vs-RTDL performance ratio;
author parity;
warm-only headline;
X-HD-specific RTDL primitive claim;
exact paper figure reproduction.
```
