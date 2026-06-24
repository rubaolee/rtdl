# Phoenix V3 M27 - LibRTS AABB Set-B Triage And Cold OptiX Retain Fix

Date: 2026-06-23

Status: **fix candidate with stability boundary; not release authorization**

M27 follows the M26 2-AI consensus:

1. First triage the Embree 32768 stress regression revealed by M25.
2. Then attempt a bounded repair for the strict cold single-shot OptiX row (`0.922x` vs the `0.950x` watch threshold).
3. Do not run all-app.

## Decision Audit

1. Was the M27 order foolish?
   No. M26/Claude required the Embree 32768 triage before further OptiX repair.

2. If yes, what actions made it foolish?
   Not applicable. The foolish action would have been to skip the new Embree issue and claim the OptiX fix alone closed the Set-B control surface.

3. Was there another path?
   Yes. We could have gone straight to Set-A runtime trunk work. That remains the major V3 path, but Set-B regressions must be understood first.

4. Can we try a different path that solves the real problem?
   Yes. M27 uses focused triage and a bounded, runner-generic single-repeat output fix, then stops short of all-app/release claims.

## Code Change

File:

```text
examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py
```

Change:

- For OptiX prepared-query-set AABB count, `query_repeat == 1` now calls the productized runner with `retain_repeat_outputs=False`.
- `query_repeat > 1` keeps `retain_repeat_outputs=True`.
- The app accepts both single dict output and tuple retained outputs.

Why:

- `retain_repeat_outputs=True` forces the runner down the repeated-output retention path even for strict single-shot rows.
- M27 direct probe shows this adds measurable cold single-shot overhead.
- This does not change the native engine, backend, fixture, operation, counts, or productized runner path.

Test:

```text
tests/v3_phoenix_librts_aabb_count_runner_test.py
```

New guard:

- `query_repeat=1` must pass `retain_repeat_outputs=False`.
- `query_repeat=3` still retains repeated outputs.
- Payload still records `prepared_execution_session_runner_used=True` and `productized_execution_path=prepared_execution_session_runner`.

## Tests

Local:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_librts_aabb_count_runner_test \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_aabb_prepared_query_cache_test

43 tests OK
```

POD:

```text
PYTHONPATH=src:. /root/rtdl_v3_rebuild_20260620/.venv/bin/python -m unittest \
  tests.v3_phoenix_librts_aabb_count_runner_test \
  tests.v3_phoenix_prepared_execution_session_runner_test \
  tests.v3_phoenix_aabb_prepared_query_cache_test

43 tests OK
```

Note: local `py_compile` hit a Windows pycache permission error after the tests had already imported the edited modules. This was not a syntax failure.

## POD Evidence

POD:

```text
root@213.173.108.14 -p 11592
GPU: NVIDIA RTX 4000 Ada Generation
Driver: 550.127.05
```

Artifacts:

```text
docs/rebuild/v3/evidence/phoenix_v3_m27_librts_embree_stress_triage_20260623_130838
docs/rebuild/v3/evidence/phoenix_v3_m27_optix_cold_retain_probe_20260623_131411
docs/rebuild/v3/evidence/phoenix_v3_m27_librts_optix_cold_retain_fix_ab_20260623_131633
docs/rebuild/v3/evidence/phoenix_v3_m27_librts_optix_cold_retain_fix_ab_extra_20260623_131735
```

No stderr output was produced by the focused benchmark runs.

## Embree 32768 Stress Triage

Scenario:

```text
backend=embree
boxes=32768
queries=1024 point + 1024 box
repeat=20
warmup=5
skip CPU oracle=true
```

Results:

| sample | V2.14 sec | current sec | current/V2.14 |
| ---: | ---: | ---: | ---: |
| 1 | 0.912685543 | 0.806993507 | 1.131x |
| 2 | 0.895104237 | 0.996299259 | 0.898x |
| 3 | 0.908242274 | 0.997105952 | 0.911x |

Aggregate:

```text
geomean current/V2.14: 0.975x
min current/V2.14: 0.898x
max current/V2.14: 1.131x
```

Interpretation:

- This is not a clean deterministic regression: the geomean is above `0.950x`.
- It is also not cleanly closed: 2 of 3 samples are below `0.950x`, and current shows larger run-to-run variance.
- M27 records this as an **Embree 32768 stability watch blocker**, not as a deterministic mean/geomean failure.

## OptiX Cold Retain Probe

Direct current-runner probe, same fixture:

```text
backend=optix
boxes=2048
queries=1024 point + 1024 box
repeat=1
warmup=0
operation=all
```

| retain_repeat_outputs | sample query sec | median query sec | average query sec |
| --- | --- | ---: | ---: |
| true | 0.334329709, 0.277623340, 0.312370911 | 0.312370911 | 0.308107987 |
| false | 0.263605766, 0.251968309, 0.279371940 | 0.263605766 | 0.264982005 |

Interpretation:

- Avoiding retained tuple output for a single measured run is a real cold-path improvement.
- The median direct runner query time improves by about `1.185x` (`0.312370911 / 0.263605766`).
- This is a generic runner-output-path change, not a native app-specific shortcut.

## Patched Strict Cold OptiX A/B

Scenario:

```text
backend=optix
boxes=2048
queries=1024 point + 1024 box
repeat=1
warmup=0
operation=all
```

Results after patch:

| sample | V2.14 sec | current sec | current/V2.14 | pass `>=0.950x` |
| ---: | ---: | ---: | ---: | --- |
| 1 | 0.287921481 | 0.541959584 | 0.531x | no |
| 2 | 0.323190220 | 0.262608394 | 1.231x | yes |
| 3 | 0.318295859 | 0.271197304 | 1.174x | yes |
| 4 | 0.301309660 | 0.297451943 | 1.013x | yes |
| 5 | 0.253155112 | 0.286616348 | 0.883x | no |
| 6 | 0.257144421 | 0.263328463 | 0.977x | yes |
| 7 | 0.300088473 | 0.278677516 | 1.077x | yes |
| 8 | 0.270549342 | 0.243741795 | 1.110x | yes |

Aggregate:

```text
geomean current/V2.14: 0.973x
median sample ratio: 1.045x
pass count >=0.950x: 6/8
min current/V2.14: 0.531x
max current/V2.14: 1.231x
```

Interpretation:

- The patch improves the typical cold single-shot path enough to cross the `0.950x` threshold by geomean and median sample ratio.
- It does not eliminate cold-process outliers. One sample is severely below threshold (`0.531x`), and one additional sample is below threshold (`0.883x`).
- Therefore M27 should be treated as an **OptiX cold fix candidate with stability boundary**, not an unconditional watch-row closure.

## Current Status

Codex recommendation before external review:

```text
retain fix: keep
OptiX cold row: improved, not unconditionally closed
Embree stress row: stability watch blocker
release/all-app/public speedup: not authorized
```

## Recommended Next Step

Ask Claude to review:

1. Whether the single-repeat retain fix is technically sound and should stay.
2. Whether the OptiX strict cold row can be accepted with a stability boundary, or remains `partial_not_closed`.
3. Whether the Embree 32768 row should block release as stability-watch, deterministic blocker, or explanation-only.
4. Whether M28 should proceed to true Set-A runtime trunk work or spend more focused time on cold/stability controls.

## Non-Authorization

This packet does not authorize:

- V3 release.
- Full all-app rerun.
- Public speedup wording.
- Broad "V3 is faster than V2.x" wording.
- Hiding the OptiX outliers.
- Hiding the Embree variance.
- Counting LibRTS AABB single-shot as Set A.
- V4/external zero-copy/embedding claims.
