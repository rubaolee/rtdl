# Goal 143: Feature-Home Documentation

## Goal

Create one canonical documentation home per supported RTDL feature so readers
can quickly understand how to use that feature well.

## Required Outcome

- add `docs/features/<feature>/README.md` for each supported feature
- each feature home must include:
  - purpose
  - code
  - example
  - best practices
  - try / try not
  - limitations
- wire the feature homes into:
  - front-door docs
  - tutorials
  - language docs

## Supported Feature Set For This Goal

- `lsi`
- `pip`
- `overlay`
- `ray_tri_hitcount`
- `point_nearest_segment`
- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`
- `polygon_pair_overlap_area_rows`
- `polygon_set_jaccard`

## Acceptance

- there is a stable index at `docs/features/README.md`
- all listed feature homes exist
- high-level docs link to the feature homes
- live feature lists are updated so they match current supported features
