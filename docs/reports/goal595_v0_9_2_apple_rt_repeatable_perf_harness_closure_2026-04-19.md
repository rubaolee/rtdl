# Goal595: v0.9.2 Apple RT Repeatable Performance Harness Closure

Date: 2026-04-19

Status: ACCEPT

## Scope

Goal595 implements the required v0.9.2 baseline harness before Apple RT
optimization work. It measures current Apple Metal/MPS RT against Embree on the
local Apple M4 host, checks parity against CPU reference, records cold-call and
warm measured samples, and reports variance using coefficient of variation.

## Artifacts

```text
/Users/rl2025/rtdl_python_only/scripts/goal595_apple_rt_perf_harness.py
/Users/rl2025/rtdl_python_only/tests/goal595_apple_rt_perf_harness_test.py
/Users/rl2025/rtdl_python_only/docs/reports/goal595_apple_rt_repeatable_perf_macos_2026-04-19.json
/Users/rl2025/rtdl_python_only/docs/reports/goal595_apple_rt_repeatable_perf_macos_2026-04-19.md
```

Review trail:

```text
/Users/rl2025/rtdl_python_only/docs/handoff/GOAL595_SINGLE_SENTENCE_EXTERNAL_REVIEW_REQUEST_2026-04-19.md
/Users/rl2025/rtdl_python_only/docs/reports/goal595_external_review_2026-04-19.md
/Users/rl2025/rtdl_python_only/docs/handoff/GOAL595_REREVIEW_REQUEST_2026-04-19.md
/Users/rl2025/rtdl_python_only/docs/reports/goal595_external_rereview_2026-04-19.md
```

## Result Summary

The final committed run uses 5 warmups, 20 measured repeats, and a stability
threshold of coefficient of variation <= 0.15.

| Workload | Embree median | Apple RT median | Apple/Embree | Parity | Stability |
| --- | ---: | ---: | ---: | --- | --- |
| 3D `ray_triangle_closest_hit` | 0.002547 s | 0.001470 s | 0.577x | true | false |
| 3D `ray_triangle_hit_count` | 0.002465 s | 0.417264 s | 169.243x | true | false |
| 2D `segment_intersection` | 0.008002 s | 0.067899 s | 8.486x | true | false |

All Apple RT rows match CPU reference. All Embree rows match CPU reference.

## Important Interpretation

The Apple RT timing cells are explicitly unstable in the final run. Therefore
the medians are valid only as engineering triage evidence. They must not be used
as public speedup wording. This is now enforced by the report format through a
`Stability` column and a `Stability Warnings` section.

This means Goal595 closes the measurement infrastructure requirement, not an
Apple RT performance claim.

## Verification

Command:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal595_apple_rt_perf_harness_test
```

Result:

```text
Ran 2 tests in 0.000s
OK
```

Command:

```text
PYTHONPATH=src:. python3 scripts/goal595_apple_rt_perf_harness.py --warmups 5 --repeats 20 --cv-threshold 0.15 --json-out docs/reports/goal595_apple_rt_repeatable_perf_macos_2026-04-19.json --md-out docs/reports/goal595_apple_rt_repeatable_perf_macos_2026-04-19.md
```

Result: JSON and Markdown artifacts written successfully.

## Consensus

Codex verdict: ACCEPT. The harness satisfies Goal595 because it provides a
repeatable procedure, parity checks, variance reporting, and an explicit
honesty boundary for unstable Apple RT timings.

External review sequence:

- First review: BLOCK because the original 7-repeat report exposed unstable
  closest-hit samples without a stability gate.
- Remediation: added coefficient-of-variation reporting, stability flags,
  `unstable_results`, 5-warmup/20-repeat rerun, and explicit wording that
  unstable medians are engineering-triage evidence only.
- Re-review: ACCEPT.

Goal595 is closed. Goal596 may proceed, with Goal595 as the baseline harness.

