# Goal5129 - X-HD Full Paper Reproduction Plan

## Verdict

`plan_full_xhd_reproduction__dataset_provenance_first`

## Current Position

The X-HD app currently has:

- bounded same-input correctness complete;
- author `hd_exec` build/run route on POD using an `Author+BuildPatch` route;
- bounded 2D and 3D author JSON gates matched;
- bounded 2D and 3D RTDL exact column-route gates matched;
- directed `input1 -> input2` semantics verified by a discriminating asymmetric
  fixture;
- system extraction completed for generic nearest/witness/max-nearest helpers.

This is **not** full X-HD paper reproduction.

## What "Full Paper Reproduction" Means

Full paper reproduction must be evidence-driven, not aspirational. The X-HD
paper contains several distinct reproducible targets:

1. **Dataset/statistics reproduction**
   - Table 1 dataset families and point counts / Gini indices.
   - MRI: BraTS 2020, 494 images.
   - Geospatial: USCounty, USZipcode, Lakes, Parks, USWater, USCensus, All Nodes
     partially used.
   - Graphics: Dragon, AsianDragon, HappyBuddha, ThaiStatuette.

2. **Correctness reproduction**
   - Same input, same author binary / route.
   - At least one exact or same-source representative input per major category:
     geospatial 2D, graphics 3D, MRI 3D.
   - Compare `HDResult` under the already established directed input1-to-input2
     contract.

3. **Author phase/performance reproduction**
   - Preserve author `Running.AvgTime` / `ReportedTime`.
   - Preserve process wall time separately.
   - Use the paper's measurement boundary: GPU timing starts after datasets are
     loaded onto GPU and stops when HD is produced.

4. **Algorithmic / component reproduction**
   - X-HD RT variant behavior, not only exact Python/NumPy reference.
   - Where available, collect intersections, visited point pairs, heavy-cell
     offload phases, radius strategy, grid auto-sizing, and memory footprint.

5. **Figure/table reproduction**
   - Minimum: reproduce a bounded subset of Figure 5 / Table 1 style evidence.
   - Preferred: reproduce at least one real paper category figure slice.
   - Full: reproduce all Figure 5-11 claims under matching data and hardware
     regimes.

## Blocking Reality

The current workspace/POD evidence does **not** include the paper datasets.
Earlier Goal5121 found author logs and scripts referencing paths like:

```text
/local/storage/shared/HDDatasets/...
```

but that data root was absent. The author repository contains source, scripts,
and logs, but not the input datasets themselves.

Therefore the next work must start with dataset provenance and acquisition.

## Reproduction Levels

### Level A - Bounded Same-Input

Status: complete.

Evidence:

- tiny2d;
- bounded2d;
- bounded3d;
- directed2d_asymmetric;
- RTDL exact column route for bounded 2D/3D.

### Level B - Same-Source Representative

Status: not complete.

Definition:

- inputs come from the same public source family named by the paper;
- preprocessing is documented and repeatable;
- point counts / dimensions are recorded;
- claim label is representative, not exact paper reproduction.

Examples:

- Census/TIGER-derived geospatial shapes;
- Stanford 3D Scanning Repository meshes;
- BraTS-derived voxel point sets if access/license permits.

### Level C - Exact Paper Dataset

Status: not complete.

Definition:

- dataset files, generated point sets, or conversion outputs have file-level
  provenance strong enough to identify the exact experiment;
- acceptable exactness evidence includes author-provided files, retained hashes,
  byte-identical converted point sets, or a documented author script that
  deterministically regenerates the same point sets from pinned public source
  files;
- counts match Table 1 / logs after preprocessing.

Important boundary:

- Matching point counts, dimensions, Gini indices, bounding boxes, or other
  summary statistics is **necessary but not sufficient** for exact paper
  dataset reproduction.
- A reconstructed public dataset with matching statistics remains Level B
  `same-source representative` unless file/hash/provenance evidence proves it
  is the exact paper input.
- file provenance, conversion scripts, and hashes are retained.

### Level D - Full Paper Figure Reproduction

Status: not complete.

Definition:

- multiple datasets across MRI/geospatial/graphics;
- author X-HD plus baselines where feasible;
- aligned hardware and measurement regime;
- fair figure/table reconstruction with explicit deviations.

Level D depends on Goal5134. Figure/performance reproduction is not authorized
unless the X-HD algorithmic route gap analysis shows that the relevant author
RT/grid/pruning/offload phases are either reproduced, fairly substituted, or
explicitly excluded from the claim.

## Proposed Goal Sequence

### Goal5130 - Paper Target Matrix

Extract from the PDF and author repository:

- datasets;
- figures/tables;
- baseline algorithms;
- required metrics;
- author CLI and script entrypoints;
- available logs.

Exit:

```text
xhd_paper_target_matrix_ready
```

### Goal5131 - Dataset Provenance And Acquisition Matrix

For every dataset named by the paper:

- exact input available?
- same-source public source available?
- license/access constraints?
- conversion path known?
- expected point count / dimensions?
- author log match available?

Exit labels:

```text
exact_xhd_paper_inputs_available
same_source_representative_inputs_available
xhd_full_reproduction_blocked_on_unavailable_inputs
```

### Goal5132 - First Real Same-Source Representative Gate

Choose the lowest-risk dataset category:

- likely graphics if Stanford meshes are accessible and small enough;
- otherwise a geospatial TIGER/OSM same-source subset.

Run:

- author `hd_exec`;
- RTDL exact route;
- optional X-HD-style route if available;
- compare `HDResult`;
- keep raw input, conversion script, author JSON, RTDL JSON.

Exit:

```text
xhd_representative_same_source_gate_matched
```

### Goal5133 - Author Script / Log Reconciliation

Map author `expr/` scripts/logs to:

- paper Figure 5-11 claims;
- exact CLI arguments;
- output schemas;
- repetition counts;
- parameters for baselines and variants.

Exit:

```text
xhd_author_experiment_scripts_mapped
```

### Goal5134 - X-HD Algorithmic Route Gap Analysis

Compare current RTDL capabilities against the actual X-HD algorithm:

- grid grouping;
- radius growth;
- pruning by HD estimators;
- RT nearest-cell traversal;
- heavy-cell offload;
- adaptive grid sizing;
- memory footprint metrics.

Classify each as:

- already in RTDL generic system;
- can be built as generic API;
- app-owned;
- out of scope.

Exit:

```text
xhd_algorithmic_gap_matrix_ready
```

### Goal5135 - Representative Performance Matrix

Only after Goal5132/5133:

- author `Running.AvgTime`;
- author process wall;
- RTDL route time;
- setup/preprocess/load separated;
- no ratio unless denominator and hardware align.

Exit:

```text
xhd_representative_performance_matrix_with_boundaries
```

### Goal5136 - Full Reproduction Closeout Decision

Choose the honest final status:

```text
xhd_representative_same_source_reproduction_complete
xhd_exact_paper_reproduction_complete
xhd_full_reproduction_blocked_on_dataset_unavailability
```

## Immediate Next Action

Start Goal5130 + Goal5131 together:

- build the paper target matrix;
- inspect author repository scripts/logs;
- search public sources for dataset availability;
- do not implement more RTDL route code until the input provenance question is
  answered.

## Claim Boundary

Not authorized at this point:

- exact paper reproduction;
- Figure 5-11 reproduction;
- author speedup parity;
- performance ratio against author;
- treating reconstructed public datasets as exact paper inputs without proof.

Authorized:

- "X-HD bounded same-input reproduction is complete."
- "Full paper reproduction is now entering target-matrix and dataset-provenance
  phase."
