# RT-DBSCAN Results

Current results:

```text
core_count_smoke_summary.json
authorofficial_core_count_gate_local_cpu_summary.json
authorofficial_core_count_gate_pod_cpu_summary.json
authorofficial_core_count_gate_pod_optix_summary.json
component_signature_gate_local_cpu_summary.json
authorofficial_component_signature_gate_pod_cpu_summary.json
authorofficial_component_signature_gate_pod_optix_summary.json
component_signature_border_noise_local_cpu_summary.json
authorofficial_component_signature_border_noise_pod_optix_summary.json
representative_partition_matrix_local_cpu_summary.json
representative_partition_matrix_pod_optix_summary.json
representative_partition_matrix_*_cold_pod_optix_summary.json
```

`core_count_smoke_summary.json` is a local RTDL CPU-reference/oracle smoke. It
records `core_count=7` and `matches_oracle=true` for the tiny synthetic fixture.

`authorofficial_core_count_gate_local_cpu_summary.json` verifies the bounded
same-input gate runner in `cpu_reference` mode and records `core_count=7`.

`authorofficial_core_count_gate_pod_cpu_summary.json` and
`authorofficial_core_count_gate_pod_optix_summary.json` are live POD
AuthorOfficial comparator results. Both record:

```text
author_comparator_used=true
matched=true
author.core_count=7
rtdl.core_count=7
bounded_core_count_reproduction_claim_authorized=true
paper_reproduction_claim_authorized=false
performance_claim_authorized=false
```

These POD results close only the bounded same-input RT-DBSCAN core-count gate.
They are not exact paper-input results, full DBSCAN label results, or performance
results.

The component-partition files are the next bounded gate. They compare canonical
point partitions modulo component-label renaming, and also record the normalized
signature:

```text
core_count=7
component_sizes=[3,4]
noise_count=1
canonical_component_labels=[0,0,0,0,1,1,1,-1]
```

`authorofficial_component_signature_gate_pod_optix_summary.json` uses RTDL's
generic prepared OptiX + Numba fixed-radius graph component-label path:

```text
partner_reference_contract=generic_prepared_optix_numba_grouped_stream_component_labels_3d
materializes_neighbor_rows=false
```

This closes only a bounded same-input component-partition gate. It intentionally
materializes the output component-label column for the app-owned comparator. It
still does not claim exact author label IDs, full DBSCAN output format, exact
paper inputs, or performance.

The border/noise fixture is a stronger second component-partition gate. It uses:

```text
epsilon=0.35
min_points=5
point_count=12
```

It includes one non-core border point assigned to a component and one distant
noise point. The POD AuthorOfficial-vs-RTDL OptiX+Numba result is:

```text
matched=true
component_partition_matched=true
core_flags_matched=true
core_count=10
component_sizes=[5,6]
noise_count=1
canonical_component_labels=[0,0,0,0,0,0,1,1,1,1,1,-1]
```

Existing benchmark evidence remains in the benchmark and internal history
trees. It should not be copied here as a paper-app result until the paper-app
input, comparator, and performance regime are pinned.

## Representative Matrix

The representative matrix uses three controlled synthetic 3D fixtures:

```text
representative_medium_two_clusters3d
representative_border_shell3d
representative_three_components_noise3d
```

The live POD OptiX+Numba summary is:

```text
representative_partition_matrix_pod_optix_summary.json
```

All three cases match patched AuthorOfficial under canonical component
partition, core flags, and normalized signature:

```text
medium: core_count=96, component_sizes=[48,48], noise_count=4
border_shell: core_count=54, component_sizes=[29,29], noise_count=2
three_components: core_count=61, component_sizes=[16,18,27], noise_count=3
```

## Bounded Timing Matrix

The timing matrix has two different regimes.

Cold one-shot POD runs start a fresh Python process per case:

```text
medium: RTDL 1.605694s, author reported total 0.047156s
border_shell: RTDL 1.717175s, author reported total 0.023916s
three_components: RTDL 1.627829s, author reported total 0.026826s
```

Warm long-lived-process diagnostics run repeated RTDL cases in one Python
process. The author side in this packet is not run as an equivalent warm
in-process loop, so these numbers are useful diagnostics but not a regime-matched
author speedup comparison:

```text
medium: RTDL median 0.005739s, author reported total median 0.048403s
border_shell: RTDL median 0.004121s, author reported total median 0.025299s
three_components: RTDL median 0.004083s, author reported total median 0.021747s
```

The warm numbers are diagnostic only. They do not authorize a public speedup
claim because the fixtures are synthetic, the author warm-process counterpart is
not measured, the process regime is different, and the exact paper datasets are
not pinned.

## Author Warm-Loop Matrix

Goal5104 adds an author warm-loop counterpart:

```text
authorofficial_warm_loop_matrix_pod_summary.json
authorofficial_warm_loop_outputs/*.jsonl
```

The patched AuthorOfficial binary repeats call-1/core and call-2/cluster in one
process after pipeline/accel setup. RTDL repeats its generic OptiX+Numba route
in one Python process. Steady medians exclude the first repeat.

```text
medium: author inner-loop 0.040645s, RTDL 0.003942s, ratio 0.097x
border_shell: author inner-loop 0.018776s, RTDL 0.003864s, ratio 0.206x
three_components: author inner-loop 0.015787s, RTDL 0.003736s, ratio 0.237x
```

This makes the warm diagnostic fairer than the earlier matrix, but it still does
not authorize an exact paper-performance or whole-program speedup claim because
the fixtures are synthetic representatives.
