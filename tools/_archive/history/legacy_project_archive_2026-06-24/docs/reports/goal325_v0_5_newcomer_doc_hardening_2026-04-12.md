# Goal 325 Report: v0.5 Newcomer Doc Hardening

Date:
- `2026-04-12`

Goal:
- fix the concrete newcomer-facing documentation problems called out by the
  external aggressive-user Windows audit

Primary audit input:
- `docs/reports/v0_5_external_aggressive_user_audit_2026-04-12.md`

Files changed:
- `docs/README.md`
- `docs/quick_tutorial.md`
- `docs/release_facing_examples.md`
- `docs/rtdl/workload_cookbook.md`
- `docs/rtdl/programming_guide.md`
- `docs/tutorials/hello_world.md`
- `docs/tutorials/nearest_neighbor_workloads.md`
- `docs/tutorials/segment_polygon_workloads.md`
- `docs/tutorials/rendering_and_visual_demos.md`
- `docs/tutorials/sorting_demo.md`

What changed:
- `docs/README.md` was reduced from a mixed newcomer/archive index into a
  clearer live-doc entry point
- live runnable docs now restate Windows PowerShell command conventions instead
  of assuming Bash-style inline environment syntax
- `docs/rtdl/workload_cookbook.md` no longer tells users to run `cd rtdl` after
  they are already presumed to be at the repo root
- `docs/rtdl/programming_guide.md` now includes a concrete host-side runtime
  input-shape section with a minimal nearest-neighbor example

Why this matters:
- the Windows audit did not report fake code or broken first-run examples
- it reported doc/product friction that a literal outside reader could hit
- these fixes tighten the public technical-preview path without pretending the
  repo is now a frictionless beginner product

Verification:
- confirmed the targeted live docs now contain explicit PowerShell guidance
- confirmed the workload cookbook no longer contains literal `cd rtdl`
  newcomer footguns
- confirmed the newcomer doc index now separates live docs from historical
  material more clearly

Honesty boundary:
- this goal changes documentation only
- this does not change backend capability, correctness, or performance claims
- this does not upgrade `v0.5` from preview-ready to final-release-ready
