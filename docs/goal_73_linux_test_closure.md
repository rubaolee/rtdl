# Goal 73: Linux Test Closure

Priority:
- after Goals 71 and 72
- before the final multi-AI audit

Problem:
- the next stabilization step after the prepared-county performance goals is a
  thorough Linux validation run
- the validation must be performed on a clean Linux clone, not a drifted local
  workspace

Goal:
- run the full Linux test matrix on a clean clone of the published repo
- rerun the targeted GPU-sensitive tests
- rerun Goal 51 Vulkan validation
- repair any Linux-specific regressions found on that path
- publish the final Linux test closure package only after 2-AI review

Acceptance:
- clean Linux clone at the current published commit
- full matrix passes
- targeted GPU slice passes
- Goal 51 Vulkan validation passes
- any Linux-specific repair patches are documented
