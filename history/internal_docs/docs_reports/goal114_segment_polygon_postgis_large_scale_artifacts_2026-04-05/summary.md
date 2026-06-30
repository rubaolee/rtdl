# Goal 114 Segment/Polygon PostGIS Validation Summary

- Generated: `2026-04-05T23:55:01`
- Dataset: `derived/br_county_subset_segment_polygon_tiled_x256`
- Segments: `2560`
- Polygons: `512`
- Host: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- PostGIS: `0.050334 s`, rows `2560`

| Backend | Time (s) | Row Count | Parity vs PostGIS | SHA256 |
| --- | ---: | ---: | --- | --- |
| `cpu` | 0.581763 | 2560 | `True` | `ad4265f181053e2f181b0e6b7e6bdd4379e1ec59e4d58581be0d6f61fb0fd099` |
| `embree` | 0.588157 | 2560 | `True` | `ad4265f181053e2f181b0e6b7e6bdd4379e1ec59e4d58581be0d6f61fb0fd099` |
| `optix` | 0.389946 | 2560 | `True` | `ad4265f181053e2f181b0e6b7e6bdd4379e1ec59e4d58581be0d6f61fb0fd099` |
