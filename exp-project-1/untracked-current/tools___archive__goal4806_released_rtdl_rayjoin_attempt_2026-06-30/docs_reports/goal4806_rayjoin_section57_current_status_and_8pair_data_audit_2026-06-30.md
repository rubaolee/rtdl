# Goal4806 RayJoin Section 5.7 Current Status And 8-Pair Data Audit

Date: 2026-06-30

## Purpose

Goal4806 is still the RayJoin Section 5.7 Polygon Overlay paper-reproduction
goal:

- use V4 / RTDL / Numba where appropriate;
- compare against the RayJoin author implementation;
- compare against the existing V2.14 exact-suite route where evidence exists;
- preserve the RayJoin workload instead of changing it after implementation
becomes hard.

This file records the current state after rereading the paper, rereading the
author code, rerunning the current POD setup probe, and checking the historical
RTDL evidence.

## Non-Negotiable Reproduction Contract

For a fair Section 5.7 reproduction, the intended change is only the
implementation stack:

| System | Stack |
|---|---|
| RayJoin author implementation | C++ / CUDA / OptiX |
| RTDL reproduction | Python / RTDL / RTDL-native OptiX / Numba continuation where measured |

This is a language/runtime substitution experiment, not an application redesign.
The correct question is:

> If the author wrote the same RayJoin Section 5.7 program with Python, RTDL,
> RTDL-native OptiX entry points, and Numba partner continuations instead of
> C++/CUDA/OptiX, can the workload preserve the same semantics and reach a
> competitive performance envelope?

Everything else must stay the same:

- same CDB input files;
- same Section 5.7 polygon overlay workload;
- same author parameters (`grid_size=15000`, `mode=rt`, `fau`,
  `xsect_factor=0.1`, `enlarge=3.5`, matching serialize prefix);
- same LSI and PIP decomposition;
- same fixed-point coordinate interpretation;
- same conservative AABB / CR precision obligation;
- same Simulation-of-Simplicity boundary behavior;
- same output-chain semantics and author-format output;
- same timing boundary for any direct performance comparison.

Changing any of these turns the row into a different experiment, not a fair
paper reproduction.

Concrete failure examples:

- replacing paper-preprocessed CDBs with same-source regenerated CDBs without
  labeling the row as `same_source_regenerated_cdb`;
- reporting only LSI, only PIP, or only a post-traversal continuation as full
  polygon-overlay performance;
- dropping the CDB face-adjacency contract and recomputing overlay polygons
  with a different topology model;
- ignoring the author's equal-height PIP tie-break behavior and accepting
  nondeterministic exterior/interior flips as "close enough."

## Paper And Author-Code Evidence Read

Paper:

- `C:/Users/Lestat/Downloads/ics24 (1).pdf`
- public copy checked at `https://gengl.me/public/publications/ics24.pdf`

Relevant paper obligations:

- Section 5.7 polygon overlay combines LSI and PIP.
- LSI casts query line segments as rays over `[tmin, tmax] = [0, 1]`.
- PIP casts a vertical ray upward from a query point and selects the closest
  boundary hit.
- Section 3.2 requires exact high-precision behavior despite FP32 RT traversal
  by using fixed-point scaled coordinates, conservative AABBs, rational
  intersection representation, and Simulation of Simplicity for degeneracies.

Author code read on the POD:

- author root: `/workspace/RayJoin_fresh`
- commit: `02bf6220d6d20b04af77ee20364eced75cc029c9`
- `git show HEAD:README.md`
- `git show HEAD:expr/run_overlay.sh`
- `git show HEAD:src/run_overlay.cu`
- `git show HEAD:src/app/map_overlay_rt.h`
- `git show HEAD:src/algo/rt_pip_custom.cu`
- `git show HEAD:src/app/output_chain.h`
- `git show HEAD:src/rt/primitive.h`

Important author-code details:

- `polyover_exec` runs map load, data load, initialization, BVH/index build,
  LSI, vertex PIP for both maps, midpoint PIP for output chains, output-chain
  construction, optional checking, and optional output writing.
- `expr/run_overlay.sh` runs the eight Section 5.7 overlay pairs from the
  expected `point_cdb/.../*_Point.cdb` layout.
- The README says RayJoin requires CDB input format, lists ArcGIS and
  SpatialHadoop/OSM source dataset links, describes the CDB generation flow,
  and still contains a preprocessed Dryad share link. It also states that
  preprocessed datasets are not currently provided. Therefore the README is
  useful for reconstructing the workload contract, but the current public link
  cannot be treated as proof that all eight paper-preprocessed CDB files are
  available on the POD.
- `misc/shp2cdb.py` is not a general polygon-to-CDB converter. It expects an
  ArcGIS `Polygon To Line` output shapefile whose features are `LineString`
  objects and already carry `LEFT_FID` / `RIGHT_FID` neighbor metadata. This
  means ordinary downloaded polygon shapefiles are not byte-equivalent Section
  5.7 inputs until the same topology-building preprocessing has been reproduced.
- `src/algo/rt_pip_custom.cu` implements the PIP closest-hit selection inside
  the custom intersection program. If two candidate edges have the same
  `xsect_y`, it compares edge slopes and flips the keep/discard condition by
  `query_map_id`. This is the deterministic rule that resolves the
  equal-height boundary cases observed in earlier diagnostics; an RTDL
  reproduction must preserve this behavior instead of relying on traversal
  order.
- `src/algo/rt_lsi_custom.cu` casts query segments with `tmin=0` and `tmax=1`
  and validates candidate base edges with the exact LSI predicate before
  appending intersections. A reproduction must keep that exact-test-after-RT
  structure.
- `src/app/map_overlay_rt.h` uses the LSI output, two vertex-PIP passes, and
  midpoint PIP during output-chain construction. Therefore a full Section 5.7
  comparison must include output-chain construction, not just the RT query
  phases.
- `src/config.h`, `src/algo/lsi.h`, and `src/app/map_overlay_rt.h` use scaled
  integer coordinates, `__int128`, and rational intersection values in the
  precision-sensitive parts. This is part of the paper's Section 3.2 contract,
  not an optional implementation detail.

The author working tree contains temporary Goal4806 debug instrumentation, so
the clean behavior must be read with `git show HEAD:<file>` when auditing source
semantics.

## Section 5.7 Paper Targets

The paper's Section 5.7 polygon overlay evaluation has eight rows. The author
script maps them to these CDB paths:

| Pair id | Base map | Query map | Expected CDB layout |
|---|---|---|---|
| `county_zipcode` | `dtl_cnty` | `USAZIPCodeArea` | `point_cdb/<map>/<map>_Point.cdb` |
| `block_water` | `USACensusBlockGroupBoundaries` | `USADetailedWaterBodies` | `point_cdb/<map>/<map>_Point.cdb` |
| `lkaf_pkaf` | `lakes/Africa` | `parks/Africa` | `point_cdb/lakes/Africa/lakes_Africa_Point.cdb`, `point_cdb/parks/Africa/parks_Africa_Point.cdb` |
| `lkas_pkas` | `lakes/Asia` | `parks/Asia` | same continent layout |
| `lkau_pkau` | `lakes/Australia` | `parks/Australia` | same continent layout |
| `lkeu_pkeu` | `lakes/Europe` | `parks/Europe` | same continent layout |
| `lkna_pkna` | `lakes/North_America` | `parks/North_America` | same continent layout |
| `lksa_pksa` | `lakes/South_America` | `parks/South_America` | same continent layout |

