# Goal4186: Contact Native Collect Repeat Accounting on RTX 4000 Ada

Date: 2026-06-09  
Source commit: `84546788`  
Artifact directory: `docs/reports/goal4186_contact_native_collect_repeat_accounting_rtx4000ada/`

## Purpose

Goal4185 found that the short-row contact-manifold stress run was not
claim-grade even though the wrapper ran for a measurable amount of time. The
problem was not the generic RTDL primitive itself. The problem was that
`native_collect_k` accepted the benchmark-level `--repeat-count` option but did
not expose repeat-aware native timing fields for that mode, so downstream
readers only saw a single short `native_collect_elapsed_sec` value.

Goal4186 fixes that measurement contract for the contact-manifold benchmark app
without changing the engine primitive:

- `repeat_count` now controls repeated calls to the same generic native collect
  symbol.
- `native_collect_elapsed_sec` remains the legacy median-style field.
- `native_collect_runs_sec`, `native_collect_total_sec`, min/max, and
  `native_collect_repeat_count` expose the aggregate timing needed for stress
  packets.
- The repeated native calls must emit stable `candidate_id_rows`; otherwise the
  app fails closed.

## Pod Evidence

Pod command:

```bash
python3 examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py \
  --mode native_collect_k --backend optix --dataset grid --grid-count 64 \
  --witness-capacity 128 --repeat-count 10000
```

RTX 4000 Ada result:

| Field | Value |
| --- | ---: |
| `repeat_count` | 10000 |
| `native_collect_repeat_count` | 10000 |
| `len(native_collect_runs_sec)` | 10000 |
| `native_collect_total_sec` | 2.063397765159607 |
| `native_collect_elapsed_sec` | 0.00020331889390945435 |
| `native_collect_min_sec` | 0.000197678804397583 |
| `native_collect_max_sec` | 0.0009395405650138855 |
| `matches_cpu_reference` | `true` |
| `native_generic_symbol` | `rtdl_optix_collect_k_bounded_i64` |
| `valid_count` | 64 |
| `overflowed` | `false` |

The aggregate now crosses the one-second stress-evidence threshold while the old
median field remains available for compatibility.

## Boundary

This is not a new public speedup claim. It is measurement hardening for one of
the short-row benchmark rows.

The native engine remains app-agnostic:

- The native symbol is the generic `rtdl_optix_collect_k_bounded_i64`.
- Candidate discovery and contact interpretation remain outside the native
  collect primitive.
- The payload explicitly states that native mode validates only app-name-free
  `COLLECT_K_BOUNDED` i64 collection over Python oracle rows.

## Validation

Local:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2621_contact_manifold_collect_k_bounded_benchmark_candidate_test tests.goal4185_short_row_stress_calibration_test
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4182_current_benchmark_scale_profile_refresh_test
py -3 -m compileall -q examples\v2_0\research_benchmarks\contact_manifold\rtdl_contact_manifold_benchmark_app.py tests\goal2621_contact_manifold_collect_k_bounded_benchmark_candidate_test.py tests\goal4185_short_row_stress_calibration_test.py
```

Pod:

```bash
timeout 180s python3 examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py \
  --mode native_collect_k --backend optix --dataset grid --grid-count 64 \
  --witness-capacity 128 --repeat-count 10000
```

The focused artifact test is `tests.goal4186_contact_native_collect_repeat_accounting_test`.
