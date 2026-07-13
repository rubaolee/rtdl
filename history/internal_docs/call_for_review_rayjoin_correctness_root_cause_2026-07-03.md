# Call For Review: RayJoin Correctness Root Cause And Resolution

Claude, please review this correctness postmortem:

```text
history/internal_docs/rayjoin_correctness_problem_root_cause_and_resolution_2026-07-03.md
```

## Context

The user asked for a detailed explanation of:

- what correctness problems we encountered;
- why they took several days to solve;
- what the root causes were;
- how we solved them;
- which parts are generic RTDL repairs rather than RayJoin-only patches.

This review should be strict. The main risk is that the document could make the
work sound cleaner than it was, omit a root cause, or accidentally overclaim the
current RayJoin reproduction result.

## Requested Verdict Labels

Use one of:

- `approve_rayjoin_correctness_root_cause_postmortem`
- `approve_with_required_amendments`
- `block_until_root_cause_or_boundaries_fixed`

## Questions

1. Does the document correctly identify the main correctness defects:
   - PIP/SoS `t_reported` tie policy;
   - per-map midpoint face overwrite;
   - nonfinite midpoint/query filtering;
   - rational midpoint construction;
   - old nondeterministic author-output trap;
   - LSI count-vs-row materialization gap;
   - duplicate-half-edge deterministic face selection?
2. Does it explain why correctness took days without excusing inefficient early
   debugging?
3. Does it correctly state that full-stream diffs are final gates, not ideal
   first-debugging tools?
4. Does it correctly distinguish Section 5.2 count success from Section 5.7
   overlay row/output correctness?
5. Does it correctly describe `AuthorOfficial = Author+RTDLContractPatch` as the
   deterministic intended comparator?
6. Does it preserve the boundary between generic RTDL core contract repairs and
   RayJoin application logic?
7. Does it avoid all-eight hidden-input, broad speedup, Embree, and
   Numba-correctness-critical overclaims?
8. Are the listed remaining limits and lessons accurate?

## Non-Authorization

This review does not authorize new runtime changes, new performance claims,
V3/V4 resurrection, Embree claims, full hidden-input all-eight claims, or public
release wording beyond the already bounded v2.14 RayJoin page.