The paper's Table 4 reports RayJoin processing time and preprocessing time in
seconds:

| Pair | Paper RayJoin processing sec | Paper RayJoin preprocessing sec |
|---|---:|---:|
| County x Zipcode | `0.12` | `0.07` |
| Block x Water | `0.23` | `0.12` |
| LKAF x PKAF | `0.01` | `0.01` |
| LKAS x PKAS | `0.04` | `0.05` |
| LKAU x PKAU | `0.01` | `0.01` |
| LKEU x PKEU | `0.20` | `0.20` |
| LKNA x PKNA | `0.25` | `0.21` |
| LKSA x PKSA | `0.02` | `0.01` |

These paper numbers are targets/context, not direct speedup denominators. Any
release-grade comparison must run the author binary and the RTDL/V4 route on
the same POD, same CDB files, and same timing boundary.

## Current Strong Evidence: County x Zipcode

The County x Zipcode pair now has a full RTDL-native OptiX reproduction whose
overlay output is byte-equal to the author output.

Author output:

`/workspace/rtdl_goal4806_fast_min/artifacts/section57_author_output_debug/author_overlay_debug.overlay.txt`

RTDL output:

`/workspace/rtdl_goal4806_fast_min/artifacts/section57_same_source_county_zipcode_output_after_no_zero_length_correction_full/section57_overlay_county_zipcode_rtdl_after_no_zero_length_correction_full_optix.txt`

Observed equality:

```text
BYTE_EQUAL=1
  87758310 author_overlay_debug.overlay.txt
  87758310 section57_overlay_county_zipcode_rtdl_after_no_zero_length_correction_full_optix.txt
chain_count 29254027 face_count 115490 total_sec 459.2447640225291
midpoint_map1_corrections 0
```

This proves that the RayJoin Section 5.7 semantics can be reproduced by the
RTDL-native route for this pair when the language-swap contract is followed.

It does not prove a high-performance claim. The same run records:

| RTDL full-output phase | Seconds |
|---|---:|
| total | `459.2447640225291` |
| compute without load/pack | `403.3002147451043` |
| load/pack | `55.94454927742481` |
| output-chain assembly | `224.5616100281477` |
| output-chain write | `79.02145949751139` |
| LSI hot | `36.43369720131159` |
| vertex map0 hot | `4.490990467369556` |
| vertex map1 hot | `5.771099708974361` |
| midpoint map0 hot | `0.23856232315301895` |
| midpoint map1 hot | `0.24261629581451416` |

The author-code timing reference for the same pair records much faster full
overlay computation, with output writing itself taking about `132119 ms`.

## Current V4+Numba Candidate Evidence

The Numba CUDA toolchain issue was diagnosed as a toolkit/driver mismatch:

- the system NVVM emitted PTX 8.7;
- the POD driver accepted PTX up to 8.4;
- installing CUDA 12.4 NVCC/runtime Python packages into the venv made Numba
  emit PTX 8.4 successfully.

Pinned POD environment:

```bash
export CUDA_HOME=/tmp/rtdl_goal4806_venv/lib/python3.12/site-packages/nvidia/cuda_nvcc
export LD_LIBRARY_PATH=$CUDA_HOME/nvvm/lib64:$LD_LIBRARY_PATH
```

Measured candidate artifact:

`/workspace/rtdl_goal4806_fast_min/artifacts/goal4806_v4_numba_candidate_probe_after_byte_equal_cuda124/candidates_warmup1_repeat3.json`

County x Zipcode candidate rows:

| Candidate | Correctness | Hot-path host materialization | Steady-state sec | Selector status |
|---|---:|---:|---:|---|
| `v4_numba_post_traversal_segmented_counts` | pass | false | `0.01628301292657852` | selected |
| `v4_numba_post_traversal_mask_compact` | pass | true | `0.006718732416629791` | rejected |
| `v4_numba_post_traversal_lsi_stream_digest` | pass | false | `0.13609668612480164` | eligible but slower |

Planner import on the POD selected:

```text
claim_classification: candidate_stage_measured_no_app_speedup_claim
selected_plan: v4_numba_post_traversal_segmented_counts
rejection reason: host_materialization_in_hot_path_rejected
```

This is real V4+Numba candidate-stage evidence, not full polygon-overlay
performance evidence.

## Exact County x Zipcode Matrix Slice

After synchronizing the current Goal4806 tools to the POD, the Section 5.7
overlay matrix runner was executed for the exact County x Zipcode pair with
these selected implementations:

- `author_rt`
- `rtdl_optix`
- `v4_numba`

Local artifacts:

| Artifact | Purpose |
|---|---|
| `docs/reports/goal4806_section57_matrix_exact_county_summary_2026-06-30.md` | human-readable matrix slice |
| `docs/reports/goal4806_section57_matrix_exact_county_summary_2026-06-30.json` | machine-readable summary |
| `docs/reports/goal4806_section57_matrix_exact_county_run_2026-06-30.json` | run attempts and command evidence |

Observed matrix row:

| Pair | Local author RT process | RTDL OptiX total | V4+Numba total | V4+Numba status |
|---|---:|---:|---:|---|
| County x Zipcode | `19.547926s` | `92.031124s` | `0.016283s` | `candidate_stage_measured_no_app_speedup_claim` |

Interpretation:

- the selected matrix columns are complete for the exact County x Zipcode slice;
- the row is not full-control complete because Embree was not selected/run in
  this slice;
- the V4+Numba value is a measured post-traversal candidate-stage continuation,
  not full polygon-overlay performance;
- the current full RTDL OptiX route is correct for this pair, but slower than
  the local author RT process under this run.

## Current POD Readiness Audit

POD:

- host: `root@157.157.221.29 -p 23132`
- GPU: NVIDIA RTX 4000 Ada Generation
- RTDL tree: `/workspace/rtdl_goal4806_fast_min`
- author tree: `/workspace/RayJoin_fresh`
- dataset root checked: `/workspace/rayjoin_section57_same_source_cdb`

Fresh setup probe command:

```bash
cd /workspace/rtdl_goal4806_fast_min
source /tmp/rtdl_goal4806_venv/bin/activate
PYTHONPATH=src python scripts/rayjoin_section57_pod_setup.py \
  --author-root /workspace/RayJoin_fresh \
  --dataset-root /workspace/rayjoin_section57_same_source_cdb \
  --output-dir artifacts/goal4806_section57_setup_refresh_20260630 \
  --output-json artifacts/goal4806_section57_setup_refresh_20260630/setup.json
```

Fresh result:

- author source exists: yes;
- author commit: `02bf6220d6d20b04af77ee20364eced75cc029c9`;
- author binaries ready: yes (`query_exec`, `polyover_exec`);
- RT-core GPU ready: yes;
- exact Section 5.7 overlay inputs ready: `1 / 8`.

Only these CDB files exist on the POD:

