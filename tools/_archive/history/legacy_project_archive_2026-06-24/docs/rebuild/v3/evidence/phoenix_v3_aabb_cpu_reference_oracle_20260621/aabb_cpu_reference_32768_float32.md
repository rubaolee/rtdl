# Phoenix V3 AABB Chunked CPU Reference Oracle

Status: evidence oracle, not release authorization.

This artifact validates the large 32,768/32,768 AABB count-only row
with an independent chunked NumPy CPU oracle. It is not a product runtime
path and not LibRTS authors-code timing.

```text
status: pass
box_count: 32768
point_query_count: 32768
box_query_count: 32768
chunk_size: 256
elapsed_sec: 27.466513
```

## Counts

| Operation | Count | Matches expected |
| --- | ---: | --- |
| `point_contains` | 46,343,760 | `true` |
| `range_contains` | 32,302,908 | `true` |
| `range_intersects` | 70,429,254 | `true` |

## Boundary

- This closes the `cpu_reference_skipped_and_matches_reference_null` evidence gap for the exact large AABB row.
- It does not make the row paper-equivalent.
- It does not provide LibRTS authors-code timing.
- It does not authorize V3-over-V2 wording.
