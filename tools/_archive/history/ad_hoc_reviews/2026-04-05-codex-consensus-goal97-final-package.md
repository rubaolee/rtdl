# Codex Consensus: Goal 97 Final Package

Date: 2026-04-05
Status: APPROVED FOR PUBLISH

## Reviewers

- Codex:
  - `/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-05-codex-review-goal97-final-package.md`
  - verdict: `APPROVE`
- Gemini:
  - `/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-05-gemini-review-goal97-final-package.md`
  - verdict: `APPROVE`

## Consensus

Goal 97 is approved for publication as a correctness/demo RTDL goal.

Accepted claim surface:

- non-join RTDL program
- nonnegative integers only
- duplicates allowed with stable `original_index` tie-break
- sorting reconstructed from geometric hit counts
- Linux small-case parity verified across:
  - `cpu_python_reference`
  - `cpu`
  - `embree`
  - `vulkan`
  - `optix`

Non-claims:

- not a performance benchmark
- not a negative-integer package
- not a full large-scale backend performance study

## Notes

Goal 97 also exposed and repaired a real OptiX `lsi` backend issue in:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_optix.cpp`

That repair is considered part of the accepted package because it was required
to make the Goal 97 OptiX backend path actually runnable on the validated Linux
host.
