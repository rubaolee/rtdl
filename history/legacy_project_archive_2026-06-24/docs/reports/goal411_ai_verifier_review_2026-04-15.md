# Goal 411 AI Verifier Review — 2026-04-15

**Verdict: ACCEPTED**

---

## What I checked

- Goal definition: `docs/goal_411_public_surface_ci_automation.md`
- Implementation report: `docs/reports/goal411_public_surface_ci_automation_2026-04-15.md`
- Workflow: `.github/workflows/public-surface.yml`
- Harness: `scripts/goal410_tutorial_example_check.py`
- Guard test: `tests/goal411_public_surface_ci_automation_test.py`
- Hosted-run evidence: `docs/reports/goal411_github_actions_public_surface_report_2026-04-15.json`

---

## Hosted run evidence vs. Goal 411 report

The JSON artifact and the report are in exact agreement on every field:

| Field | JSON artifact | Report claim |
|---|---|---|
| machine | `github-actions-ubuntu` | `github-actions-ubuntu` |
| system | `Linux` | (ubuntu-latest, implied Linux) |
| python | `3.12.11` | — |
| passed | `24` | `24` |
| failed | `0` | `0` |
| skipped | `11` | `11` |
| total | `35` | — |
| cpu_python_reference | `true` | `True` |
| cpu | `true` | `True` |
| embree | `false` | `False` |
| optix | `false` | `False` |
| vulkan | `false` | `False` |

No discrepancy found. The numbers are also internally consistent: counting the 35 cases in `public_cases()` by which backends are unavailable on the runner (embree=False, optix=False, vulkan=False) yields exactly 11 skipped cases and 24 passing cases.

---

## Minimum automation target: cpu_python_reference and cpu

Both are enforced:

- `cpu_python_reference` appears in `public_cases()` with no `requires` constraint. It runs unconditionally on any platform. Six cases use this backend.
- `cpu` cases carry `requires=("cpu",)`. The hosted runner detected `cpu=True`, so all `_cpu` cases executed. Five `_cpu` cases are present.
- The harness exits with code `1` when any case fails (`return 1 if failed else 0`). A regression in either portable backend will fail the workflow job and block the branch.

The workflow triggers on `push` to `main` and all `codex/**` branches, and on every `pull_request`. This means the gate is active for all normal contribution paths.

---

## Optional backend handling: honesty check

The `should_skip` function gates execution on two independent conditions:

1. `linux_only=True` and `system != "Linux"` → skip with reason `linux_only`
2. Any entry in `requires` not present (or False) in `backend_status` → skip with reason `missing_<backend>`

On the hosted runner:
- Embree cases are skipped because `embree=False`. They are not marked `linux_only`, so they would run if Embree were installed — this is correct.
- OptiX and Vulkan cases are skipped because `optix=False` and `vulkan=False`. They are also marked `linux_only=True`, consistent with the goal definition's constraint that GPU backends remain Linux-maintainer-host-only until a stable automation environment is available.

No case pretends a backend is available when it is not. Skips are recorded with an explicit reason, not silently omitted.

---

## Guard test coverage

`tests/goal411_public_surface_ci_automation_test.py` enforces three structural invariants by loading the live harness module at test time:

1. **Portable minimum present** — asserts `hello_world`, `hello_world_cpu_python_reference`, `hello_world_cpu`, `graph_bfs_cpu_python_reference`, `graph_bfs_cpu`, `graph_triangle_cpu_python_reference`, and `graph_triangle_cpu` all appear in `public_cases()`.
2. **GPU cases are Linux-only** — asserts `linux_only=True` for all six OptiX and Vulkan cases.
3. **Portable minimum is not Linux-only** — asserts `linux_only=False` for every `_cpu_python_reference` and `_cpu` case.

These tests act as a structural lock: if a future edit removes a portable case or accidentally marks a portable backend as Linux-only, the guard test fails before the workflow even runs the harness.

---

## Continuous public first-run gate

The repo now has a real gate:

- Workflow file is present at `.github/workflows/public-surface.yml`.
- It installs the necessary system libraries (`libgeos-dev`, `pkg-config`) and Python requirements.
- It runs the shared harness with a stable machine label and writes a report artifact.
- A successful hosted run exists (run id `24455519225`, branch `main`, conclusion `success`, ~37 s).
- The harness is the single source of truth shared between Goal 410 manual validation and Goal 411 automation.

The portability boundary is correctly stated: `ubuntu-latest`, portable CPU backends only as the guaranteed minimum. Embree is opportunistic; GPU backends remain explicitly out of scope for hosted CI.

---

## Minor noted items (non-blocking)

- **Node 24 annotation** — GitHub Actions emitted a deprecation notice about the referenced action versions requiring Node 24-compatible updates. The run succeeded; this is routine maintenance debt and does not affect Goal 411 acceptance.
- **Embree on hosted runners** — The hosted runner does not have Embree, so three Embree cases are skipped every run. This is accurately described in the report. If Embree becomes available on a future runner, it would be picked up automatically with no harness changes needed.

---

## Summary

Goal 411 delivers exactly what the goal definition required:

- The Goal 410 command matrix is the single source of truth.
- A workflow file provides repository-hosted automation.
- The portable minimum (`cpu_python_reference`, `cpu`) is always exercised and any failure fails the job.
- Optional backend handling is honest: skips are real, not pretended successes.
- The hosted-run evidence is internally consistent and matches the report.
- A guard test structurally locks the minimum so it cannot be silently regressed.

**Goal 411 is accepted.**
