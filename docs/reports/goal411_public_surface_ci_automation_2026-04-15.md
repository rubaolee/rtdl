# Goal 411: Public Surface CI Automation

## Scope

This goal adds an honest repository-hosted automation layer for the public
first-run surface established by Goal 410.

The automated source of truth remains:

- [goal410_tutorial_example_check.py](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal410_tutorial_example_check.py)

## What was added

Workflow:

- [public-surface.yml](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/.github/workflows/public-surface.yml)

Guard test:

- [goal411_public_surface_ci_automation_test.py](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal411_public_surface_ci_automation_test.py)

## Automated coverage boundary

Repository-hosted automation now runs on:

- `ubuntu-latest`

The workflow installs:

- `libgeos-dev`
- `pkg-config`
- Python requirements from `requirements.txt`

Then it runs:

```bash
PYTHONPATH=src:. python scripts/goal410_tutorial_example_check.py \
  --machine github-actions-ubuntu \
  --output build/goal411/public_surface_ci_report.json
```

That means the automated gate always checks the portable public surface and
fails if any public first-run command regresses.

## Honest boundary

What this automation does cover:

- the Goal 410 public command matrix
- `cpu_python_reference`
- `cpu`
- any additional backends that happen to be available on the automation host

What it does not promise by itself:

- Embree on every hosted run
- OptiX on hosted CI
- Vulkan on hosted CI

Those remain environment-dependent and are still validated on the maintainer
machines.

## First verification evidence

Local proof of automation wiring:

- the new guard test locks the portable minimum and Linux-only GPU markings
- the public harness remains the shared source of truth between Goal 410 manual
  validation and Goal 411 automation

Hosted workflow evidence:

- once the workflow is pushed, the expected artifact is:
  - `build/goal411/public_surface_ci_report.json`
- if the hosted run is visible from the repo environment, it should be checked
  and recorded as the next update to this report

## Current status

Goal 411 is implementation-ready once the workflow is pushed.

If the hosted run succeeds, the repo will have a continuous public first-run
gate for the portable RTDL surface.