```text
/workspace/rayjoin_section57_same_source_cdb/point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb
/workspace/rayjoin_section57_same_source_cdb/point_cdb/dtl_cnty/dtl_cnty_Point.cdb
```

Missing exact inputs:

| Pair | Missing CDB inputs |
|---|---|
| `block_water` | `USACensusBlockGroupBoundaries_Point.cdb`, `USADetailedWaterBodies_Point.cdb` |
| `lkaf_pkaf` | `lakes_Africa_Point.cdb`, `parks_Africa_Point.cdb` |
| `lkas_pkas` | `lakes_Asia_Point.cdb`, `parks_Asia_Point.cdb` |
| `lkau_pkau` | `lakes_Australia_Point.cdb`, `parks_Australia_Point.cdb` |
| `lkeu_pkeu` | `lakes_Europe_Point.cdb`, `parks_Europe_Point.cdb` |
| `lkna_pkna` | `lakes_North_America_Point.cdb`, `parks_North_America_Point.cdb` |
| `lksa_pksa` | `lakes_South_America_Point.cdb`, `parks_South_America_Point.cdb` |

The old Dryad preprocessed-data link was rechecked earlier and redirected to
`/404`. The author README also states that users may need to download the
source datasets and generate CDB files themselves.

The author repository contains saved experiment logs for all eight overlay
pairs under `expr/draw/overlay`, but those logs are not a substitute for the
missing CDB data. They can help interpret author-side timing, but they cannot
prove RTDL/V4 correctness or performance for the missing seven pairs.

The author RT logs copied from `/workspace/RayJoin_fresh/expr/draw/overlay`
contain the eight Section 5.7 processing rows. Summing
`Intersection edges + Map 0 PIP + Map 1 PIP + Computer output polygons`
reproduces the paper's RayJoin processing-time column:

| Author log | Approx preprocess sec (`Init + Build Index`) | Approx processing sec | Read sec | Load sec |
|---|---:|---:|---:|---:|
| `dtl_cnty_USAZIPCodeArea_rt.log` | `0.11` | `0.12` | `0.74` | `0.04` |
| `USACensusBlockGroupBoundaries_USADetailedWaterBodies_rt.log` | `0.16` | `0.23` | `1.66` | `0.06` |
| `lakes_parks_Africa_rt.log` | `0.09` | `0.01` | `0.16` | `0.00` |
| `lakes_parks_Asia_rt.log` | `0.13` | `0.04` | `0.60` | `0.03` |
| `lakes_parks_Australia_rt.log` | `0.11` | `0.01` | `0.13` | `0.00` |
| `lakes_parks_Europe_rt.log` | `0.21` | `0.20` | `2.56` | `0.11` |
| `lakes_parks_North_America_rt.log` | `0.19` | `0.25` | `2.37` | `0.11` |
| `lakes_parks_South_America_rt.log` | `0.10` | `0.02` | `0.23` | `0.01` |

These logs are useful author-side references. They still do not make a V4 row
complete unless the exact CDB data is present and the RTDL/V4 route is run.

## Data Acquisition Audit Added

To avoid leaving the project at a vague "missing data" statement, Goal4806 now
has a machine-readable data-acquisition audit:

`scripts/rayjoin_section57_data_acquisition_audit.py`

Generated artifacts:

- `docs/reports/goal4806_section57_data_acquisition_audit_current_2026-06-30.json`
- `docs/reports/goal4806_section57_data_acquisition_audit_network_2026-06-30.json`

The compact network audit reports:

- exact local `data/rayjoin_section57_cdb` coverage: `0 / 8`;
- current POD exact coverage from setup probe: `1 / 8`;
- Dryad preprocessed share: HTTP `404`, final URL `https://datadryad.org/404`;
- same-source regenerated route currently registered for only the two U.S.
  pairs:
  - `county_zipcode`;
  - `block_water`;
- six Lakes/Parks pairs have no registered same-source generator targets yet.

The four registered ArcGIS FeatureServer sources are live and match the stored
feature counts:

| Source | Observed count | Registry count | Status |
|---|---:|---:|---|
| USA Census Counties | `3144` | `3144` | live |
| USA ZIP Code Boundaries | `32294` | `32294` | live |
| USA Census Block Groups | `239203` | `239203` | live |
| USA Detailed Water Bodies | `463591` | `463591` | live |

This creates a concrete next engineering path for the U.S. 2/8 slice:

1. stage the four ArcGIS FeatureServer sources;
2. build a `same_source_regenerated_cdb` tree using the existing
   `build-arcgis-cdb-tree` command;
3. run County x Zipcode and Block x Water under the same Section 5.7 commands;
4. keep the claim boundary explicit: same-source regenerated CDBs are not
   recovered paper-preprocessed CDBs unless equivalence is proven separately.

It also clarifies the remaining 6/8 blocker: the Lakes/Parks continent pairs
need registered source targets and conversion before any all-eight-pair claim.

## U.S. Same-Source Block x Water Progress

The U.S. same-source route was then moved beyond smoke scale for the
`block_water` pair. On the POD, the full registered ArcGIS FeatureServer
sources were staged and converted to CDB:

| Target | Downloaded features | CDB bytes | CDB chains / segments | Nonzero faces |
|---|---:|---:|---:|---:|
| `blockgroup` | `239,203` | `3,146,767,020` | `28,473,338` | `239,203` |
| `waterbodies` | `463,591` | `2,402,941,772` | `22,431,809` | `463,512` |

Local artifacts:

| Artifact | Purpose |
|---|---|
| `docs/reports/goal4806_section57_arcgis_full_us_stage_block_water_2026-06-30.json` | full source staging manifest |
| `docs/reports/goal4806_section57_arcgis_full_us_build_block_water_2026-06-30.json` | CDB build stats |
| `docs/reports/goal4806_section57_arcgis_full_us_availability_2026-06-30.json` | availability after build |
| `docs/reports/goal4806_section57_rtdl_optix_same_source_block_water_2026-06-30.json` | RTDL OptiX run result |
| `docs/reports/goal4806_section57_matrix_same_source_block_water_rtdl_only_2026-06-30.md` | human-readable RTDL-only matrix slice |
| `docs/reports/goal4806_section57_matrix_same_source_block_water_rtdl_only_2026-06-30.json` | machine-readable RTDL-only matrix slice |

The generated `block_water` same-source CDB pair is runnable by the RTDL OptiX
overlay route:

| Metric | Value |
|---|---:|
| input provenance | `same_source_regenerated_cdb` |
| RTDL OptiX total | `367.23167979717255s` |
| load/pack | `303.9990338385105s` |
| compute without load/pack | `63.23264595866203s` |
| LSI intersections | `649,605` |
| map0 points in map1 PIP | `56,946,676` |
| map1 points in map0 PIP | `44,863,618` |
| map0 midpoint PIP | `131,495` |
| map1 midpoint PIP | `120,074` |

The same-source author-code run was also attempted with the same two generated
CDBs and the Section 5.7 flags, but it did not produce a phase/output JSON
within the interactive threshold. It was manually stopped after about 20
minutes of sustained CPU execution. Therefore there is still no valid local
author performance row for this generated `block_water` CDB pair.

