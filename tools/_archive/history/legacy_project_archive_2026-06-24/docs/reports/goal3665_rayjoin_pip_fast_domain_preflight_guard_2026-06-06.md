# Goal3665 RayJoin PIP Fast-Domain Preflight Guard

Date: 2026-06-06

Status: internal v2.9 correctness-boundary hardening; not performance evidence
and not release authorization.

## Purpose

Goal3663 confirmed strong RTDL/OptiX batched repeated-request PIP throughput
on two validated public-CDB county slices. A larger `count16545` probe then
hit the older Goal3320 correctness boundary: the generic device-filtered
closed-shape fast route counted `47264` positives while exact prepared
semantics counted `47262`.

Goal3665 hardens the benchmark runner around that boundary:

- `preflight_rayjoin_pip_fast_count_domain(...)` now accepts
  `device_predicate_eps`, so the preflight uses the same tuned generic route
  settings as the measured path.
- `scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py` adds
  `--rtdl-pip-require-validated-fast-domain`.
- When the flag is supplied, the runner performs the app-level exact-vs-fast
  PIP preflight before RayJoin timing and fails closed if the selected fast
  route is not exact for that input domain.

This is app-level benchmark policy over generic point/closed-shape primitives.
It does not add RayJoin-specific native-engine logic.

## Evidence

Local focused tests:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3321_rayjoin_pip_validated_domain_preflight_test tests.goal3244_rayjoin_same_slice_repeated_count_runner_test
```

Result: 34 tests OK.

Pod smoke summary:

- `docs/reports/goal3665_rayjoin_pip_fast_domain_preflight_guard_a5000/summary.json`

The pod smoke used an RTX A5000 checkout with the Python app/runner/test patch
copied into place. It is intentionally recorded as functionality smoke, not
clean-source performance evidence.

## Pod Smoke Results

| Probe | Dataset | Exact count | Fast count | Result |
| --- | --- | ---: | ---: | --- |
| validated slice pass | `br_county_start256_count512.cdb` | 1417 | 1417 | preflight allowed, timing proceeded |
| full-county fail closed | `br_county_start0_count16545.cdb` | 47262 | 47264 | preflight rejected before RayJoin timing |

The failing probe printed:

```text
validated-domain preflight rejected fast PIP count route: 47264 != 47262
```

and the captured run confirmed:

```text
fail_probe_rayjoin_started no
```

## Interpretation

This closes a practical safety hole in the benchmark workflow. Without the new
guard, a large invalid domain can spend time running RayJoin before the RTDL
validated fast route fails during its own measurement. With the guard, the
runner refuses that route before RayJoin timing begins.

The larger conclusion is unchanged:

- validated slices can use the fast generic batch executor;
- full county-style topology still needs a richer generic topology-aware
  closed-shape membership contract or a fallback/correction route;
- the current engine remains app-agnostic because the native side still sees
  generic point/closed-shape count primitives.

## Boundary

Goal3665 does not authorize:

- public v2.9 release wording;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app RayJoin speedup wording;
- RayJoin paper reproduction wording;
- RTDL-beats-RayJoin wording;
- true zero-copy wording;
- automatic partner/backend selection;
- app-specific native-engine logic.

