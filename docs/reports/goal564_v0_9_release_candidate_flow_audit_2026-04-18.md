# Goal 564: v0.9 Release-Candidate Flow Audit

Date: 2026-04-18

Repository: `/Users/rl2025/rtdl_python_only`

## Verdict

ACCEPT as a v0.9 release-candidate flow audit.

The v0.9 HIPRT line has a coherent evidence chain from feasibility, planning,
implementation, matrix completion, performance comparison, public docs refresh,
pre-release tests, and documentation audit. No release-blocking code, test,
documentation, or flow defect is known at this audit point.

This report does not authorize or perform the final `v0.9.0` release action.
It says the release candidate is ready for final user decision after external
review of this audit.

## Flow Summary

The v0.9 line delivered the requested HIPRT goal:

- HIPRT SDK/CUDA-path feasibility was studied and reviewed.
- HIPRT was implemented as a real backend path, not a hidden CPU fallback.
- `run_hiprt` now covers the 18-workload matrix:
  - geometry
  - 2D geometry
  - nearest-neighbor
  - graph
  - bounded DB-style analytics
- Linux HIPRT correctness matrix is complete:
  - `pass=18`
  - `not_implemented=0`
  - `hiprt_unavailable=0`
  - `fail=0`
- Linux cross-backend parity/performance smoke matrix is complete:
  - 18 workloads x 4 backends = 72 checks
  - backends: HIPRT, Embree, OptiX, Vulkan
  - `pass=72`
  - `backend_unavailable=0`
  - `fail=0`
- Local and Linux full unittest discovery both pass:
  - local macOS-side: `232 tests`, `OK`
  - Linux backend host: `232 tests`, `OK`
- Public docs now describe the state as an active `v0.9` candidate, not as a
  stale one-workload HIPRT preview.

## Goal And Review Ledger

The following goals have reports and external-style ACCEPT reviews:

| Goal | Role | Review status |
| --- | --- | --- |
| 537 | HIPRT CUDA feasibility | Claude + Gemini reviews accepted |
| 538 | OptiX after CUDA 12.2 validation | Claude + Gemini reviews accepted |
| 539 | all-workload OptiX CUDA 12.2 correctness | Claude + Gemini reviews accepted |
| 540 | HIPRT probe/backend bring-up | Claude + Gemini reviews accepted |
| 541 | HIPRT 3D ray/triangle hit-count | Claude + Gemini reviews accepted |
| 542 | prepared HIPRT 3D ray/triangle path | Claude + Gemini reviews accepted |
| 543 | `run_hiprt` dispatch surface | Claude + Gemini reviews accepted |
| 544 | initial HIPRT public docs/example | Claude + Gemini reviews accepted |
| 545 | v0.9 HIPRT plan and requirements matrix | Claude + Gemini reviews accepted |
| 546 | API parity skeleton | external review accepted |
| 547 | correctness matrix harness | external review accepted |
| 548 | HIPRT fixed-radius 3D | external review accepted |
| 549 | HIPRT 3D KNN | external review accepted |
| 550 | HIPRT 2D geometry plan + segment intersection | external reviews accepted |
| 551 | HIPRT 2D ray/triangle | external review accepted |
| 552 | HIPRT point-in-polygon | external review accepted |
| 553 | HIPRT point-nearest-segment | external review accepted |
| 554 | HIPRT segment/polygon workloads | external review accepted |
| 555 | HIPRT 2D neighbors | external review accepted |
| 556 | HIPRT overlay | external review accepted |
| 557 | HIPRT BFS discover | external review accepted |
| 558 | HIPRT triangle match | external review accepted |
| 559 | HIPRT DB workloads | external review accepted |
| 560 | HIPRT backend performance comparison | external review accepted |
| 561 | public docs refresh | Claude + Gemini reviews accepted |
| 562 | pre-release test gate | external review accepted |
| 563 | documentation audit | external review accepted |

Machine check used for this ledger:

```text
Goals 540-563: missing_or_unclear []
```

## Release-Critical Evidence

Primary v0.9 candidate docs:

- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_reports/v0_9/support_matrix.md`

Final test gate:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal562_v0_9_pre_release_test_gate_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal562_external_review_2026-04-18.md`

Final doc gate:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal563_v0_9_documentation_audit_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal563_external_review_2026-04-18.md`

Final matrix artifacts:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal562_hiprt_correctness_matrix_linux_2026-04-18.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal562_hiprt_backend_perf_compare_linux_2026-04-18.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal560_hiprt_backend_perf_compare_2026-04-18.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal560_external_review_2026-04-18.md`

Public docs checked:

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/docs/capability_boundaries.md`
- `/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/README.md`
- `/Users/rl2025/rtdl_python_only/examples/README.md`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_hiprt_ray_triangle_hitcount.py`

## Known Boundaries

These are not blockers because they are explicitly documented:

- `v0.9.0` is not released until the user authorizes the release action.
- HIPRT validation is Linux NVIDIA/CUDA/Orochi, not AMD GPU validation.
- The tested NVIDIA GTX 1070 has no RT cores, so no RT-core speedup claim is
  allowed from this evidence.
- HIPRT performance is not currently leading on the one-repeat small-fixture
  comparison because per-call setup/JIT/module overhead dominates.
- `prepare_hiprt` is currently narrower than `run_hiprt`; prepared context
  reuse is implemented for 3D ray/triangle hit-count, not the full 18-workload
  matrix.
- The current performance comparison is a smoke comparison, not a production
  throughput benchmark.

## Code/Test/Doc/Flow Answers

Known code errors: none release-blocking after the current test gate. The full
test suite passes locally and on Linux, and HIPRT-specific matrix checks pass.

Known documentation errors: none release-blocking after Goal 563. Stale HIPRT
preview wording was found and fixed; public links in the audited set are valid.

Known flow errors: none release-blocking. Every v0.9 goal from implementation
through pre-release gates has external-style review. Major planning/docs gates
have Claude/Gemini coverage. Final release action remains intentionally
separate from this audit.

## Release Decision

The v0.9 candidate is ready for final external review of this flow audit and
then user-controlled release authorization.

Do not tag or publish `v0.9.0` from this report alone. The next step is an
explicit user release decision after reviewing this final audit and its
external review responses.
