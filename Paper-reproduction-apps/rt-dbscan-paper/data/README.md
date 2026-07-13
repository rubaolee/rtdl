# RT-DBSCAN Data

This directory records data provenance for the RT-DBSCAN paper app.

Current status:

```text
paper inputs not pinned; bounded and representative same-input fixtures added
```

The manifest pins the AuthorOfficial source and records the bounded fixture
evidence. It does not identify exact paper dataset files or their preprocessing
and ordering contract.

Goal5105 adds a provenance ledger for the paper datasets:

```text
paper_dataset_candidates.json
```

The ledger identifies the paper's four dataset names and public/source
candidates:

- `3DRoad` -> UCI 3D Road Network (North Jutland, Denmark)
- `Porto` -> UCI Taxi Service Trajectory - Prediction Challenge
- `3DIono` -> author-local `3D_iono.txt` hint plus public TEC-source candidates
- `NGSIM` -> U.S. DOT NGSIM vehicle trajectories

This is not enough to claim exact dataset reproduction. The pinned author
artifact reads an input file from the command line and does not package the
paper's preprocessed `x y z` point files. The public sources still need exact
paper preprocessing, point-order, coordinate selection, size-prefix, epsilon,
and minPts reconstruction before they can become exact paper inputs.

Future work must add one of:

- exact paper inputs and comparator outputs;
- a bounded same-input artifact generated from a pinned author program;
- a representative public input explicitly labeled as representative, not exact
  paper data.

Current bounded fixture:

```text
fixtures/tiny3d_core_count.csv
fixtures/tiny3d_core_count_expected.json
```

This fixture is for the first AuthorOfficial core-count gate only. It is not an
exact paper dataset and must not be described as full RT-DBSCAN reproduction.

Additional bounded fixtures:

```text
fixtures/border_noise3d_component_signature.csv
fixtures/representative_medium_two_clusters3d.csv
fixtures/representative_border_shell3d.csv
fixtures/representative_three_components_noise3d.csv
fixtures/representative_fixtures_manifest.json
```

The representative fixtures are synthetic same-input cases used for canonical
component-partition comparison against patched AuthorOfficial. They are not
paper datasets and must not be described as exact RT-DBSCAN paper reproduction.

Goal5106 adds a UCI 3DRoad same-source candidate:

```text
source/uci_3droad/3d_road_network_north_jutland_denmark.zip
source/uci_3droad/3D_spatial_network.txt
fixtures/uci_3droad_1k_author_2d_zero_z.csv
fixtures/uci_3droad_16k_author_2d_zero_z.csv
fixtures/uci_3droad_full_author_2d_zero_z.csv
```

The candidate transformation writes `(longitude, latitude, 0.0)` rows for the
author input contract. This is a same-source public candidate, not the author's
packaged `3droad_full.csv` and not an exact paper input.

POD smoke status:

```text
1K AuthorOfficial payload produced, but process exits with SIGSEGV during teardown.
1K author payload and CPU reference agree on core_count/core_flags but not on
component partition/signature.
16K AuthorOfficial run reaches timing output but also exits with SIGSEGV.
```

Therefore the UCI 3DRoad route is not yet a clean correctness gate.

Goal5107 explains the 1K component mismatch and stabilizes the author teardown:

```text
author_patches/goal5107_authorofficial_skip_context_destroy_after_payload.patch
scripts/analyze_uci_3droad_author_contract.py
results/uci_3droad_1k_goal5107_contract_analysis.json
results/uci_3droad_1k_author_goal5107_clean.jsonl
results/uci_3droad_16k_author_goal5107_clean.jsonl
```

The 1K mismatch is not explained by the fixed-radius core predicate. Core flags
match. It is explained by the author's index-directional border-assignment
contract: in the author call-2 path, a non-core point can be attached by a core
neighbor only when the current ray/source index is greater than the primitive
index (`xID > primID`). A conventional DBSCAN reference attaches a border point
to any core neighbor.

On the 1K UCI 3DRoad same-source candidate:

```text
conventional_mismatch_count=12
author_directional_mismatch_count=0
author_signature={core_count=329, component_sizes=[90,168,181], noise_count=561}
conventional_signature={core_count=329, component_sizes=[102,168,181], noise_count=549}
```

The 12 conventional-reference-only border points each have lower-index core
neighbors and no higher-index core neighbors. They therefore remain noise under
the author contract.

The teardown patch is comparator-only: it sets
`RTDL_AUTHOROFFICIAL_SKIP_CONTEXT_DESTROY=1` to return cleanly after payload and
timing output, without changing kernels or DBSCAN payload semantics. Clean
author outputs now exist for the 1K and 16K same-source candidates, but this is
still not exact paper input reproduction and not an RTDL 3DRoad correctness gate.

Goal5108 promotes that diagnosed contract into the app runner:

```text
scripts/run_authorofficial_component_signature_gate.py --backend author_directional_cpu_reference
results/uci_3droad_1k_author_directional_gate_summary.json
```

On the 1K UCI 3DRoad same-source candidate, the conventional CPU reference still
mismatches the clean author payload, while the author-directional app reference
matches exactly:

```text
matched=true
signature_matched=true
component_partition_matched=true
core_flags_matched=true
```

This backend is intentionally app-owned. It is not exported as an RTDL core
primitive and must not be described as conventional DBSCAN.

The RTDL OptiX+Numba route remains blocked on the current POD by a CUDA/PTX
toolchain mismatch: Numba emits PTX 8.7, while the active driver/linker path
accepts PTX 8.4. Goal5108 narrows this to an environment/toolchain blocker, not
a 3DRoad correctness failure.

Goal5109 tries a GPU partner route that avoids the Numba PTX blocker:

```text
scripts/run_authorofficial_component_signature_gate.py --backend optix_cupy_component_signature
results/uci_3droad_1k_optix_cupy_author_directional_gate_summary.json
```

The route successfully runs the existing generic RTDL OptiX + CuPy grouped
stream component-label pipeline on the 1K UCI 3DRoad same-source candidate, but
it does not match the pinned AuthorOfficial directional-border contract:

```text
matched=false
core_flags_matched=true
rtdl_signature={core_count=329, component_sizes=[102,168,181], noise_count=549}
author_signature={core_count=329, component_sizes=[90,168,181], noise_count=561}
```

This is a semantic-contract gap, not merely an execution-environment gap. The
generic RTDL grouped-stream route currently behaves like the conventional
component partition on this input; the pinned author program applies an
index-directional border-attachment rule. That author-specific rule remains
outside RTDL core and must not be promoted as ordinary DBSCAN semantics.

Project decision after Goal5109: do not open a new author-directional SoS or
border-assignment route for RT-DBSCAN. RTDL's SoS/degeneracy protocols were
settled through the RayJoin line and are not reopened for this app. Therefore
this 1K same-source result is recorded as an AuthorOfficial semantic-contract
gap, not as a reason to change RTDL language semantics.
