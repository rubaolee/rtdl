# Goal 150 v0.2 Release Readiness And Stability

## Verdict

Frozen v0.2 is stable enough to continue release shaping.

Current `main` is not yet the final v0.2 release artifact, but the accepted
v0.2 surface is now in a state where more feature growth would add less value
than a final release package.

## Scope Checked

Frozen workload surface:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

Plus:

- narrow generate-only
- feature-home docs
- release-facing example layer

## Current Readiness Result

Accepted statement:

- frozen v0.2 is functionally stable on current `main`
- Linux remains the primary validation platform
- this Mac remains a limited local platform
- the Jaccard line remains accepted only with its narrow pathology/unit-cell
  contract and documented fallback-vs-native boundary

Not claimed:

- that this Mac is a whole-platform closure host
- that Jaccard has native Embree, OptiX, or Vulkan kernels
- that `main` is already the final tagged v0.2 release

## Fresh Evidence

### Local Mac

Compile smoke:

- `python3 -m compileall examples/rtdl_segment_polygon_hitcount.py examples/rtdl_segment_polygon_anyhit_rows.py examples/rtdl_polygon_pair_overlap_area_rows.py examples/rtdl_polygon_set_jaccard.py scripts/rtdl_generate_only.py`
  - `OK`

Frozen local matrix:

- `PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group v0_2_local`
  - `28` tests
  - `OK`
  - `3` skipped
  - `geos_c` linker warnings still appear in skipped environment-bounded rows

Feature-home audit:

- `python3 scripts/goal147_doc_audit.py`
  - `feature_home_count = 9`
  - `all_feature_sections_present = true`
  - `all_top_level_docs_link_feature_homes = true`

Release-surface audit:

- `python3 scripts/goal149_release_surface_audit.py`
  - `all_docs_link_release_examples = true`
  - `all_examples_exist = true`
  - `release_example_doc_has_no_machine_local_links = true`

Release-facing example smoke:

- `segment_polygon_hitcount`
  - backend `cpu_python_reference`
  - dataset `derived/br_county_subset_segment_polygon_tiled_x16`
  - `row_count = 160`
- `segment_polygon_anyhit_rows`
  - backend `cpu_python_reference`
  - dataset `derived/br_county_subset_segment_polygon_tiled_x16`
  - `row_count = 176`
- `polygon_pair_overlap_area_rows`
  - `2` overlap rows
  - rows:
    - `(left=1, right=10, intersection=4, union=14)`
    - `(left=2, right=11, intersection=1, union=5)`
- `polygon_set_jaccard`
  - `intersection_area = 5`
  - `left_area = 13`
  - `right_area = 11`
  - `union_area = 19`
  - `jaccard_similarity = 0.2631578947368421`
- `generate_only`
  - handoff bundle generated for `polygon_set_jaccard`
  - manifest:
    - `build/generated_polygon_set_jaccard_bundle_goal150/request.json`

### Linux Primary Platform

Fresh clean-checkout host:

- `lestat@192.168.1.20`
- clean temporary clone at commit `4272bb7`

Frozen Linux matrix:

- `PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group v0_2_full`
  - `36` tests
  - `OK`
  - `3` skipped

Focused Jaccard slice:

- `PYTHONPATH=src:. python3 -m unittest tests.goal146_jaccard_backend_surface_test tests.goal140_polygon_set_jaccard_test tests.goal138_polygon_pair_overlap_area_rows_test`
  - `13` tests
  - `OK`

Linux example / generate-only smoke:

- `PYTHONPATH=src:. python3 examples/rtdl_polygon_set_jaccard.py`
  - same authored result as local:
    - `intersection_area = 5`
    - `left_area = 13`
    - `right_area = 11`
    - `union_area = 19`
    - `jaccard_similarity = 0.2631578947368421`
- `PYTHONPATH=src:. python3 scripts/rtdl_generate_only.py --workload polygon_set_jaccard --dataset authored_polygon_set_jaccard_minimal --backend cpu_python_reference --output-mode rows --artifact-shape handoff_bundle --output build/generated_polygon_set_jaccard_bundle_goal150`
  - bundle generated successfully

Fresh several-second Linux Jaccard row:

- `PYTHONPATH=src:. python3 scripts/goal146_jaccard_linux_stress.py --copies 64 --output-dir build/goal150_goal146_stress_x64`
  - source: `MoNuSeg 2018 Training Data`
  - selected nuclei: `16`
  - left polygons: `547584`
  - right polygons: `547584`
  - Python: `8.264004 s`
  - CPU: `4.115949 s`
  - Embree: `3.899038 s`
  - OptiX: `3.881174 s`
  - Vulkan: `3.873838 s`
  - consistency vs Python:
    - CPU `true`
    - Embree `true`
    - OptiX `true`
    - Vulkan `true`
  - `jaccard_similarity = 0.917956`

## Interpretation

The frozen v0.2 package is now in the right state for release shaping:

- the frozen local and Linux matrices still pass
- the release-facing examples still run
- generate-only still works on the accepted narrow surface
- the feature-home and release-surface doc layers are aligned
- the several-second Linux Jaccard line remains consistent across the public
  backend run surfaces

The most important remaining boundary is unchanged:

- the Jaccard line is not a native Embree/OptiX/Vulkan maturity story
- it is a narrow workload line with documented native CPU/oracle fallback under
  those public run surfaces

## Remaining Work Before Final v0.2 Release

- front-door status wording freeze
- final release statement
- final support/readiness note
- final tagged release packaging