This is still real progress: the second U.S. pair now has full same-source CDB
inputs and a completed RTDL OptiX route. It is not a paper-preprocessed
Section 5.7 performance claim, and it does not replace the missing exact
preprocessed CDBs.

### Block x Water Same-Source LSI Phase Probe

After the full same-source `block_water` run, a bounded LSI-only phase probe was
run against the author `query_exec` and the RTDL OptiX LSI route. This separates
first-load/serialization cost from the actual LSI query phase.

Artifacts:

| Artifact | Purpose |
|---|---|
| `docs/reports/goal4806_section57_phase_probe_same_source_block_water_author_lsi_2026-06-30.json` | first author LSI probe |
| `docs/reports/goal4806_section57_phase_probe_same_source_block_water_rtdl_optix_lsi_2026-06-30.json` | first RTDL LSI probe |
| `docs/reports/goal4806_section57_phase_probe_same_source_block_water_author_lsi_warm_2026-06-30.json` | warmed author LSI probe after `/dev/shm` serialization exists |
| `docs/reports/goal4806_section57_phase_probe_same_source_block_water_rtdl_optix_lsi_warm_2026-06-30.json` | warmed RTDL LSI probe |
| `docs/reports/goal4806_section57_phase_probe_same_source_block_water_rtdl_optix_lsi_stage_profile_2026-06-30.json` | RTDL LSI stage profile |
| `docs/reports/goal4806_section57_phase_probe_same_source_block_water_rtdl_optix_lsi_stage_profile_cached_2026-06-30.json` | RTDL LSI stage profile with packed cache enabled |
| `docs/reports/goal4806_section57_phase_probe_same_source_block_water_rtdl_optix_lsi_grouping_orientation_probe_2026-06-30.json` | grouping/orientation probe |
| `docs/reports/goal4806_section57_phase_probe_same_source_block_water_rtdl_optix_lsi_warm_after_default_grouping_2026-06-30.json` | RTDL LSI run after default grouped-range fix |

Observed same-source `block_water` LSI:

| Probe | Count | Total/elapsed sec | Author query ms | RTDL native traversal ms | Notes |
|---|---:|---:|---:|---:|---|
| Author first run | `649605` | `737.5520778596401` | `22.6698` | n/a | dominated by first load of map 1 from CDB: `718397 ms` |
| Author warmed run | `649605` | `27.812459461390972` | `22.6128` | n/a | maps deserialized from `/dev/shm`, but read/deserialization still totals about `25.6s` |
| RTDL first run | `649605` | `26.990751959383488` | n/a | `7.216254` | count matches author; wrapper hot path still spends about `26.79s` outside native traversal |
| RTDL warmed run | `649605` | `21.997184455394745` | n/a | `7.206304` | count matches author; wrapper hot path still spends about `21.80s` outside native traversal |
| RTDL warmed after default grouping fix | `649605` | `10.327529288828373` | n/a | `47.447443` | count still matches author; grouped range count drops to about `1.51M` |

Interpretation:

- correctness at the LSI count level matches exactly on this same-source
  regenerated `block_water` input (`649605`);
- the author's true RT query phase is tens of milliseconds, while elapsed time
  is dominated by CDB/deserialization overhead;
- RTDL's native traversal counter is also milliseconds, but the original
  Python wrapper/native-call boundary recorded tens of seconds in
  `hot_call_sec`;
- the first issue was not CDB parsing in the normal run path: with the packed
  cache environment enabled, packed input loading is sub-second;
- the concrete route bug was that the LSI exact-count front door defaulted to
  identity grouped ranges. The author-style grouped-range defaults
  (`max_size=32`, `area_enlarge=3.5`) preserve the correct count and cut the
  warmed RTDL LSI path from `21.997s` to `10.328s`;
- this remains `same_source_regenerated_cdb` evidence, not paper-preprocessed
  Section 5.7 evidence.

The corrected cached RTDL stage profile shows the current wall-time split:

| RTDL LSI stage | Seconds |
|---|---:|
| load base packed inputs | `0.2853436693549156` |
| load query packed inputs | `0.20857134461402893` |
| prepare query/right OptiX set | `6.7718124985694885` |
| prepare base/left OptiX set | `9.577194906771183` |
| native count and pair dump call | `5.957480549812317` |
| row array from pair dump | `0.3924281969666481` |
| total profiled wall | `23.19283116608858` |

The grouping/orientation probe then showed:

- keeping the current RTDL orientation is required for correctness
  (`649605`); swapping to the author orientation in the current generic route
  produced `649604`;
- enabling author-style grouped ranges on the current orientation reduced the
  right group count to `1510519` and the count wall time to about `4.13s`;
- after making those grouped-range defaults automatic in the RTDL LSI predicate
  context, the normal `run-rtdl` LSI path measured `10.3275s`.

This shows that the current V4/RTDL reproduction path still has one large
engineering cost center before it can be called a high-performance
language/runtime substitution: prepare/native wrapper setup is still seconds
around a millisecond-scale traversal. The route improved materially, but it is
not yet in the author's tens-of-milliseconds query envelope.

These are implementation/runtime problems, not reasons to change the Section
5.7 workload.

### Block x Water Same-Source Full-Output Summary Fast Path

After the initial full-output summary path completed in `303.278848s`, the
packed-input summary composer was specialized for the two-point-chain CDB shape
used by the generated U.S. same-source CDBs. The fast path completed within the
300 second bound and preserved the previously observed output summary counts.

Artifact:

`docs/reports/goal4806_overlay_block_water_full_output_fast_summary_300s_2026-06-30.json`

Trace:

`docs/reports/goal4806_overlay_block_water_full_output_fast_summary_300s_2026-06-30.jsonl`

Measurement-boundary rerun:

`docs/reports/goal4806_overlay_block_water_full_output_fast_summary_processing_boundary_300s_2026-06-30.json`

Measurement-boundary trace:

`docs/reports/goal4806_overlay_block_water_full_output_fast_summary_processing_boundary_300s_2026-06-30.jsonl`

Observed result:

| Metric | Value |
|---|---:|
| total | `197.54020334780216s` |
| load packed inputs | `2.7563903406262398s` |
| LSI row materialization | `6.926935590803623s` |
| LSI row sort | `25.281363859772682s` |
| point-location prepare | `65.21790799498558s` |
| output-chain summary assembly | `6.958222389221191s` |
| output chain count | `46,224,907` |
| face count | `2,581,524` |

This is real implementation progress: the same summary counts are produced, and
the output summary assembly component drops from `134.539783s` in the earlier
generic packed-array summary run to `6.958222s` in the two-point fast path.

The follow-up measurement-boundary rerun preserved the same summary counts and
added the explicit author-style processing/preprocessing split:

| Boundary metric | Value |
|---|---:|
| total | `223.7678336724639s` |
| native prepare total | `119.58403451740742s` |
| processing without load/pack or native prepare | `102.88588897138834s` |
| LSI prepare total | `34.930331490933895s` |
| point-location prepare wall | `84.65370302647352s` |
| output chain count | `46,224,907` |
| face count | `2,581,524` |

