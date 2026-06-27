# RayJoin Datasets In RTDL

RTDL Goal 2 adds a Python-side dataset pipeline for RayJoin-style CDB inputs before GPU runtime integration.

## Current Scope

The current dataset work is aimed at:

- parsing CDB chain files,
- deriving RTDL-friendly segment views,
- deriving point-probe views from chain starts,
- deriving polygon-reference views from face ids,
- and using tiny RayJoin-derived fixtures for repeatable local tests.

## RayJoin-Origin Sources

The prototype is aligned with the public RayJoin sample data:

- `br_county_clean_25_odyssey_final.txt`
- `br_soil_ascii_odyssey_final.txt`
- `br_countyXbr_soil_answer.txt`

These source URLs are tracked in `src/rtdsl/datasets.py`.

## In-Repo Test Fixtures

For local, deterministic tests, RTDL keeps tiny subsets extracted from the RayJoin sample data under:

- `tests/fixtures/rayjoin/br_county_subset.cdb`
- `tests/fixtures/rayjoin/br_soil_subset.cdb`

These are not intended to be representative benchmark datasets. They exist to validate:

- CDB parsing,
- chain-to-segment transformation,
- chain-to-point transformation,
- and face-based polygon-reference extraction.

## Limitations

This dataset pipeline does not yet reconstruct full topologically correct polygon faces from arbitrary CDB inputs. The current polygon-reference view is sufficient for compiler/dataflow work and CPU-side testing of workload plumbing, but not yet for a complete runtime-faithful polygon execution path.

That fuller reconstruction work should happen together with later runtime integration and stronger geometry validation.
