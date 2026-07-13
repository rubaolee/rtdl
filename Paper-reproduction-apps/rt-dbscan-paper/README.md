# RT-DBSCAN Paper Reproduction App

This directory is the bounded RT-DBSCAN paper-reproduction project for RTDL.

The AuthorOfficial comparator, bounded same-input fixtures, and representative
synthetic partition matrix are complete. This remains a scoped reproduction:
the exact paper preprocessing and full dataset/performance matrix are not
available, and RTDL deliberately does not copy the author's index-directional
border-assignment behavior into the general system.

## Paper And Artifact

- Paper: `RT-DBSCAN: Accelerating DBSCAN using Ray Tracing Hardware`
- Venue: `IPDPS 2023`
- DOI: `10.1109/IPDPS54959.2023.00100`
- Authors recorded by the existing benchmark metadata:
  - Vani Nagarajan
  - Milind Kulkarni

Candidate author artifact:

- repository: `https://github.com/vani-nag/OWLRayTracing`
- branch: `rt-dbscan`
- commit: `92749fe82ed001e5b7303265d4a2a73aa1bbf529`
- sample path: `samples/cmdline/s02-rtdbscan`

This artifact has been located, patched as an AuthorOfficial comparator, built
on a CUDA/OptiX POD, and executed for bounded same-input gates. Exact paper input
provenance is not pinned yet.

Goal5105 records dataset provenance candidates in:

```text
data/paper_dataset_candidates.json
```

The paper names four real datasets: `3DRoad`, `NGSIM`, `Porto`, and `3DIono`.
The pinned author source reads a command-line input file and does not ship those
preprocessed point files. Its source comments point at developer-local files for
`3D_iono.txt`, `porto.txt`, and `3droad_full.csv`; no packaged NGSIM file was
found. Public source candidates exist for 3DRoad, Porto, and NGSIM, but the
exact paper preprocessing and point ordering remain unpinned.

## Existing RTDL Assets

The current repository already contains RT-DBSCAN-style work under:

```text
examples/current/research_benchmarks/rt_dbscan/
examples/current/apps/ml/rtdl_dbscan_clustering_app.py
```

Those files are historical benchmark and application assets. They are not by
themselves paper-reproduction evidence; the gates and artifacts in this
directory provide the current paper-app evidence.

## RTDL Program

The initial RTDL language/system surface for this paper app is expected to be:

```text
fixed_radius_neighbors
prepare_generic_fixed_radius_count_threshold_2d
run_generic_fixed_radius_count_threshold_2d
run_generic_prepared_fixed_radius_threshold_reached_count_2d
prepare_optix_fixed_radius_count_threshold_2d
prepare_optix_fixed_radius_count_threshold_3d
fixed_radius_count_threshold_2d_partner_columns
fixed_radius_count_threshold_3d_partner_columns
```

The benchmark line also uses partner continuations for component signatures and
cluster summaries. Those partner routes must be audited before they are treated
as paper-app evidence.

## App-Owned Code

The RT-DBSCAN app owns:

- paper workload selection,
- paper input provenance,
- DBSCAN epsilon/min-points policy,
- cluster expansion and label interpretation,
- author comparator or source-of-truth selection,
- route-choice policy,
- performance-regime selection.

These are not RTDL core semantics unless a separate generic contract is defined
and reviewed.

## Reproduction Scope

Current status:

```text
bounded_same_input_authorofficial_gates_passed
representative_synthetic_partition_matrix_executed
```

Closed bounded gates:

```text
core-count gate: tiny3d_core_count.csv
component-partition gate: tiny3d_core_count.csv
component-partition gate: border_noise3d_component_signature.csv
representative component-partition matrix: 3 synthetic fixtures
```

Current AuthorOfficial POD status:

```text
core_count=7
tiny_partition=[0,0,0,0,1,1,1,-1]
border_noise_partition=[0,0,0,0,0,0,1,1,1,1,1,-1]
signature_matched=true
component_partition_matched=true
core_flags_matched=true
matched=true
author_comparator_used=true
```

