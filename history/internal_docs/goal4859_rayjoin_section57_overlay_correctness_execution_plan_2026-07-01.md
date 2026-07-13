# Goal4859: RayJoin Section 5.7 Overlay Correctness Execution Plan

Date: 2026-07-01

Depends on:

- Goal4858: `completed_section57_preflight__go_directly_to_57`

## Purpose

Attempt the first Section 5.7 polygon-overlay correctness run after the 5.4-5.6
dependency audit.  This is the next goal; it is not executed by Goal4858.

## First Dataset Pair

Start with:

`county_zipcode`

Reason:

- smallest serious U.S. Section 5.7 row with the most prior evidence;
- appears in the paper table;
- has prior Goal4380/Goal4816 evidence;
- exposes the real full-overlay path without immediately choosing the largest
  Block x Water row.

If exact CDB inputs are missing in the active execution environment, do not
silently substitute a regenerated dataset.  Record one of:

- `paper_preprocessed_cdb`;
- `historical_recovered_exact_cdb`;
- `same_source_regenerated_cdb`;
- `missing_input`.

## Author Command Template

Use AuthorPatch semantics and locked Section 5.7 parameters:

```bash
polyover_exec \
  -poly1 <dataset_root>/point_cdb/dtl_cnty/dtl_cnty_Point.cdb \
  -poly2 <dataset_root>/point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb \
  -serialize=/dev/shm \
  -grid_size=15000 \
  -mode=rt \
  -v=1 \
  -fau \
  -xsect_factor 0.1 \
  -enlarge=3.5 \
  -check=false \
  -output <author_overlay_output>
```

If the local AuthorPatch wrapper uses `scripts/rayjoin_paper_reproduction_suite.py`,
record the expanded command and the underlying `polyover_exec` command.

## RTDL Route Options

Goal4859 must choose and label one route.

### Preferred route: `generic_public_primitives_plus_app_layer`

Allowed:

- `load_cdb`;
- `chains_to_planar_map_segments`;
- `chains_to_planar_map_points`;
- `prepare_planar_map_lsi_2d_optix` for count checks;
- public segment-pair row/column APIs if they can provide intersection ids and
  coordinates without private bundled helpers;
- `prepare_planar_map_point_location_2d_optix`;
- Numba partner code for midpoint generation, row transforms, topology filters,
  and output-chain app logic.

Forbidden:

- importing or calling `rtdsl.rayjoin_overlay._run_lsi_rows`;
- importing or calling `rtdsl.rayjoin_overlay._run_point_location_faces`;
- importing or calling `rtdsl.rayjoin_overlay._assemble_output_chains`;
- calling `run_rayjoin_overlay_rtdl_from_cdb_paths` and labeling it generic;
- editing RTDL runtime/native code inside this goal.

If this route cannot obtain LSI rows/coordinates through public APIs, close the
route as:

`blocked_by_public_lsi_row_coordinate_surface_gap`

and do not fake success by switching to bundled helpers under the same label.

### Fallback route: `bounded_bundled_helper_reproduction`

Allowed only if explicitly labeled:

- `run_rayjoin_overlay_rtdl_from_cdb_paths(..., assemble_output=True, output_path=...)`

This proves a bounded shipped helper path, not that an ordinary user built the
app from generic primitives.

## Correctness Gate

Before timing:

1. Author output must exist.
2. RTDL output must exist.
3. Compare byte equality if formatting is expected to match.
4. If byte equality fails, compute a topology/chain diagnostic:
   - chain count;
   - total coordinate rows;
   - coordinate multiset hash;
   - first differing chain id and local point index;
   - whether mismatch is coordinate formatting, ordering, missing chain, or
     semantic topology.
5. No performance comparison is allowed unless correctness is either byte-equal
   or explicitly classified as a bounded topology-equivalent diagnostic.

## Performance Gate

Only after correctness:

- compare AuthorPatch and RTDL on the same machine;
- use same input provenance;
- record process wall vs hot/phase boundaries separately;
- report no broad RayJoin or RTDL performance claim from one pair.

## Expected Exit Labels

Allowed:

- `completed_section57_county_zipcode_byte_equal_generic_route`
- `completed_section57_county_zipcode_byte_equal_bundled_helper_route`
- `completed_section57_county_zipcode_topology_equivalent_diagnostic_only`
- `blocked_by_public_lsi_row_coordinate_surface_gap`
- `blocked_by_output_chain_app_logic_gap`
- `blocked_by_missing_exact_input`
- `blocked_by_authorpatch_build_or_runtime_gap`

The preferred successful label is:

`completed_section57_county_zipcode_byte_equal_generic_route`

but the most likely honest risk is:

`blocked_by_public_lsi_row_coordinate_surface_gap`

unless public row/coordinate APIs are sufficient.