The total differs from the earlier `197.540203s` run because this is a separate
large POD execution with different prepare timing, but the output summary counts
match. The important new evidence is the boundary split: even after excluding
load/pack and native prepare, the current RTDL processing boundary is still
about `102.886s` on the generated `block_water` same-source pair, far outside
the author's reported Section 5.7 processing envelope.

The suite was then wired to use a prepared summary-output session when
`--assemble-overlay-output` is requested without an output file. This reuses the
packed inputs, the LSI prepared state, and the two point-location prepared
states across warmup/repeat runs. It does not change the RayJoin workload or the
summary output semantics; it changes the measurement boundary so that hot
processing can be measured separately from native prepare.

Prepared-session artifact:

`docs/reports/goal4806_overlay_block_water_prepared_summary_w1_r2_2026-06-30.json`

Observed prepared-session result (`warmup=1`, `repeat=2`):

| Metric | Value |
|---|---:|
| prepared packed-input load | `1.7698231264948845s` |
| native prepare total | `85.55640242248774s` |
| LSI prepare | `28.000225141644478s` |
| point-location prepare | `57.556091755628586s` |
| hot median total | `68.63220720365644s` |
| hot min / max | `68.34214404970407s` / `68.9222703576088s` |
| LSI row materialization median | `6.799069814383984s` |
| LSI row sort median | `25.09762617945671s` |
| output-chain summary assembly median | `7.110118988901377s` |
| output chain count | `46,224,907` |
| face count | `2,581,524` |

This is the current best `block_water` same-source summary-output hot boundary.
It is a meaningful improvement over the cold/boundary run, but it still does
not reach the author's Section 5.7 processing envelope. The next concrete
runtime gap is the Python row/object/sort path around LSI output: materialize
plus sort alone accounts for about `31.9s` of the `68.6s` hot median.

A post-release Goal4806 runtime-hardening candidate then changed the scaled LSI
sort key from full exact squared distance to exact distance along the dominant
edge axis. For intersections on a single segment, the dominant-axis distance is
monotonic with the segment parameter and preserves the same ordering while
avoiding a large fraction of Python `Fraction` arithmetic in the sorted
intersection view.

Axis-sort artifact:

`docs/reports/goal4806_overlay_block_water_prepared_summary_axis_sort_w1_r2_2026-06-30.json`

Observed result (`warmup=1`, `repeat=2`):

| Metric | Before axis-sort | After axis-sort |
|---|---:|---:|
| hot median total | `68.63220720365644s` | `60.297987304627895s` |
| hot min / max | `68.34214404970407s` / `68.9222703576088s` | `60.24182541668415s` / `60.35414919257164s` |
| LSI row materialization median | `6.799069814383984s` | `6.9644372425973415s` |
| LSI row sort median | `25.09762617945671s` | `16.121675919741392s` |
| output-chain summary assembly median | `7.110118988901377s` | `7.315004803240299s` |
| output chain count | `46,224,907` | `46,224,907` |
| face count | `2,581,524` | `2,581,524` |

This is a real runtime improvement on the same generated `block_water`
same-source workload: the hot summary boundary improves by about `1.14x`, and
the LSI sort component improves by about `1.56x`. It is still not a completed
RayJoin Section 5.7 high-performance claim. The remaining hot boundary is about
`60.3s`, and the row remains `same_source_regenerated_cdb` rather than exact
paper-preprocessed CDB input.

It is not a completed Section 5.7 high-performance claim. The row remains
`same_source_regenerated_cdb`, not recovered paper-preprocessed CDB input; it
does not write or byte-compare a full output file; and the full elapsed time is
still far outside the author's reported processing envelope. The remaining
dominant costs are point-location prepare, LSI row sorting/materialization, and
other Python/runtime orchestration overhead around the RT phases.

A follow-up POD probe tested the existing opt-in parallel PIP prepare switch:

```bash
RTDL_RAYJOIN_OVERLAY_OPTIX_PARALLEL_PIP_PREPARE=1
```

The probe reached the same LSI count (`649,605`) and sort stage, then failed
during point-location prepare with:

```text
RuntimeError: CUDA driver error: invalid device context
```

Trace artifact:

`/workspace/rtdl_goal4806_fast_min/artifacts/goal4806_overlay_block_water_full_output_fast_summary_parallel_prepare_300s.jsonl`

This closes Python-thread parallel prepare as a safe default optimization for
the current OptiX route. The two point-location acceleration structures must
remain serially prepared unless the native OptiX/CUDA context ownership model is
changed. The next useful target is a prepared full-output session and a lighter
LSI row/sort path, not another attempt to thread the current native prepare.

## U.S. Same-Source Staging Entry Point Added

The RayJoin paper reproduction suite now has a first-class staging command:

```bash
python scripts/rayjoin_paper_reproduction_suite.py stage-arcgis-sources \
  --staged-root artifacts/goal4806_section57_arcgis_stage/staged \
  --dataset-root artifacts/goal4806_section57_arcgis_stage/dataset \
  --targets county,zipcode,blockgroup,waterbodies \
  --gzip \
  --resume \
  --output-json artifacts/goal4806_section57_arcgis_stage/stage.json
```

For CI and planning, the dry-run command was executed:

```bash
python scripts/rayjoin_paper_reproduction_suite.py stage-arcgis-sources \
  --staged-root artifacts/goal4806_section57_arcgis_stage_plan_20260630/staged \
  --dataset-root artifacts/goal4806_section57_arcgis_stage_plan_20260630/dataset \
  --targets county,zipcode,blockgroup,waterbodies \
  --max-pages 1 \
  --dry-run \
  --output-json docs/reports/goal4806_section57_arcgis_stage_plan_dry_run_2026-06-30.json
```

Dry-run artifact:

`docs/reports/goal4806_section57_arcgis_stage_plan_dry_run_2026-06-30.json`

The staging command emits the next CDB-build command:

```bash
python scripts/rayjoin_paper_reproduction_suite.py build-arcgis-cdb-tree \
  --staged-root artifacts/goal4806_section57_arcgis_stage/staged \
  --dataset-root artifacts/goal4806_section57_arcgis_stage/dataset \
  --targets county,zipcode,blockgroup,waterbodies \
  --topology-mode polygon_to_line
```

Boundary: this route creates `same_source_regenerated_cdb` evidence. It is a
valid engineering route for testing RTDL/V4 on the same source families, but it
does not become `paper_preprocessed_cdb` evidence unless equivalence with the
paper-preprocessed files is separately proven.

The staging path has also been smoke-tested with one page per registered U.S.
source (`county`, `zipcode`, `blockgroup`, `waterbodies`). The smoke run
successfully staged source features, built CDB files, and made the two U.S.
same-source overlay rows available:

| Smoke artifact | Purpose |
|---|---|
| `docs/reports/goal4806_section57_arcgis_stage_smoke_stage_2026-06-30.json` | one-page source staging result |
| `docs/reports/goal4806_section57_arcgis_stage_smoke_build_cdb_tree_2026-06-30.json` | CDB build result from staged features |
| `docs/reports/goal4806_section57_arcgis_stage_smoke_availability_2026-06-30.json` | post-build availability matrix |

This proves the same-source acquisition/build machinery is real for the U.S.
2/8 slice. It still does not prove equivalence to the paper-preprocessed CDBs,
and it does not solve the six Lakes/Parks continent pairs.