This is a bounded same-input result against a patched AuthorOfficial comparator.
It is not a full paper reproduction result and does not use the exact paper
datasets.

Representative synthetic fixtures have also been generated and executed:

```text
representative_medium_two_clusters3d.csv
representative_border_shell3d.csv
representative_three_components_noise3d.csv
```

All three representative fixtures match patched AuthorOfficial under canonical
component partition, core flags, and normalized component signature. These are
larger controlled fixtures, not exact paper datasets.

AuthorOfficial gate packet status:

```text
executed_on_pod
```

The packet contains:

- `data/fixtures/tiny3d_core_count.csv`, a bounded same-input 3D fixture;
- `author_patches/goal5092_authorofficial_core_count_output.patch`, a minimal
  patch that exposes the author's `core_count`, `component_labels`,
  `component_sizes`, `noise_count`, `core_flags`, and `parent_roots` without
  changing the RT-DBSCAN kernels;
- `scripts/setup_authorofficial_core_count.sh`, a POD setup/build wrapper;
- `scripts/run_authorofficial_core_count_gate.py`, a same-input comparator
  runner that can compare patched author output against RTDL.
- `scripts/run_authorofficial_component_signature_gate.py`, a same-input
  component-partition comparator runner.

The component runner now compares canonical point partitions modulo component
label renaming. It also records normalized component signatures. The partition
gate exists because component-size signatures alone are blind to some border
point assignment errors.

The app now uses the generic RTDL component-partition helpers:

```text
rtdsl.canonical_partition_labels
rtdsl.component_signature_from_partition
rtdsl.partition_equivalent
```

Those helpers compare component partitions modulo label renaming and preserve a
noise label. They are generic result-comparison helpers, not DBSCAN primitives.

Validated RTDL system routes:

```text
fixed_radius_count_threshold_3d
prepare_optix_numba_radius_graph_grouped_stream_continuation_3d
radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns
```

This app currently does not claim:

- full RT-DBSCAN paper reproduction,
- exact paper dataset reproduction,
- author-performance parity,
- whole-program speedup,
- DBSCAN-native RTDL engine ABI,
- automatic route selection.

## Performance Scope

No public paper-app performance claim is made by this scaffold.

Historical benchmark evidence may be useful for requirements, but it must not be
copied into this paper app as a reproduction result until the input, comparator,
and phase boundary are pinned.

The current representative matrix records bounded diagnostic timing only:

```text
cold one-shot RTDL: 1.61s to 1.72s on the three synthetic representatives
warm long-lived-process RTDL median: 0.0041s to 0.0057s
```

Cold one-shot RTDL is much slower than the author's reported phase totals on
these small fixtures because first-use setup/compilation dominates. Warm
long-lived-process medians are much smaller, but they are diagnostic only and
must not be used as a public speedup claim or exact paper-performance result.
This packet does not include an equivalent author warm-process loop.

Goal5104 adds that author warm-loop counterpart for the representative synthetic
fixtures. In that bounded diagnostic, steady RTDL medians remain about
`0.097x-0.237x` of the patched author's inner-loop medians. This is still not an
exact paper-performance result.

## Next Step

The next decision is explicit:

1. stop this bounded RT-DBSCAN line here and send Goals5093-5095 as the
   closed bounded same-input packet; or
2. add a larger representative same-input fixture and require canonical
   partition equality again; or
3. separately pursue exact paper dataset provenance.

Goals5097-5103 took option 2 for three synthetic representative fixtures. The
remaining decisions are now:

1. stop after the bounded representative packet and external review;
2. pursue exact paper dataset provenance; or
3. define a real long-lived prepared-service regime and measure it separately.

Do not turn the current bounded result into a full RT-DBSCAN paper reproduction
claim.

Goal5105 took option 2 only as a provenance audit. It identifies candidate
dataset sources and author-local filename hints, but it does not close exact
paper dataset reproduction.
