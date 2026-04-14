# Goal 360 Report: v0.6 real-data bounded triangle-count eval

## Summary

`v0.6` now has a first bounded real-data `triangle_count` result on `SNAP wiki-Talk`.

The result is intentionally bounded:
- edge-capped
- transformed to a simple undirected graph
- parity-focused
- Linux/PostgreSQL-backed

## Current bounded real-data triangle-count fact

Dataset:
- `SNAP wiki-Talk`

Transform:
- simple undirected
- self-loops dropped
- canonical undirected edges deduped

Bound:
- first `50000` canonical undirected edges

Linux result:

| backend | seconds | parity |
| --- | ---: | --- |
| Python | `12.45560523896711` | truth path |
| oracle | `0.3653613229980692` | `true` |
| PostgreSQL | `2.510055066959467` | `true` |

## Interpretation

This is enough to say:
- `triangle_count` now has a bounded real-data path
- RTDL compiled CPU/oracle matches the Python truth path
- the bounded PostgreSQL baseline also matches

This is **not** enough to say:
- full `wiki-Talk` triangle-count closure
- large-scale paper evaluation
- final graph-performance ranking