## Why The Missing Seven Pairs Cannot Be Faked

The missing inputs are not just raw geometries. The CDB lines encode chain
identity, point ids, and neighboring face ids:

```text
<chain id> <number of points in the chain> <first point id> <last point id> <left face id> <right face id>
<point coordinates>
```

RayJoin's PIP and polygon-overlay output-chain logic use those left/right face
ids. Therefore, regenerating CDB inputs requires the same topology-preserving
preprocessing path, not merely downloading polygons and converting coordinates.
If the preprocessing differs, any performance or correctness row must be
classified as a new workload, not a Section 5.7 reproduction row.

## Historical V2.14 Evidence

Historical V2.14 Section 5.7 matrix:

`tools/_archive/history/legacy_project_archive_2026-06-24/docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/rayjoin_section57_overlay/section57_overlay_summary.json`

The archived summary itself reports:

```json
{
  "overlay_pairs_total": 8,
  "overlay_pairs_complete": 2,
  "overlay_pairs_incomplete": 6
}
```

Completed V2.14 rows:

| Pair | Author RT process sec | RTDL OptiX total sec | Output assembled? |
|---|---:|---:|---|
| `county_zipcode` | `5.521469049155712` | `5.7823397144675255` | no |
| `block_water` | `27.94386315345764` | `28.649871326982975` | no |

The V2.14 rows are valuable evidence that RTDL already had a strong LSI/PIP
Section 5.7 route on two pairs. They are not proof of full output-chain
byte-equality, and they are not proof of all-eight-pair completion.

## Current Completion Assessment

What is complete:

1. The fair reproduction contract has been re-derived from the paper and author
   code.
2. County x Zipcode full overlay correctness is proven by byte-equal output.
3. V4+Numba candidate-stage measurement is real and consumed by the planner.
4. The previous Numba PTX blocker is fixed in the pinned POD environment.
5. The POD current-state setup has been refreshed.
6. A machine-readable data-acquisition audit now separates exact input
   coverage, U.S. same-source regenerated coverage, and the missing Lakes/Parks
   source-target gap.
7. The same-source `block_water` LSI phase now has author and RTDL probe
   artifacts with matching intersection counts (`649605`), separating author
   query time from CDB/deserialization overhead.
8. The RTDL LSI route now auto-enables author-style grouped ranges for the
   RayJoin LSI predicate, reducing warmed same-source `block_water` RTDL LSI
   wall time from `21.997s` to `10.328s` without changing the workload or count.
9. The LSI phase runner now separates the author-style scalar LSI query from the
   row-producing overlay path. On same-source `block_water`, prepared scalar
   LSI count is stable at `649605` with hot median `0.047314s` over five measured
   repeats:

   `docs/reports/goal4806_section57_phase_probe_same_source_block_water_rtdl_optix_lsi_count_only_prepared_reuse_w1_r5_2026-06-30.json`

   The earlier row-producing path is still needed for full polygon overlay, but
   it is not the fair denominator for author `query_exec -query=lsi`.
10. A same-source `block_water` no-output overlay run with cached packed inputs
    records `106.628s` total and `105.930s` compute-without-load/pack:

    `docs/reports/goal4806_section57_phase_probe_same_source_block_water_rtdl_optix_overlay_no_output_after_lsi_no_scaled_materialization_2026-06-30.json`

    The phase breakdown moves the bottleneck away from scalar LSI count and
    toward overlay-level prepared state and PIP:

    | Phase | Seconds |
    |---|---:|
    | load/pack from packed cache | `0.6976` |
    | LSI native count pass | `0.0474` |
    | LSI pair dump/decode for overlay rows | `0.3995` |
    | LSI prepare total | `19.6310` |
    | point-location prepare total | `41.4364` |
    | vertex PIP map0 in map1 hot | `13.6606` |
    | vertex PIP map1 in map0 hot | `11.7898` |
    | midpoint projection | `0.6693` |
    | midpoint PIP total | about `0.1871` |

11. An attempted `RTDL_RAYJOIN_OVERLAY_OPTIX_PARALLEL_PIP_PREPARE=1` run failed
    with `CUDA driver error: invalid device context`, so parallel OptiX PIP
    prepare is not a safe immediate optimization path.
12. The no-output overlay runner now has a reusable prepared-session boundary:
    packed inputs, LSI prepared state, and point-location prepared states are
    built once, then query phases are repeated. On same-source `block_water`,
    `warmup=1 repeat=2` records query median `26.664861s`, separate prepare
    total `12.165601s`, and packed-input load `0.045159s`:

    `docs/reports/goal4806_section57_phase_probe_same_source_block_water_rtdl_optix_overlay_no_output_prepared_session_w1_r2_2026-06-30.json`

    This is the first RTDL overlay measurement boundary that is structurally
    close to the author's read/build/query timing split. It is still not a
    speed win.
13. Same-source `block_water` PIP had been the dominant measured performance
    gap, but the native OptiX reported-`t` bug has now been isolated and
    repaired. The bug was in RTDL's scaled CDB PIP intersection path: it kept
    exact scaled `hit_y` for Simulation-of-Simplicity ordering, which is
    correct, but it also reported the scaled y-distance to
    `optixReportIntersection()`. The RayJoin author code reports world-space
    y-distance after unscaling. Reporting scaled distance prevents OptiX's
    closest-hit `tmax` pruning from becoming tight, so traversal continues to
    visit many candidates that the author implementation prunes.

    | System / route | Query/hot median |
    |---|---:|
    | Author `query_exec -query=pip` | `0.0532861s` |
    | RTDL OptiX PIP count before fix | `11.814801s` |
    | RTDL OptiX PIP device-resident count before fix | `9.780761s` |
    | RTDL OptiX PIP device segment ids before fix | `9.773332s` |
    | RTDL OptiX PIP count after world-`t` fix | `2.206397s` |
    | RTDL OptiX PIP device-resident count after world-`t` fix | `0.097489s` |
    | RTDL OptiX PIP device segment ids after world-`t` fix | `0.097413s` |

    Author artifact:

    `docs/reports/goal4806_section57_phase_probe_same_source_block_water_author_pip_warm_2026-06-30.json`

    RTDL before-fix artifact:

    `docs/reports/goal4806_section57_phase_probe_same_source_block_water_rtdl_optix_pip_w1_r3_2026-06-30.json`

    RTDL after-fix artifact:

    `docs/reports/goal4806_section57_phase_probe_same_source_block_water_rtdl_optix_pip_after_world_t_fix_w1_r3_2026-06-30.json`

    The device-resident RTDL PIP hot path is now in the same order of magnitude
    as the author query (`97.5ms` vs `53.3ms`, about `1.83x` slower), rather
    than two orders of magnitude slower.
