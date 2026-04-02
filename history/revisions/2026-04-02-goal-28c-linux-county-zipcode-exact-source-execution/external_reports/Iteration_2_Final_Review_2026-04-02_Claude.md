---

**Findings ordered by severity**

---

**[Medium] `chains_to_polygon_refs` has a broken `vertex_offset` computation**
`datasets.py:544`

```python
for index, face_id in enumerate(sorted(faces), start=0):
    refs.append({"id": face_id, "vertex_offset": index, ...})
```

`vertex_offset` is set to the face enumeration index (0, 1, 2, …), not the cumulative vertex count of preceding faces. A packed polygon buffer requires `vertex_offset` to point to the first vertex of each face in the flat vertex array. Any consumer that passes this to Embree or CPU PIP via `pack_polygons` will get garbage offsets. The function is exported in `__init__.py` and `__all__` but is not on the execution path for this goal — the script uses `chains_to_polygons` instead. Latent but ships as broken public API.

---

**[Medium] Mixed `.json` / `.json.gz` page ordering is unstable**
`datasets.py:391-392` (same pattern repeated in `count_arcgis_loaded_pages:419-420`)

```python
page_paths = sorted(root_path.glob("page_*.json")) + sorted(root_path.glob("page_*.json.gz"))
```

All `.json` pages come first, all `.json.gz` pages come second, regardless of page number. A directory mixing both extensions (e.g., some pages saved uncompressed, others gzipped) would load out of order. The current staging run produces only `.json.gz`, so this doesn't affect Goal 28C, but it's a silent ordering hazard for future re-staging or mixed-format directories. Should be a single merged sort keyed by stem name.

---

**[Low] Degenerate ring filter threshold is `< 2`, not `< 3`**
`datasets.py:461`

```python
if len(ring) < 2:
    continue
```

A 2-vertex ring is a degenerate line segment and produces a `CdbChain` with `point_count=2`. The test data at `goal28c_conversion_test.py:23` includes a 3-vertex ring `[[5,5],[6,5],[5,5]]` (first == last, net zero area) that passes through and produces a chain. Neither is a meaningful polygon. The threshold should be `< 3` (or `< 4` following ArcGIS convention that closed rings duplicate the first vertex). Non-blocking for this goal since the actual ArcGIS source rings are well-formed, but the code accepts and forwards degenerate geometry silently.

---

**[Low] LSI 0-row result is unexplained in the report**
`docs/reports/…_2026-04-02.md`, Results section

CPU and Embree both returned 0 LSI pairs in 3.6 s and 1.4 s respectively. The report declares parity=True but offers no note on why the chosen 1-county / 1-zipcode feature pair produces no segment intersections. A one-sentence note — e.g., that the first county feature and first zipcode feature selected by `OBJECTID` order are non-overlapping or spatially separated — would close the interpretive gap. Without it, a reader cannot distinguish "expected zero because geometries don't overlap" from "zero because execution is broken."

---

**[Low] Test suite is thin on the new API surface**
`tests/goal28c_conversion_test.py`

3 tests cover: ring-to-chain conversion, `chains_to_polygons`, invalid-tail skip. Missing:
- `write_cdb` / `load_cdb` round-trip (point precision, header format)
- `slice_cdb_dataset` (max_faces boundary behaviour — the `not filtered` guard on line 377 allows one over-limit chain)
- `chains_to_segments` (segment count vs point count)
- `chains_to_probe_points` (returns first point, not a guaranteed interior point)

Not a closure blocker but leaves the new helpers undertested.

---

**Verdict**

Closure boundary is met. All five required items are present and correctly described:

- Full USCounty exact-source conversion: 3144 features, 12273 chains, confirmed.
- Staged-checkpoint Zipcode conversion: 7000 features (invalid tail page correctly dropped), confirmed.
- First feature-limited Linux lsi/pip execution slice: executed on 192.168.1.20, confirmed.
- CPU vs Embree parity: LSI parity=True, PIP parity=True, confirmed.
- Report language on partial Zipcode input and chain-derived polygon approximation: explicit in both the design-rule section and the boundary section, confirmed.

The `chains_to_polygon_refs` bug is real but outside this goal's execution path. The page-ordering hazard is real but inert for the current all-gzip staging layout. Neither blocks the declared scope.

**Approved with minor notes**
