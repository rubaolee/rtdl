# Gemini Review Request: Goals3818-3820 Benchmark Front-Door Hardening

Please perform an independent read-only review and write the result to:

`docs/reviews/goal3821_gemini_review_goal3818_3820_benchmark_front_door_hardening_2026-06-07.md`

## Scope

Review current `main` after:

- `f84b1bae Goal3818 record current benchmark smoke`
- `641e3391 Goal3819 trim report whitespace`
- `f7b19ac6 Goal3820 trim report whitespace`

## Files To Inspect

- `docs/reports/goal3818_current_benchmark_contract_smoke_a5000_2026-06-07.md`
- `tests/goal3818_current_benchmark_contract_smoke_a5000_test.py`
- `docs/reports/goal3818_current_benchmark_contract_smoke_a5000/summary.json`
- `docs/reports/goal3818_current_benchmark_contract_smoke_a5000/repair_summary.json`
- `docs/reports/goal3819_triangle_counting_native_mode_probe_2026-06-07.md`
- `tests/goal3819_triangle_counting_native_mode_probe_test.py`
- `docs/reports/goal3819_triangle_counting_native_mode_probe_a5000/triangle_native.stdout.txt`
- `docs/reports/goal3820_rtnn_prepared_optix_ranked_summary_app_mode_2026-06-07.md`
- `tests/goal3820_rtnn_prepared_optix_ranked_summary_app_mode_test.py`
- `docs/reports/goal3820_rtnn_prepared_optix_ranked_summary_app_mode_a5000/`
- `examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py`
- `examples/v2_0/research_benchmarks/rtnn/README.md`
- `examples/v2_0/research_benchmarks/triangle_counting/README.md`
- `examples/v2_0/research_benchmarks/hausdorff_xhd/README.md`
- `examples/v2_0/research_benchmarks/contact_manifold/README.md`

## Questions

1. Does Goal3818 fairly record that all ten promoted benchmark apps have at
   least one current executable A5000 route after the repaired Hausdorff and
   Contact Manifold commands?
2. Are the two initial Goal3818 failures correctly classified as command
   contract/fail-closed behavior rather than hidden app breakage?
3. Does Goal3819 correctly improve the triangle-counting command guidance by
   documenting explicit `--optix-graph-mode native` while preserving that the
   route still does not authorize RT-core triangle-count claims?
4. Does Goal3820 correctly close the RTNN benchmark-front-door gap by adding a
   current executable `prepared_optix_ranked_summary` mode that returns pure
   JSON and wraps the existing generic prepared OptiX ranked-summary aggregate?
5. Does the RTNN wrapper remain app-agnostic at the native-engine boundary and
   avoid hidden partner selection?
6. Do the reports/docs avoid release, package-install, public speedup, broad
   RT-core speedup, paper-reproduction, AMD performance, true-zero-copy,
   automatic partner selection, and app-specific native-engine claims?

## Validation To Reproduce If Useful

```powershell
$env:PYTHONPATH="src;."; py -3 -m unittest tests.goal3820_rtnn_prepared_optix_ranked_summary_app_mode_test tests.goal3819_triangle_counting_native_mode_probe_test tests.goal3818_current_benchmark_contract_smoke_a5000_test tests.goal3814_broad_current_doc_version_label_cleanup_test tests.goal3812_current_benchmark_docs_and_adequacy_aliases_test
```

A5000 pod validation at `f7b19ac6` passed:

```text
Ran 9 tests in 0.543s
OK
```

The committed RTNN app mode also ran on the pod with:

```bash
python examples/v2_0/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py --mode prepared_optix_ranked_summary --point-count 4096 --radius 0.02 --k 32 --repeat 2 --query-batch-size 4096 --distribution uniform
```

and returned `runner_payload.ok=true` with pure JSON stdout.

## Verdict

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.
