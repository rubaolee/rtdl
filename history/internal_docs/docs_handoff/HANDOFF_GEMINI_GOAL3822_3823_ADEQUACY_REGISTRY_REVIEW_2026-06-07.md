# Gemini Review Request: Goals3822-3823 Current Benchmark Adequacy And Front-Door Registry

Please perform an independent read-only review and write the result to:

`docs/reviews/goal3824_gemini_review_goal3822_3823_adequacy_registry_2026-06-07.md`

## Scope

Review current `main` after:

- `fe3ae8f2 Goal3822 refresh benchmark adequacy front doors`
- `456d9c0c Goal3823 add benchmark front-door registry`
- `56cdc3e0 Goal3823 add A5000 front-door registry artifact`

## Files To Inspect

- `src/rtdsl/v2_9_benchmark_adequacy.py`
- `src/rtdsl/current_benchmark_front_doors.py`
- `src/rtdsl/__init__.py`
- `scripts/goal3823_current_benchmark_front_door_runner.py`
- `docs/reports/goal3822_current_benchmark_adequacy_after_front_door_hardening_2026-06-07.md`
- `docs/reports/goal3823_current_benchmark_front_door_registry_2026-06-07.md`
- `docs/reports/goal3823_current_benchmark_front_door_registry_a5000/summary.json`
- `docs/learn/benchmark_partner_reference_matrix.md`
- `docs/learn/partner_choice_for_custom_logic.md`
- `docs/reports/goal3786_current_benchmark_adequacy_after_hiprt_closeout_2026-06-07.md`
- `tests/goal3822_current_benchmark_adequacy_after_front_door_hardening_test.py`
- `tests/goal3823_current_benchmark_front_door_registry_test.py`
- `tests/goal3786_current_benchmark_adequacy_after_hiprt_closeout_test.py`
- `tests/goal3812_current_benchmark_docs_and_adequacy_aliases_test.py`

## Questions

1. Does Goal3822 correctly update the current benchmark adequacy source of
   truth after Goals3818-3820 without changing it into a release packet or
   performance leaderboard?
2. Are the RTNN and triangle-counting adequacy rows now precise: RTNN points to
   the executable `prepared_optix_ranked_summary` app mode, and triangle
   counting points to explicit `--optix-graph-mode native` while preserving no
   RT-core triangle-count claim?
3. Does Goal3823 provide a single current command registry and bounded runner
   for all ten promoted benchmark app front doors?
4. Does the A5000 artifact fairly record all ten registered rows passing, and
   is it scoped as command-front-door evidence rather than public speedup
   evidence?
5. Does the runner avoid hidden partner selection and app-specific native-engine
   logic?
6. Do all touched files preserve claim boundaries: no release, package-install,
   public speedup, whole-app acceleration, broad RT-core, paper-reproduction,
   true-zero-copy, AMD performance, automatic partner selection, or
   app-specific native-engine claims?

## Validation To Reproduce If Useful

```powershell
$env:PYTHONPATH="src;."; py -3 -m unittest tests.goal3823_current_benchmark_front_door_registry_test tests.goal3822_current_benchmark_adequacy_after_front_door_hardening_test tests.goal3812_current_benchmark_docs_and_adequacy_aliases_test tests.goal3818_current_benchmark_contract_smoke_a5000_test
```

A5000 pod validation at `56cdc3e0` passed:

```text
Ran 16 tests in 0.531s
OK
```

The runner also executed all ten registered front doors on A5000 and produced
`docs/reports/goal3823_current_benchmark_front_door_registry_a5000/summary.json`
with `all_pass=true`.

## Verdict

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.
