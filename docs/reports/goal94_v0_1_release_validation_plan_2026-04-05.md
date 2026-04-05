# Goal 94 Plan: v0.1 Release Validation

Date: 2026-04-05
Status: planned

## Validation model

Goal 94 should use a two-tier release gate:

1. local preflight on the current workspace
2. clean Linux clone at the release head

The local preflight is advisory.

The clean Linux clone is the authoritative release gate.

This matches the current project reality:

- Linux clean-clone validation is the real backend trust anchor
- broader local macOS coverage is limited by the known `geos_c` rebuild issue
- release closure should not be blocked on that known local environment limit

## Planned release checks

### Local preflight

- Python syntax/compile sanity for the release-critical scripts and tests
- focused milestone regression tests
- targeted parser/view helper sanity

Recommended local commands:

```bash
cd /Users/rl2025/rtdl_python_only
python3 -m py_compile \
  src/rtdsl/datasets.py \
  src/rtdsl/optix_runtime.py \
  src/rtdsl/embree_runtime.py \
  scripts/goal50_postgis_ground_truth.py \
  scripts/goal69_pip_positive_hit_performance.py \
  scripts/goal71_prepared_backend_positive_hit_county.py \
  scripts/goal77_runtime_cache_measurement.py \
  tests/goal80_runtime_identity_fastpath_test.py \
  tests/goal69_pip_positive_hit_performance_test.py \
  tests/goal71_prepared_backend_positive_hit_county_test.py \
  tests/goal50_postgis_ground_truth_test.py \
  tests/optix_embree_interop_test.py
```

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest \
  tests.goal91_backend_boundary_support_test \
  tests.goal80_runtime_identity_fastpath_test \
  tests.goal89_backend_comparison_refresh_test \
  tests.goal76_runtime_prepared_cache_test \
  tests.rtdsl_py_test.RtDslPythonTest.test_rayjoin_cdb_parser_and_views \
  tests.goal28c_conversion_test \
  tests.goal69_pip_positive_hit_performance_test \
  tests.goal71_prepared_backend_positive_hit_county_test \
  tests.goal50_postgis_ground_truth_test \
  tests.optix_embree_interop_test \
  tests.goal79_linux_performance_reproduction_matrix_test
```

### Linux hard gate

- clean clone at the release head
- full matrix on Linux
- focused milestone add-on slice
- Vulkan hardware slice
- Goal 51 Vulkan validation summary
- fresh long exact-source backend summary reruns

Recommended Linux commands:

```bash
cd /home/lestat/work/rtdl_goal94_clean
PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group full
```

```bash
cd /home/lestat/work/rtdl_goal94_clean
PYTHONPATH=src:. python3 -m unittest \
  tests.goal91_backend_boundary_support_test \
  tests.goal80_runtime_identity_fastpath_test \
  tests.goal89_backend_comparison_refresh_test \
  tests.goal76_runtime_prepared_cache_test \
  tests.rtdsl_py_test.RtDslPythonTest.test_rayjoin_cdb_parser_and_views
```

```bash
cd /home/lestat/work/rtdl_goal94_clean
make build-vulkan
PYTHONPATH=src:. python3 -m unittest \
  tests.rtdsl_vulkan_test \
  tests.goal71_prepared_backend_positive_hit_county_test \
  tests.goal69_pip_positive_hit_performance_test
```

```bash
cd /home/lestat/work/rtdl_goal94_clean
PYTHONPATH=src:. RTDL_OPTIX_PTX_COMPILER=nvcc RTDL_NVCC=/usr/bin/nvcc \
python3 scripts/goal51_vulkan_validation.py \
  --output build/goal94_goal51_validation/summary.json
```

```bash
cd /home/lestat/work/rtdl_goal94_clean
PYTHONPATH=src:. python3 scripts/goal71_prepared_backend_positive_hit_county.py \
  --backend optix \
  --county-dir /home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/uscounty_feature_layer \
  --zipcode-dir /home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/zipcode_feature_layer \
  --output-dir build/goal94/optix_prepared \
  --host-label lestat-lx1-goal94
```

```bash
cd /home/lestat/work/rtdl_goal94_clean
PYTHONPATH=src:. python3 scripts/goal71_prepared_backend_positive_hit_county.py \
  --backend embree \
  --county-dir /home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/uscounty_feature_layer \
  --zipcode-dir /home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/zipcode_feature_layer \
  --output-dir build/goal94/embree_prepared \
  --host-label lestat-lx1-goal94
```

```bash
cd /home/lestat/work/rtdl_goal94_clean
PYTHONPATH=src:. python3 scripts/goal71_prepared_backend_positive_hit_county.py \
  --backend vulkan \
  --county-dir /home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/uscounty_feature_layer \
  --zipcode-dir /home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/zipcode_feature_layer \
  --output-dir build/goal94/vulkan_prepared \
  --host-label lestat-lx1-goal94
```

```bash
cd /home/lestat/work/rtdl_goal94_clean
PYTHONPATH=src:. python3 scripts/goal77_runtime_cache_measurement.py \
  --backend optix \
  --county-dir /home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/uscounty_feature_layer \
  --zipcode-dir /home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/zipcode_feature_layer \
  --output-dir build/goal94/optix_raw \
  --host-label lestat-lx1-goal94
```

```bash
cd /home/lestat/work/rtdl_goal94_clean
PYTHONPATH=src:. python3 scripts/goal77_runtime_cache_measurement.py \
  --backend embree \
  --county-dir /home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/uscounty_feature_layer \
  --zipcode-dir /home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/zipcode_feature_layer \
  --output-dir build/goal94/embree_raw \
  --host-label lestat-lx1-goal94
```

```bash
cd /home/lestat/work/rtdl_goal94_clean
PYTHONPATH=src:. python3 scripts/goal77_runtime_cache_measurement.py \
  --backend vulkan \
  --county-dir /home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/uscounty_feature_layer \
  --zipcode-dir /home/lestat/work/rayjoin_sources/uscounty_zipcode_exact/zipcode_feature_layer \
  --output-dir build/goal94/vulkan_raw \
  --host-label lestat-lx1-goal94
```

## Pass / fail standard

Pass only if:

- all Linux commands exit `0`
- the Linux full matrix passes
- the focused milestone add-on slice passes
- the GPU slice passes
- Goal 51 writes a summary with all `parity=true`
- the long exact-source backend summaries retain the accepted row count,
  digest, indexed PostGIS plan, and parity invariants

Important nuance:

- OptiX prepared is not required to beat PostGIS on every first prepared rerun
  because the accepted claim is a warmed prepared win, not an unconditional
  cold prepared win
- Vulkan is allowed to remain slower than PostGIS

## Main question

What is the smallest high-signal rerun package that still gives a trustworthy
release-head validation result for v0.1?
