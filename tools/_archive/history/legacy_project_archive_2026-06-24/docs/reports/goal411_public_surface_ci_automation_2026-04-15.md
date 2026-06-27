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
- `PYTHONPATH=src:. python3 -m unittest tests.goal411_public_surface_ci_automation_test`
  passed locally
- the public harness remains the shared source of truth between Goal 410 manual
  validation and Goal 411 automation

Hosted workflow evidence:

- workflow:
  - `Public Surface`
- workflow file:
  - [public-surface.yml](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/.github/workflows/public-surface.yml)
- successful hosted run:
  - run id `24455519225`
  - branch `main`
  - conclusion `success`
  - job duration about `37s`
- uploaded artifact copied into the repo:
  - [goal411_github_actions_public_surface_report_2026-04-15.json](/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal411_github_actions_public_surface_report_2026-04-15.json)

Hosted report summary:

- machine label: `github-actions-ubuntu`
- result:
  - `24` passed
  - `0` failed
  - `11` skipped
- backend availability:
  - `cpu_python_reference = True`
  - `cpu = True`
  - `embree = False`
  - `optix = False`
  - `vulkan = False`

Skip story on the hosted runner:

- Embree cases skipped because Embree is not installed on the hosted runner
- OptiX and Vulkan cases skipped because the hosted runner is not the Linux GPU
  maintainer host

Non-blocking hosted-run note:

- GitHub Actions emitted a platform annotation that the currently referenced
  official actions will eventually need Node 24-compatible versions
- the run still succeeded, so this is maintenance debt, not a Goal 411 blocker

## Current status

Goal 411 is accepted as the first honest repository-hosted automation gate for
the public RTDL surface.

The repo now has a continuous public first-run gate for:

- `cpu_python_reference`
- `cpu`

with optional accelerated backends recorded when available rather than
pretended.
