# Call For Review: Goal4790 Ray Hit And Grouped Continuation Tutorial Batch

Date: 2026-06-28

## Requested Verdict Labels

Please return exactly one verdict label:

- `approve_goal4790_ray_hit_and_grouped_continuation_tutorial_batch_complete`
- `approve_with_required_amendments`
- `block_goal4790_ray_hit_and_grouped_continuation_batch`

## Files To Review

Primary implementation:

- `examples/tutorial_programs/ray_triangle_hits.py`
- `examples/tutorial_programs/continuation_grouped_sum.py`

Tutorial pages:

- `tutorials/current/10_ray_triangle_hits.md`
- `tutorials/current/11_grouped_continuations.md`

Navigation and command surfaces:

- `tutorials/current/README.md`
- `examples/tutorial_programs/README.md`
- `examples/README.md`
- `docs/public_documentation_map.md`

Validation gate:

- `tests/v4_goal4640_public_docs_cleanup_test.py`

Engineering record:

- `docs/engineering/goal4790_ray_hit_and_grouped_continuation_tutorial_batch_2026-06-28.md`

## What Changed

Goal4790 extends the final tutorial ladder with:

- a real RTDL kernel for ray/triangle any-hit rows;
- a real RTDL kernel that emits ray hit-count rows;
- a grouped continuation over those rows;
- V4 runtime/operator mapping for `any_hit`, `grouped_sum`, and `grouped_i64`;
- public tutorial pages that teach kernel relation first and V4 surface second.

## Validation To Consider

Windows validation:

```text
py -3 examples\tutorial_programs\ray_triangle_hits.py --mode both
py -3 examples\tutorial_programs\continuation_grouped_sum.py --mode both
py -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Observed result:

```text
Ran 21 tests in 79.039s
OK
```

Linux clean-copy validation on `192.168.1.20`:

```text
cd /tmp/rtdl_goal4790_ray_cont
PYTHONPATH=src:. python3 examples/tutorial_programs/ray_triangle_hits.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/continuation_grouped_sum.py --mode both
PYTHONPATH=src:. python3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Observed result:

```text
Ran 21 tests in 29.775s
OK
```

## Required Review Questions

1. Does `ray_triangle_hits.py` teach the RTDL kernel relation before the V4 runtime surface?
2. Does `continuation_grouped_sum.py` teach continuation as a post-kernel reduction over relation rows?
3. Do both programs coherently support `--mode kernel`, `--mode visible`, `--mode v4`, and `--mode both`?
4. Do the tutorial pages avoid teaching a one-call black-box app API?
5. Is partner wording honest and explicit, without implying broad V4-over-V2/V3 speedup?
6. Are lessons 10 and 11 correctly linked into the public tutorial path?
7. Are the Windows and Linux validation results sufficient to move to the next tutorial batch?

## Non-Authorization

This review must not authorize:

- a new release claim;
- a new performance claim;
- a broad V4-over-V2/V3 speedup claim;
- Tier-3 arbitrary callback support;
- raw OptiX callback support;
- C ABI, embedding, or non-Python host claims;
- full paper-reproduction support;
- any app-specific native-kernel exception.
