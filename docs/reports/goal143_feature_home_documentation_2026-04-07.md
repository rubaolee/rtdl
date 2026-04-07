# Goal 143 Report: Feature-Home Documentation

## Result

Goal 143 is closed.

The repo now has one canonical documentation home per supported RTDL feature
under:

- [docs/features/README.md](/Users/rl2025/rtdl_python_only/docs/features/README.md)

Added feature homes:

- [LSI](/Users/rl2025/rtdl_python_only/docs/features/lsi/README.md)
- [PIP](/Users/rl2025/rtdl_python_only/docs/features/pip/README.md)
- [Overlay](/Users/rl2025/rtdl_python_only/docs/features/overlay/README.md)
- [Ray/Triangle Hit Count](/Users/rl2025/rtdl_python_only/docs/features/ray_tri_hitcount/README.md)
- [Point/Nearest Segment](/Users/rl2025/rtdl_python_only/docs/features/point_nearest_segment/README.md)
- [Segment/Polygon Hit Count](/Users/rl2025/rtdl_python_only/docs/features/segment_polygon_hitcount/README.md)
- [Segment/Polygon Any-Hit Rows](/Users/rl2025/rtdl_python_only/docs/features/segment_polygon_anyhit_rows/README.md)
- [Polygon-Pair Overlap Area Rows](/Users/rl2025/rtdl_python_only/docs/features/polygon_pair_overlap_area_rows/README.md)
- [Polygon-Set Jaccard](/Users/rl2025/rtdl_python_only/docs/features/polygon_set_jaccard/README.md)

Each feature home now includes:

- purpose
- docs
- code
- example
- best practices
- try / try not
- limitations

## High-Level Doc Integration

The new feature homes were linked into:

- [README.md](/Users/rl2025/rtdl_python_only/README.md)
- [docs/README.md](/Users/rl2025/rtdl_python_only/docs/README.md)
- [docs/quick_tutorial.md](/Users/rl2025/rtdl_python_only/docs/quick_tutorial.md)
- [docs/rtdl/README.md](/Users/rl2025/rtdl_python_only/docs/rtdl/README.md)
- [docs/rtdl_feature_guide.md](/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md)
- [docs/v0_2_user_guide.md](/Users/rl2025/rtdl_python_only/docs/v0_2_user_guide.md)
- [docs/rtdl/workload_cookbook.md](/Users/rl2025/rtdl_python_only/docs/rtdl/workload_cookbook.md)
- [docs/rtdl/programming_guide.md](/Users/rl2025/rtdl_python_only/docs/rtdl/programming_guide.md)
- [docs/rtdl/dsl_reference.md](/Users/rl2025/rtdl_python_only/docs/rtdl/dsl_reference.md)

## Important Corrections

This goal also repaired live doc drift:

- the high-level feature lists now include:
  - `segment_polygon_anyhit_rows`
  - `polygon_pair_overlap_area_rows`
  - `polygon_set_jaccard`
- the language docs now name the narrow Jaccard line as part of the current
  implemented surface

## Honest Boundary

These feature homes are documentation homes, not claims of equal maturity.

The limitation sections keep the accepted boundaries explicit:

- `overlay` remains an overlay-seed workload
- the Jaccard line remains narrow and unit-cell/pathology-oriented
- Linux remains the primary validation platform for the strongest v0.2 evidence
