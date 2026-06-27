# Goal 526 External Review

Date: 2026-04-18
Reviewer: Claude (Sonnet 4.6)
Verdict: **ACCEPT**

## What Was Checked

- `docs/release_facing_examples.md` — stale phrase removal and Goal509 scope wording
- `docs/rtdl_feature_guide.md` — v0.8 app-building capability bullet completeness
- `tests/goal526_v0_8_public_doc_stale_phrase_test.py` — guard test coverage

## Findings

### release_facing_examples.md

The phrase `the other two v0.8 apps` is absent. Goal509 is now scoped
explicitly:

> "Goal509 covers the robot collision screening and Barnes-Hut apps."

That sentence also correctly summarizes what Goal509 accepted and rejected
(CPU/Embree/OptiX for robot collision; robot Vulkan rejected for parity
failure; CPU/Embree/OptiX/Vulkan for Barnes-Hut candidate generation with
Python force reduction kept separate). No overclaiming introduced.

### rtdl_feature_guide.md

The "What RTDL Can Currently Do" bullet now names all six accepted v0.8
app-building examples:

- Hausdorff distance
- ANN candidate search
- outlier detection
- DBSCAN clustering
- robot collision screening
- Barnes-Hut force approximation

The bullet correctly cites Goal507, Goal509, and Goal524 as the app-specific
backend/performance boundary reports. The adjacent performance note section
accurately reproduces the per-app boundaries (robot Vulkan rejected, Barnes-Hut
Python-owns-force-reduction, ANN/outlier/DBSCAN no external-baseline speedup
claim). No overclaiming introduced.

### Guard Test

`goal526_v0_8_public_doc_stale_phrase_test.py` covers:

- absence of `the other two v0.8 apps` in release examples
- presence of the scoped Goal509 sentence
- all six app names present in the feature guide (including the
  newline-split `"ANN\n  candidate search"` which matches the actual
  multi-line bullet in the guide)
- presence of `Goal507, Goal509, and Goal524 reports` in the feature guide

The newline-split in the ANN subTest is intentional and matches the actual
document text (`ANN\n  candidate search` in the feature guide bullet list).
The test is correct as written.

Report states 6 tests ran OK across goal526, goal525, and goal511 suites.
That is consistent with the single new test class (one test method with six
subtests collapsed into one test count, plus the pre-existing tests).

## Summary

Both doc changes are accurate, complete, and bounded. The stale phrase is
gone. Goal509 scope is correctly narrowed to robot collision screening and
Barnes-Hut. The feature guide now names all six apps without introducing
any external-baseline speedup claim. The guard test enforces all of this.
No overclaiming found anywhere in the changeset.
