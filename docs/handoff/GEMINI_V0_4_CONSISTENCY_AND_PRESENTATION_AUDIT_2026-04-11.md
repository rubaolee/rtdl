Please perform a final consistency-and-presentation audit of the clean RTDL
`v0.4` release-prep branch at:

- `[REPO_ROOT]`

This review must follow this exact priority order:

1. front page
2. tutorials
3. docs
4. examples
5. code-facing surface
6. tests/reports/history

Your job is to judge whether the project feels:

- easy for new users
- professional
- attractive
- coherent

And whether it avoids:

- bad links
- bad expressions
- duplicated explanations
- unexplained acronyms
- maintainer-local leakage
- ugly or contradictory release wording

Important review rule:

- If the same problem appears in multiple places, weight it by the highest user
  visibility where it appears first.
- The front page and tutorials matter more than historical reports.

Start from these surfaces in order:

### Front page

- `[REPO_ROOT]/README.md`
- `[REPO_ROOT]/docs/README.md`

### Tutorials

- `[REPO_ROOT]/docs/quick_tutorial.md`
- `[REPO_ROOT]/docs/tutorials/README.md`
- `[REPO_ROOT]/docs/tutorials/hello_world.md`
- `[REPO_ROOT]/docs/tutorials/sorting_demo.md`
- `[REPO_ROOT]/docs/tutorials/segment_polygon_workloads.md`
- `[REPO_ROOT]/docs/tutorials/nearest_neighbor_workloads.md`
- `[REPO_ROOT]/docs/tutorials/rendering_and_visual_demos.md`

### Docs

- `[REPO_ROOT]/docs/features/README.md`
- `[REPO_ROOT]/docs/release_facing_examples.md`
- `[REPO_ROOT]/docs/v0_4_application_examples.md`
- `[REPO_ROOT]/docs/rtdl/programming_guide.md`
- `[REPO_ROOT]/docs/rtdl/dsl_reference.md`
- `[REPO_ROOT]/docs/rtdl/workload_cookbook.md`
- `[REPO_ROOT]/docs/workloads_and_research_foundations.md`
- `[REPO_ROOT]/docs/release_reports/v0_4/`

### Examples

- `[REPO_ROOT]/examples/README.md`
- `[REPO_ROOT]/examples/`

### Code-facing surface

- `[REPO_ROOT]/src/rtdsl/reference.py`
- `[REPO_ROOT]/src/rtdsl/runtime.py`
- `[REPO_ROOT]/src/rtdsl/baseline_runner.py`

### Lower-priority historical/report layer

- `[REPO_ROOT]/docs/reports/`

Write the review to:

- `[REPO_ROOT]/docs/reports/gemini_v0_4_consistency_and_presentation_audit_2026-04-11.md`

Use these sections only:

- Verdict
- Front Page
- Tutorials
- Docs
- Examples
- Code-Facing Surface
- Lower-Priority Issues
- Release Recommendation

If there are no blocking findings, say so explicitly.
