---

## Findings

### Medium — `chains_to_polygon_refs`: `vertex_offset` is semantically wrong (`datasets.py:550`)

```python
for index, face_id in enumerate(sorted(faces), start=0):
    refs.append({"id": face_id, "vertex_offset": index, "vertex_count": faces[face_id]})
```

`vertex_offset` holds an ordinal position in the sorted-face enumeration, not an offset into any vertex buffer. Any caller treating it as a buffer index would get silently wrong geometry. Codex acknowledged this as "latent legacy API issue outside the 28C execution path" — that's accurate — but the function is still exported in `__init__.py:29` and carries a misleading field name. The 28C closure boundary is unaffected. Flag for the next dedicated cleanup goal.

---

### Low — `build_arcgis_geojson_query_url` is a no-op passthrough (`datasets.py:276-298`, `__init__.py:24-25`)

The function is an exact forwarding wrapper around `build_arcgis_query_url` with the same signature. It adds no logic and exports a second name for the same thing into the public API. Confusing but harmless.

---

### Low — Page-discovery sort logic duplicated (`datasets.py:391-394` vs `422-425`)

`load_arcgis_feature_pages` and `count_arcgis_loaded_pages` both repeat the same glob+sort block verbatim. A private helper would eliminate the drift risk. Not a correctness issue today.

---

### Low — Sort key tie for same-numbered `.json` and `.json.gz` pages (`datasets.py:392`)

```python
key=lambda path: path.name.replace(".gz", "")
```

If both `page_000000.json` and `page_000000.json.gz` coexist, the sort key is identical and their relative order is undefined (Python `sorted` is stable, but the glob concatenation order is OS-dependent). The test confirms mixed-extension ordering for distinct page numbers. Coexisting same-number pages don't arise in the current staging workflow, so this is a latent edge case only.

---

### Informational — Double page-read in converter script (`goal28c_convert_and_run_county_zipcode.py:122-147`)

County pages are read twice (once for the full conversion, once for the exec subset). Same for zipcode. At 28-page staging scale this is negligible. At full 32 000-feature zipcode scale it doubles disk I/O. Not a bug, just a scalability note for a future iteration.

---

### Resolved (no issue)

- Degenerate ring threshold raised to `< 3`: correct; 3-point triangle is the minimum meaningful closed ring.
- Mixed `.json`/`.json.gz` page ordering: correct and covered by `test_arcgis_loader_merges_json_and_gz_pages_in_page_order`.
- LSI zero-row result: the bounding-box explanation (Alabama vs Alaska) is complete and geometrically sound.
- PIP parity `True` (6 rows CPU = 6 rows Embree): clean.
- Report boundary statements accurately scope the closure.
- All four tests pass syntactically and the logic matches the implementation.

---

## Verdict

The 28C execution path is correct. The degenerate ring fix, page ordering fix, and LSI zero-row explanation all land cleanly. The remaining open item (`chains_to_polygon_refs.vertex_offset`) is correctly scoped outside the closure boundary and acknowledged. The other findings are minor quality notes that don't touch this goal's execution path.

**Approved with minor notes**
