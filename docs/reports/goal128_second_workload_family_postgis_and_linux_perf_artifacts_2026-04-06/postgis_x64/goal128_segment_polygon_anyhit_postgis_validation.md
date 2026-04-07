# Goal 128 Segment/Polygon Any-Hit Rows PostGIS Validation Summary

- Generated: `2026-04-06T20:51:17`
- Dataset: `derived/br_county_subset_segment_polygon_tiled_x64`
- Segments: `640`
- Polygons: `128`
- Host: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- PostGIS: `0.003241 s`, rows `704`

| Backend | Time (s) | Row Count | Parity vs PostGIS | SHA256 |
| --- | ---: | ---: | --- | --- |
| `cpu` | 0.010849 | 704 | `True` | `e97b0f49c4a5f024bdda672737ddd83c88a05f054ce0486919af3b9a6edf6210` |
| `embree` | 0.010000 | 704 | `True` | `e97b0f49c4a5f024bdda672737ddd83c88a05f054ce0486919af3b9a6edf6210` |
| `optix` | 0.006234 | 704 | `True` | `e97b0f49c4a5f024bdda672737ddd83c88a05f054ce0486919af3b9a6edf6210` |
| `vulkan` | 0.003213 | 704 | `True` | `e97b0f49c4a5f024bdda672737ddd83c88a05f054ce0486919af3b9a6edf6210` |
