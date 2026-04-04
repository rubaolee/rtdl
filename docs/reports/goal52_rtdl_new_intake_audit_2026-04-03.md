# Goal 52 Intake Audit For `rtdl-new`

## Question

Should the recent external `rtdl-new` work be merged into the main RTDL repository?

## Short Answer

Yes, partially.

- the code changes are small, coherent, and useful
- the review and consensus docs are not reliable enough to import as authoritative project records without revision

So the right action is:

- keep the code
- reject or revise the external consensus narrative

## What Was Reviewed

Repository under review:

- `/Users/rl2025/claude-work/rtdl-new`

Reviewed code:

- `src/rtdsl/api.py`
- `src/rtdsl/__init__.py`
- `tests/_embree_support.py`
- `tests/test_core_quality.py`
- `scripts/run_full_verification.py`

Reviewed docs:

- `docs/test_quality_report.md`
- `docs/gemini_report_review.md`
- `docs/cross_review_response_to_gemini_final.md`
- `docs/consensus_rounds/*.md`

## Verified Facts

### Code changes are real

The external repo contains these actual code additions:

- `rt.contains()` alias in `src/rtdsl/api.py`
- `contains` export in `src/rtdsl/__init__.py`
- `sys.path` injection fix in `tests/_embree_support.py`
- new `tests/test_core_quality.py`

### The new quality suite is real

I ran:

- `PYTHONPATH=src:. python3 -m unittest tests.test_core_quality`

Result:

- `90` tests
- `OK`

### Full test discovery passes

I ran:

- `PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'`

Result:

- `165` tests
- `2` skips
- `OK`

### `run_full_verification.py` is better than the docs claim

The external consensus docs claim the verification script still uses empty-input correctness-smoke calls and therefore has no real assertion value.

That is no longer accurate for the current code.

The current `scripts/run_full_verification.py` does run:

- CLI smoke checks
- artifact generation
- `compare_goal15(...)`
- Embree parity smoke

So the documentation is stale relative to the actual file.

## Main Problem

The external code is in better shape than the external consensus docs.

Concretely:

- the docs repeatedly claim a `255`-test baseline
- the actual current external repo passes `165` tests with `2` skips
- the docs still describe `scripts/run_full_verification.py` as if it had an older, weaker implementation

That means the cross-AI review materials are not trustworthy as a final authority without revision.

## Keep / Reject Recommendation

### Keep

- `src/rtdsl/api.py` alias addition
- `src/rtdsl/__init__.py` export
- `tests/_embree_support.py` loader fix
- `tests/test_core_quality.py`

### Keep Provisionally

- current `scripts/run_full_verification.py`
  - not because it changed in this patchset relative to main
  - but because the external docs no longer describe it correctly

### Reject As Authoritative Without Revision

- `docs/consensus_rounds/CONSENSUS_FINAL.md`
- `docs/consensus_rounds/round_3_claude.md`
- `docs/consensus_rounds/round_3_gemini.md`
- and any other external doc that still claims:
  - `255` passing tests
  - or the stale `run_full_verification.py` critique

## Additional Recommended Fix Before Merge

If we intake the code, add one direct test for the new alias:

- assert that `rt.contains(...)` produces the same predicate object shape as `rt.point_in_polygon(...)`

The alias is trivial, so this is low risk, but it should be directly covered if we accept it.

## Recommended Goal 52 Merge Policy

1. get Gemini and Claude review on this intake audit
2. if consensus agrees:
   - merge code only
   - do not import the stale consensus docs as accepted project history
3. add a direct alias test in the main repo
4. run tests in the main repo
5. write a final result report stating exactly what was merged and what was rejected
