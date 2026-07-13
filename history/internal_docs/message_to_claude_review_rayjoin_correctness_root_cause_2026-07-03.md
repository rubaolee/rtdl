# Message To Claude: Review RayJoin Correctness Root-Cause Postmortem

Claude, please review:

```text
history/internal_docs/call_for_review_rayjoin_correctness_root_cause_2026-07-03.md
history/internal_docs/rayjoin_correctness_problem_root_cause_and_resolution_2026-07-03.md
```

Please be skeptical. The user wants to understand why this correctness work took
days, what the real root causes were, and whether we actually fixed generic
RTDL contracts rather than slipping RayJoin-specific hacks into the system.

The most important things to check:

1. Are the listed defects complete and technically accurate?
2. Does the postmortem fairly admit the early inefficiency of broad
   patch-and-run/full-stream debugging?
3. Does it explain why count-level LSI success was not enough for Section 5.7?
4. Does it correctly justify the AuthorOfficial comparator?
5. Does it separate generic RTDL core repairs from app-layer RayJoin logic?
6. Does it avoid overclaiming the bounded Section 5.7 result?

Requested verdict labels:

- `approve_rayjoin_correctness_root_cause_postmortem`
- `approve_with_required_amendments`
- `block_until_root_cause_or_boundaries_fixed`
