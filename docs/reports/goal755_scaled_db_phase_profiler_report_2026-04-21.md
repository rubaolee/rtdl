# Goal755 Scaled DB Phase Profiler Report

## Verdict

ACCEPT.

Goal755 adds scaled fixture support to the DB phase profiler and runs Linux backend comparisons. The evidence identifies the next DB optimization target: prepared RT backends make query phases much faster, but one-shot prepared dataset construction dominates total app time.

## Consensus

- Codex implementation and validation: ACCEPT.
- Gemini Flash plan review: ACCEPT, no blockers.
- Gemini Flash finish review: ACCEPT, no blockers.
- Windows review request was sent through the bridge. No Windows finish result was required to execute this diagnostic step because the plan already had 2-AI consensus from Codex and Gemini.

## Implementation

Updated profiler:

- `/Users/rl2025/rtdl_python_only/scripts/goal693_db_phase_profiler.py`

Updated tests:

- `/Users/rl2025/rtdl_python_only/tests/goal693_db_phase_profiler_test.py`

New profiler options:

- `--copies N`: repeats deterministic DB fixtures to expose scaled behavior.
- `--last-output-mode full|summary`: keeps old full-output behavior by default, but allows compact evidence for large runs.

Important correction: the profiler now mirrors the real public `sales_risk` app path for RT backends by preparing one dataset and running three prepared queries. The first scaled run exposed that the old profiler path was unfair because it used three unprepared `run_*` calls for RT backends.

## Linux Evidence

Host: `lestat-lx1`

Fixture scale:

- `copies=20000`
- `regional_dashboard`: 140,000 rows
- `sales_risk`: 120,000 rows
- `iterations=3`
- output mode: compact summary

Evidence files:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal755_db_phase_cpu_reference_copies20000_linux_2026-04-21.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal755_db_phase_embree_copies20000_linux_2026-04-21.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal755_db_phase_optix_copies20000_linux_2026-04-21.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal755_db_phase_vulkan_copies20000_linux_2026-04-21.json`

GTX 1070 boundary: this is backend behavior evidence, not RTX RT-core speedup evidence.

## Regional Dashboard Results

Median seconds:

| Backend | Input build | Native prepare | Query scan | Query grouped count | Query grouped sum | Total |
|---|---:|---:|---:|---:|---:|---:|
| `cpu_reference` | 0.033334 | n/a | n/a | n/a | n/a | 0.574799 |
| `embree` | 0.035084 | 0.682085 | 0.094195 | 0.031812 | 0.024897 | 0.869333 |
| `optix` | 0.034644 | 0.658928 | 0.147177 | 0.083572 | 0.081850 | 1.006391 |
| `vulkan` | 0.034994 | 0.664756 | 0.175493 | 0.079599 | 0.077886 | 1.103061 |

Interpretation:

- RT prepared query phases are small after preparation.
- One-shot native preparation is larger than the CPU reference total for this fixture.
- For this app shape, prepared dataset reuse is the required next optimization before claiming app-level speedup.

## Sales Risk Results

Median seconds:

| Backend | Input build | Native prepare | Query scan | Query grouped count | Query grouped sum | Python postprocess | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| `cpu_reference` | 0.027460 | n/a | 0.265127 | 0.242942 | 0.250334 | 0.006319 | 0.790234 |
| `embree` | 0.027187 | 0.516756 | 0.051826 | 0.026135 | 0.026235 | 0.005869 | 0.653485 |
| `optix` | 0.027025 | 0.501863 | 0.084089 | 0.057467 | 0.056774 | 0.005771 | 0.733702 |
| `vulkan` | 0.026924 | 0.508971 | 0.076829 | 0.047498 | 0.046490 | 0.005751 | 0.732711 |

Interpretation:

- The prepared RT path is already faster than CPU total for this sales-risk fixture, even with one-shot preparation.
- Query phases are much faster than CPU once the dataset is prepared.
- Native preparation is still the dominant cost for RT backends.

## Main Conclusion

The DB app should stay classified as `python_interface_dominated` for public claims until we improve the prepared-session interface. The evidence also shows the classification is too coarse for engineering: query execution is no longer the main problem after prepared datasets; one-shot preparation and app/interface reuse policy are the bottlenecks.

## Next Optimization

Implement a public prepared DB app/session mode:

- build the prepared dataset once;
- run multiple query bundles against the same dataset;
- expose phase timing for cold prepare, warm query, and close;
- keep compact result summaries for apps that only need counts/sums;
- avoid rebuilding the same prepared dataset for every app invocation where the table is unchanged.

This is a better next step than rewriting native DB kernels immediately, because the measured query phases are already small relative to preparation.

## Verification

Local macOS:

```bash
PYTHONPATH=src:. python3 -m unittest -v tests.goal693_db_phase_profiler_test tests.goal692_optix_app_correctness_transparency_test
python3 -m py_compile scripts/goal693_db_phase_profiler.py tests/goal693_db_phase_profiler_test.py
git diff --check
```

Result: 11 tests OK; py_compile OK; diff check OK.

Linux:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIB=$PWD/build/librtdl_optix.so RTDL_VULKAN_LIB=$PWD/build/librtdl_vulkan.so \
python3 -m unittest -v tests.goal693_db_phase_profiler_test tests.goal692_optix_app_correctness_transparency_test
```

Result: 11 tests OK.
