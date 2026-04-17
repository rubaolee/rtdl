# Goal 411: Public Surface CI Automation

## Goal

Automate the public tutorial and release-facing example check so the current
first-run contract is continuously enforced.

## Required outcome

- the Goal 410 public command matrix remains the single source of truth
- there is an automated runner for the public surface check
- the automation is honest about platform/backend bounds
- the repo documents what is checked automatically and what remains
  maintainer-machine-only

## Minimum automation target

- repository-hosted automation must run the public surface harness for the
  portable baseline:
  - `cpu_python_reference`
  - `cpu`
- the automation must fail when a documented first-run command regresses

## Optional bounded extensions

- if an automation host has Embree, include Embree in the automated gate
- keep OptiX/Vulkan as explicitly Linux GPU-host-only until there is a stable
  automation environment that really supports them

## Deliverables

- CI/automation config
- any small harness adjustments needed for CI
- updated docs that describe the automated coverage boundary
- one report that records:
  - what is automated
  - what is still manual
  - what the first successful automation run covered
