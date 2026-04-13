# RTDL v0.5 Preview: Call For Test

Date: 2026-04-12
Status: open for external testing and criticism

## Why This Exists

RTDL `v0.5 preview` is at the point where outside testing is useful.

This is not a request for passive reading. It is a request to:

- run the current surfaces
- try the backends that are available on your machine
- look for correctness drift
- look for unclear documentation
- look for front-page confusion
- criticize unsupported or overclaimed areas
- suggest what should be improved before any stronger public release claim

The current preview state is:

- **preview-ready**
- **not final-release-ready**

Use this document as the practical guide for what to try and what kinds of
feedback are useful.

## What RTDL v0.5 Preview Adds

The `v0.5 preview` line is mainly the nearest-neighbor expansion line.

Current workload surface:

- `fixed_radius_neighbors` 2D
- `knn_rows` 2D
- `bounded_knn_rows` 2D
- `fixed_radius_neighbors` 3D
- `bounded_knn_rows` 3D
- `knn_rows` 3D

Current Linux backend surface for the 3D nearest-neighbor trio:

- Python reference
- native CPU / oracle
- Embree
- OptiX
- Vulkan
- PostGIS as external correctness/timing anchor

Current bounded non-Linux surface:

- Windows:
  - Embree correctness verified
  - no large-scale performance claim
- local macOS:
  - Embree correctness verified
  - no large-scale performance claim

## Backend Names In Plain English

- `cpu_python_reference`
  - pure Python truth path
  - slowest but easiest to trust and inspect
- `CPU/oracle`
  - RTDL's compiled C/C++ correctness baseline
- `Embree`
  - Intel CPU ray-tracing backend
- `OptiX`
  - NVIDIA GPU ray-tracing backend
- `Vulkan`
  - Vulkan ray-tracing GPU backend
- `PostGIS`
  - external database baseline, not an RTDL backend

## What Kinds Of Feedback Are Most Valuable

We want criticism on all of these:

- correctness
- backend consistency
- API clarity
- example quality
- installation friction
- terminology confusion
- support-matrix honesty
- performance interpretation
- missing docs
- bad docs
- suspicious claims
- weak or fake-feeling tests

## Ground Rules For Reviewers

Please do not assume:

- every backend is equally mature on every OS
- Linux performance claims automatically apply to Windows or macOS
- PostGIS is a production RTDL backend
- `preview-ready` means `final-release-ready`

Please do check whether the repo says those boundaries clearly enough.

## Recommended Reading Before Testing

Start here:

- [README.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/README.md)
- [support_matrix.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/release_reports/v0_5_preview/support_matrix.md)
- [goal320_v0_5_preview_readiness_audit_2026-04-12.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal320_v0_5_preview_readiness_audit_2026-04-12.md)
- [comprehensive_v0_5_transition_audit_report_2026-04-12.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/comprehensive_v0_5_transition_audit_report_2026-04-12.md)

If you want the current Linux backend picture:

- [goal317_v0_5_current_linux_4backend_nn_perf_report_2026-04-12.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal317_v0_5_current_linux_4backend_nn_perf_report_2026-04-12.md)

## Quick Start

Clone and install:

```bash
git clone https://github.com/rubaolee/rtdl.git
cd rtdl
python -m pip install -r requirements.txt
```

Linux/macOS shell:

```bash
PYTHONPATH=src:. python examples/rtdl_hello_world.py
```

Windows `cmd.exe`:

```bat
set PYTHONPATH=src;.
python examples\rtdl_hello_world.py
```

PowerShell:

```powershell
$env:PYTHONPATH="src;."
python examples/rtdl_hello_world.py
```

## Suggested Test Plan

### 1. Basic repo sanity

Try:

```bash
PYTHONPATH=src:. python examples/rtdl_hello_world.py
PYTHONPATH=src:. python examples/rtdl_hello_world_backends.py
```

Questions:

- Is initial setup reasonable?
- Is the first success path obvious?
- Is any backend naming confusing immediately?

### 2. Released nearest-neighbor surface

Try:

```bash
PYTHONPATH=src:. python examples/rtdl_fixed_radius_neighbors.py
PYTHONPATH=src:. python examples/rtdl_knn_rows.py
PYTHONPATH=src:. python examples/rtdl_service_coverage_gaps.py
PYTHONPATH=src:. python examples/rtdl_facility_knn_assignment.py
```

Questions:

- Do these examples make the public NN surface understandable?
- Do they feel like real workloads or toy demos only?
- Do backend switches work as expected on your machine?

### 3. Bounded 3D nearest-neighbor correctness

These are especially useful if you want to inspect the new `v0.5` line.

Embree 3D:

```bash
PYTHONPATH=src:. python -m unittest \
  tests.goal298_v0_5_embree_3d_fixed_radius_test \
  tests.goal299_v0_5_embree_3d_bounded_knn_test \
  tests.goal300_v0_5_embree_3d_knn_test
```

CPU/oracle 3D:

```bash
PYTHONPATH=src:. python -m unittest \
  tests.goal292_v0_5_native_3d_fixed_radius_oracle_test \
  tests.goal293_v0_5_native_3d_bounded_knn_oracle_test \
  tests.goal296_v0_5_native_3d_knn_oracle_test
```

Vulkan 3D, if available:

```bash
PYTHONPATH=src:. python -m unittest tests.goal315_v0_5_vulkan_3d_nn_test
```

OptiX 3D, if available:

```bash
PYTHONPATH=src:. python -m unittest tests.goal311_v0_5_optix_3d_nn_test
```

Questions:

- Do the results look parity-clean?
- Are any backend failures easy to understand?
- Are failure messages honest and actionable?

### 4. Broader regression confidence

Try:

```bash
PYTHONPATH=src:. python -m unittest tests.claude_v0_5_full_review_test
```

Questions:

- Does the repo feel stable?
- Does the broader regression surface support the claimed `v0.5 preview` state?

### 5. Linux backend/performance review

If you have a Linux host with the relevant backends available, use the current
reports as the benchmark reference rather than guessing expected results:

- [goal310_v0_5_linux_large_scale_embree_nn_perf_2026-04-12.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal310_v0_5_linux_large_scale_embree_nn_perf_2026-04-12.md)
- [goal312_v0_5_linux_large_scale_native_embree_optix_perf_2026-04-12.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal312_v0_5_linux_large_scale_native_embree_optix_perf_2026-04-12.md)
- [goal313_v0_5_linux_32768_backend_table_2026-04-12.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal313_v0_5_linux_32768_backend_table_2026-04-12.md)
- [goal316_v0_5_linux_large_scale_embree_optix_vulkan_perf_2026-04-12.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal316_v0_5_linux_large_scale_embree_optix_vulkan_perf_2026-04-12.md)
- [goal317_v0_5_current_linux_4backend_nn_perf_report_2026-04-12.md](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal317_v0_5_current_linux_4backend_nn_perf_report_2026-04-12.md)

Questions:

- Are the performance claims easy to follow?
- Are the backend boundaries stated clearly enough?
- Is there any sign of overclaiming Linux results as universal?

## Suggested Review Angles

### A. API angle

Please comment on:

- are the workload names understandable?
- is `bounded_knn_rows` intuitive or confusing?
- are 2D vs 3D surfaces explained well enough?
- do backend entry points feel coherent?

### B. Documentation angle

Please comment on:

- does the front page explain the project clearly?
- is `v0.4` versus `v0.5 preview` obvious?
- are backend names explained in plain language?
- are support limits obvious?
- are there docs that feel stale, duplicated, or contradictory?

### C. Correctness angle

Please comment on:

- whether the test surface looks strong enough for the claims made
- whether any backend appears under-tested
- whether any proof chain feels too indirect

### D. Performance angle

Please comment on:

- whether the Linux performance story is convincing
- whether the benchmarking language is honest
- whether comparisons against PostGIS are framed correctly
- whether Windows/macOS boundaries are clear enough

### E. Product/release angle

Please comment on:

- does `preview-ready` feel justified?
- what still blocks `final-release-ready`?
- what should be removed or toned down before broader public exposure?

## What We Especially Want People To Criticize

Please criticize any of these if they seem weak:

- front-page clarity
- backend terminology
- test adequacy
- support claims
- performance claims
- preview-vs-release wording
- Linux-vs-Windows/macOS wording
- external baseline wording

## Suggested Feedback Format

Please structure feedback like this when possible:

1. Environment
- OS
- Python version
- available backends

2. What you ran
- commands
- docs you used

3. Findings
- correctness issues
- doc issues
- UX/setup issues
- performance interpretation issues

4. Severity
- blocker
- important
- nice-to-have

5. Suggested fix
- concrete change if possible

## What Would Count As Especially Helpful External Review

Any of these would be high value:

- a strict code/test audit
- a docs/support-matrix honesty audit
- a Linux backend/performance review
- a Windows/macOS bounded Embree correctness review
- a front-page/new-user confusion review
- a “should this really be called preview-ready?” review

## Current Honest Bottom Line

RTDL `v0.5 preview` is ready to be tested seriously.

What is ready:

- real 3D nearest-neighbor surfaces
- real Linux backend closure
- real large-scale Linux performance evidence
- bounded Windows/macOS Embree correctness

What is not claimed:

- final `v0.5` release sign-off
- cross-platform performance parity
- universal backend maturity on every machine

That distinction is intentional. Please test the repo against that exact claim
surface.