14. The same fix plus prepared-query-point and device-buffer reuse moved the
    same-source `block_water` no-output overlay prepared-session query from
    `26.664861s` to `1.204362s`. A follow-up no-output prepared-session
    optimization bypassed full structured LSI row materialization for the
    midpoint-only path: it reads the binary pair dump directly, computes
    intersection points once, and projects midpoint point inputs from those
    pair arrays under the same ordering rule.

    | Route | Query median |
    |---|---:|
    | RTDL prepared-session no-output overlay before PIP fix | `26.664861s` |
    | RTDL prepared-session no-output overlay after world-`t` fix only | `5.960462s` |
    | RTDL prepared-session no-output overlay after world-`t` + buffer reuse | `1.204362s` |
    | RTDL prepared-session no-output overlay after direct pair-dump midpoint projection | `0.872126s` |

    Artifacts:

    `docs/reports/goal4806_section57_phase_probe_same_source_block_water_rtdl_optix_overlay_no_output_after_world_t_and_buffer_reuse_prepared_session_w1_r2_2026-06-30.json`

    `docs/reports/goal4806_section57_phase_probe_same_source_block_water_rtdl_optix_overlay_no_output_after_direct_pair_dump_midpoint_prepared_session_w1_r2_2026-06-30.json`

    Current hot phase breakdown:

    | Phase | Seconds |
    |---|---:|
    | LSI count + direct pair-dump midpoint-input hot call | `0.591523` |
    | LSI candidate count pass | `0.047288` |
    | LSI binary pair-dump read | `0.005015` |
    | direct midpoint projection from pair arrays | `0.533242` |
    | vertex PIP map0 in map1 | `0.181091` |
    | vertex PIP map1 in map0 | `0.097520` |
    | midpoint PIP map0/map1 combined | about `0.0035` |

    The remaining no-output overlay bottleneck is no longer PIP traversal or
    pair-dump decode; it is direct midpoint projection plus the two vertex PIP
    traversals. Full output-chain assembly remains separate and still must be
    measured before any full Section 5.7 performance claim.
15. The same-source author `overlay_block_water` run was measured on the POD
    after the RTDL repair to keep a live author denominator in the report:

    `docs/reports/goal4806_section57_author_overlay_block_water_same_source_w0_r1_2026-06-30.json`

    The author run records these internal timings:

    | Author phase | Seconds |
    |---|---:|
    | Build Index | `0.079766` |
    | Intersection edges | `0.0270219` |
    | Compute output polygons | `0.0824549` |
    | Build + query + output-polygon compute subtotal | about `0.189243` |

    This means the repaired RTDL no-output prepared-session row (`0.872126s`)
    is much better than the previous RTDL row, but it is still about `4.6x`
    slower than the author's same-source build/query/output-polygon subtotal,
    and it still excludes full output-chain assembly/writing. It is progress,
    not completion.
16. A same-source `block_water` RTDL OptiX full-output probe was attempted after
    the direct midpoint optimization:

    ```text
    python scripts/rayjoin_paper_reproduction_suite.py run-rtdl \
      --dataset-root /workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630/dataset \
      --case-id overlay_block_water \
      --backend optix \
      --warmup 0 \
      --repeat 1 \
      --input-provenance same_source_regenerated_cdb \
      --assemble-overlay-output \
      --output-json /workspace/rtdl_goal4806_fast_min/artifacts/goal4806_overlay_block_water_full_output_probe_w0_r1_after_direct_midpoint.json
    ```

    The process was still running at about `9m15s` elapsed with about `97%` CPU
    and no output JSON, so it was terminated rather than treated as a completed
    measurement. A follow-up bounded trace probe with
    `RTDL_RAYJOIN_OVERLAY_PHASE_TRACE_PATH` timed out after `180s` with an empty
    trace file, proving it had not yet entered `_run_rayjoin_overlay_packed`.
    A direct `rt.load_cdb()` probe on the first `block_water` input also timed
    out after `180s` without finishing. The input sizes explain the blocker:
    `USACensusBlockGroupBoundaries_Point.cdb` is about `3.0GB` / `85,420,014`
    lines, and `USADetailedWaterBodies_Point.cdb` is about `2.3GB` /
    `67,295,427` lines.

    This was not a benchmark result, but it was useful blocker evidence at the
    time: the full-output path was blocked before the RTDL overlay kernel by the
    Python CDB object loader used by `assemble_output=True`. The next item shows
    the follow-up fix that moved this blocker.
17. That CDB-loader blocker has now been moved by routing
    `run_rayjoin_overlay_rtdl_from_cdb_paths(..., assemble_output=True)` through
    `load_cdb_overlay_packed_inputs()` and adding packed chain-offset / chain
    face-id metadata. The path can reuse the existing v1 packed cache for
    two-point CDB chains and assemble output chains from packed arrays instead
    of a giant Python `CdbDataset` object graph.

    Bounded probe artifact:

    `docs/reports/goal4806_overlay_block_water_full_output_phase_trace_packed_input_2026-06-30.jsonl`

    The new 180s full-output trace reached these phases before timeout:

    | Phase | Seconds / fact |
    |---|---:|
    | entered overlay packed path | yes |
    | map0 edges / points | `28,473,338` / `56,946,676` |
    | map1 edges / points | `22,431,809` / `44,863,618` |
    | LSI rows complete | reached |
    | LSI count native candidate pass | `0.047466s` |
    | full-output LSI pair dump + scaled row decode | `16.789326s` |
    | LSI row object materialize | `6.974969s` |
    | LSI row sort | `25.189023s` |

    This proves the first full-output blocker has moved. The new blocker is no
    longer CDB load; it is full-output scaled-intersection row materialization
    and Python object/sort work before point-location and output-chain assembly.
18. A follow-up 240s packed-input full-output trace moved one blocker further:

    `docs/reports/goal4806_overlay_block_water_full_output_phase_trace_packed_input_240s_2026-06-30.jsonl`

    It reached `output_chain_assembly_start` before timeout:

    | Phase | Seconds / fact |
    |---|---:|
    | LSI rows complete | reached |
    | full-output LSI pair dump + scaled row decode | `16.740619s` |
    | LSI row object materialize | `6.862886s` |
    | LSI row sort | `24.882513s` |
    | point-location prepare | `78.579130s` |
    | vertex PIP map0 rows | `5.383096s` |
    | vertex PIP map1 rows | `3.974163s` |
    | midpoint PIP map0 rows | `0.203953s` |
    | midpoint PIP map1 rows | `0.184290s` |
    | output-chain assembly | started, did not finish before 240s timeout |

    Therefore the next full-output blocker was explicit at this point: the Python
    output-chain assembly loop over tens of millions of CDB points/edges is not
    release-measurable. It needs a native/streaming output-chain composer or a
    bounded output-chain phase reducer before `block_water` can become a
    completed full-output timing row.
19. A 300s assembly-progress trace quantified that blocker:

    `docs/reports/goal4806_overlay_block_water_full_output_assembly_progress_300s_2026-06-30.jsonl`

    The run timed out with `EXIT_CODE=124` after reaching these assembly
    progress events:

    | Assembly progress | Value |
    |---|---:|
    | map index reached | `0` only |
    | map0 chains total | `28,473,338` |
    | last map0 chain index reached | `24,234,156` |
    | last point index reached | `48,468,312` |
    | output chains accumulated so far | `21,628,526` |

    So the packed full-output path got past input loading and all RT/PIP
    phases, but the materialized Python output-chain assembly could not complete
    the `block_water` row inside a 300s bounded probe and had not even started
    map1 by timeout. This is the blocker that the following summary composer
    reduces, but does not solve as a high-performance path.
