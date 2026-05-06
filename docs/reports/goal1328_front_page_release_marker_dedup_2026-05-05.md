# Goal1328: Front Page Release Marker Dedup

Date: 2026-05-05

## Scope

Remove the duplicated root README release marker while preserving the v1.0
public release boundary.

## Change

The root README now states the current release once:

```text
The current released version is `v1.0`.
```

The older bullet-form duplicate was removed from the root README only. Release
packages and historical reports remain unchanged.

## Boundary

This is public front-page polish only. It does not authorize public v1.5
release wording, public NVIDIA speedup wording, or any whole-app speedup claim.

## Validation

Targeted local gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1221_v0_9_8_release_action_test \
  tests.goal646_public_front_page_doc_consistency_test

Ran 7 tests in 0.006s
OK
```
