# Goal3794 Quick Tutorial HIPRT Autodiscovery Note

Status: implemented locally.

## Purpose

Goal3794 updates the current learner quick tutorial so its optional HIPRT build
snippet matches the current Makefile and Goal3785 runner behavior.

## Change

`docs/quick_tutorial.md` now shows:

- `make build-hiprt` as the first command, because common HIPRT SDK locations
  are auto-discovered;
- `make build-hiprt HIPRT_PREFIX=/path/to/hiprtSdk` as the explicit override
  when a pod uses a non-standard SDK layout;
- the boundary that HIPRT/Orochi on NVIDIA is not AMD GPU validation.

## Boundary

Goal3794 is a documentation consistency update. It does not authorize AMD
performance claims, public speedup wording, whole-app acceleration wording,
broad RT-core wording, paper-reproduction claims, release claims, zero-copy
claims, or app-specific native-engine logic.

## Validation

Focused validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3794_quick_tutorial_hiprt_autodiscovery_note_test
```