20. A summary-only packed output-chain composer was then added for
    `assemble_output=True` with no `output_path`, matching the author's common
    no-output-file measurement boundary more closely than materializing every
    output-chain point in Python. This path still performs LSI, vertex PIP,
    midpoint PIP, and output-chain composition, but it returns `chain_count` and
    `face_count` without building the full point-id/output-file payload.

    Artifacts:

    `docs/reports/goal4806_overlay_block_water_full_output_summary_420s_2026-06-30.json`

    `docs/reports/goal4806_overlay_block_water_full_output_summary_420s_2026-06-30.jsonl`

    Result on same-source `block_water`:

    | Field | Value |
    |---|---:|
    | completed? | yes |
    | total sec | `303.278848` |
    | load packed inputs | `1.777121` |
    | LSI row object materialize | `7.012723` |
    | LSI row sort | `25.167172` |
    | point-location prepare wall | `53.911489` |
    | output-chain summary assembly | `134.539783` |
    | output chain count | `46,224,907` |
    | face count | `2,581,524` |
    | assembly input mode | `packed_arrays_summary_no_output_file` |

    This is an important completion step because the full-output summary row now
    finishes instead of timing out. It is also a negative performance result:
    it is nowhere near the author's same-source `Build Index + Intersection
    edges + Compute output polygons` subtotal of about `0.189243s`. The current
    RTDL path is correct in shape but dominated by Python-level full-output
    composition and cannot support a high-performance Section 5.7 claim.

What is not complete:

1. All eight Section 5.7 pairs are not runnable on the current POD because only
   County x Zipcode exact CDB inputs are present.
2. Full V4+Numba polygon overlay has not been proven faster than the author
   C++/CUDA/OptiX implementation.
3. Historical V2.14 evidence covers only two pairs and does not include full
   byte-equal output-chain proof.
4. Current RTDL full-output runtime for County x Zipcode is correct but slower
   than the author code, especially in output-chain assembly and writing.
5. Same-source regenerated CDB support currently covers only two U.S. pairs,
   not the six Lakes/Parks continent pairs.
6. The `block_water` scalar LSI phase now records `0.047314s` prepared-hot
   median versus the author same-source `query_exec -query=lsi` row's
   `0.0226128s` query phase. This is a meaningful reduction from the earlier
   mixed row-producing wrapper number, but it is still about `2.09x` slower
   than the author LSI query and therefore not a high-performance claim.
7. The no-output path no longer pays the full structured-row materialization
   cost: pair-dump read is now about `0.005s` in the direct midpoint projection
   row. The full-output path still needs structured intersections, sorted rows,
   midpoint owner assignment, and output-chain assembly, so that broader
   materialization/assembly bottleneck is not closed by the no-output fix.
8. The current overlay runner now has a reusable no-output prepared-session
   boundary matching the author's read/build/query timing separation more
   closely than the earlier CLI repeated-total row. It still does not cover
   full output-chain assembly/writing.
9. The new prepared-session overlay boundary fixes the repeated-call
   measurement issue, and the measured no-output overlay query is now
   `0.872s` on same-source `block_water`. This is a major improvement, but it
   is not a full polygon-overlay claim because output-chain assembly and output
   writing are excluded.
10. RTDL PIP is much closer to the author implementation after the world-`t`
    fix (`97.5ms` device-resident RTDL hot time versus `53.3ms` author query
    time), but it is still not faster than the author route and it has only
    been measured on same-source `block_water` plus the existing County x
    Zipcode correctness slice.
11. The first two full-output blockers have been moved enough to expose the
    next one: `assemble_output=True` now uses packed inputs, reaches the overlay
    path, completes LSI rows/sort, point-location prepare, vertex PIP, and
    midpoint PIP in the bounded trace. The row still must not be cited as a
    completed timing because it times out after `output_chain_assembly_start`.
    The new target is a native/streaming output-chain composer or bounded
    output-chain phase reducer.
12. Assembly progress tracing shows that the Python composer had processed
    `24,234,156 / 28,473,338` map0 chains and accumulated `21,628,526` output
    chains by the 300s timeout, without starting map1. A completed full-output
    row now depends on replacing this Python list/dict-heavy composer, not on
    more RT traversal tuning.
13. The packed summary composer completes the same-source `block_water`
    no-output-file output composition row in `303.279s`, with
    `134.540s` spent in output-chain summary assembly. This closes the timeout
    as an engineering blocker, but it opens the release blocker clearly: V4's
    current Python output-composition layer is orders of magnitude slower than
    the author C++ output-polygon phase.

Therefore Goal4806 is not complete as an all-eight-pair high-performance paper
reproduction. It is also not a failure of the language-swap principle: the first
full pair proves the semantics can match byte-for-byte, and the remaining broad
claim is blocked by missing exact inputs plus performance work. The current
engineering blocker has moved: it is no longer "PIP traversal is two orders of
magnitude slow"; it is now "RTDL no-output overlay composition still spends
about 0.53s projecting midpoint point inputs and about 0.28s in vertex PIP
traversal on same-source `block_water`; full output-chain assembly is not yet
part of the fast prepared-session row."

## Next Legitimate Actions

There are only six honest next paths:

1. Acquire or regenerate the missing seven pairs of exact CDB files, then run
   the all-eight Section 5.7 matrix under the same contract.
2. Close only the County x Zipcode slice after external review, explicitly
   saying that all-eight-pair Section 5.7 is still open.
3. Continue performance engineering on the `block_water` same-source prepared
   session, targeting direct midpoint projection and remaining vertex PIP
   traversal now that PIP `t` reporting and pair-dump decode have been repaired.
4. Replace or sharply reduce Python output-chain assembly for large packed
   Section 5.7 inputs, then rerun the bounded full-output trace and compare the
   completed row against the author overlay phases.
5. Continue performance engineering on the County x Zipcode full-output route,
   targeting output-chain assembly and write time before broader runs.
6. Use the now-live ArcGIS FeatureServer route to build and validate the U.S.
   same-source 2/8 slice, while keeping it out of `paper_preprocessed_cdb`
   claims until equivalence is proven.

What is not allowed:

- treating the Numba candidate-stage row as full overlay speedup;
- comparing to paper-table numbers instead of same-machine author-code rows;
- changing Section 5.7 semantics to make the implementation easier;
- calling 1/8 input coverage an all-eight-pair paper reproduction;
- using the old V2.14 2/8 matrix as if it were an all-eight-pair result.

## Goal-Level Decision Audit

Decision: do not mark Goal4806 complete; document current evidence and continue
or seek external review for the slice/blocker status.

1. Was I being stupid? Not if I preserve the full scope and refuse to inflate a
   1/8 slice into an 8/8 claim.
2. What would make the decision stupid? It would be stupid to hide the missing
   CDB inputs, cite the V4+Numba candidate as full overlay performance, or keep
   rerunning toy substitutes.
3. Is there another path? Yes: regenerate/acquire the exact missing CDB inputs,
   or formally close the County x Zipcode slice while keeping the full goal open.
4. Can I start a better path now? Yes: this report makes the current blocker
   auditable and points the next engineering work at exact data acquisition or
   County x Zipcode full-output performance engineering.
