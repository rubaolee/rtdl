# Antigravity External Review Intake

Date: 2026-04-07
Source artifact:

- [2026-04-07-antigravity-review-rtdl-test-report.md](/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-07-antigravity-review-rtdl-test-report.md)

## Verdict

The Antigravity report is useful as a supplementary external test artifact, but
it should not replace the current canonical v0.2 release-shaping story.

## What Is Usable

- it provides an additional outside test pass over CPU/Embree/PostGIS-oriented
  surfaces
- it independently exercised Linux and local Mac environments
- it reports clean parity on the surfaces it actually tested
- it identified and fixed one benchmark-path issue during its own run

## What Is Too Broad Or Repo-Inaccurate

- it uses a non-canonical Linux tree:
  - `~/rtdl_test_work/rtdl`
  instead of the accepted current primary repo path or a clean-clone release
  check
- it centers:
  - `make verify`
  - `make eval-rtdsl-embree`
  which are broader legacy whole-repo gates, not the current canonical frozen
  v0.2 release gates
- it excludes live OptiX and Vulkan runs in a way that does not match the
  accepted current v0.2 segment/polygon and Jaccard release story
- its concluding sentence is too strong for current repo policy:
  - current v0.2 is in release-shaping mode
  - not in resumed feature-growth / GPU-integration mode

## Accepted Interpretation

Use the Antigravity result as:

- supplementary external evidence for CPU/Embree/PostGIS-oriented validation
- another signal that the repo remains stable on tested bounded surfaces

Do not use it as:

- the canonical definition of the v0.2 release surface
- a reason to reopen feature growth
- a reason to overclaim native GPU maturity for the Jaccard line
