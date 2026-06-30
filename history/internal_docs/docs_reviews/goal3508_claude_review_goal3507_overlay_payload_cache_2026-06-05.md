# Goal3508 — Claude Independent Review of Goal3507 Overlay Prepared Payload Cache

**Review date:** 2026-06-05
**Reviewer:** Claude Sonnet 4.6 (independent, read-only)
**Verdict:** `accept-with-boundary`

---

## Files Reviewed

- `src/rtdsl/v2_8_overlay_area_prepared_payload.py` — serialization/deserialization functions
- `src/rtdsl/__init__.py` — public API exports
- `scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py` — cache write/read paths
- `tests/goal3507_overlay_area_prepared_payload_cache_test.py` — cache test coverage
- `tests/goal3502_overlay_area_single_triangulation_payload_construction_test.py` — prior serialization baseline
- `docs/reports/goal3507_overlay_area_prepared_payload_cache_2026-06-05.md` — author report
- `docs/reports/goal3507_overlay_area_prepared_payload_cache_write_pod_2026-06-05.json` — write artifact
- `docs/reports/goal3507_overlay_area_prepared_payload_cache_read_pod_2026-06-05.json` — read artifact

---

## Question 1: Generic payload serialization without app-specific native engine logic

**Finding: Confirmed — no app-specific native engine logic.**

The JSON cache path (`_write_prepared_payload_cache` / `_read_prepared_payload_cache`,
executor lines 324–468) serializes exactly three things: (a) the generic prepared
component payload via `rt.prepared_simple_polygon_component_payload_to_dict`, which
serializes triangle float64 tuples and component metadata; (b) the `shape_to_components`
mapping (shape ordinal → component ordinal list); and (c) the WKB hex strings for each
shape's repaired Shapely geometry (needed by the exact oracle, not by the native engine).
No CUDA state, OptiX handle, or device buffer is serialized.

The serialization functions themselves (`prepared_simple_polygon_component_payload_to_dict`,
`prepared_simple_polygon_component_payload_from_dict`, and their numpy column equivalents)
live entirely in `v2_8_overlay_area_prepared_payload.py` and carry explicit contract fields:
`app_specific_engine_logic_allowed: False`, `automatic_partner_selection_allowed: False`.
None of the CuPy kernels, kernel strings, or tile-task planning logic is touched by
the cache write or read path.

The only design note: the JSON cache contains `geometry_wkb_hex` entries alongside the
prepared triangles. These are stored for the exact Shapely oracle path and are not
consumed by the native engine. The duplication is intentional and correctly scoped.

---

## Question 2: Read mode avoids rebuild work; evidence supports 1.441s → 0.355s

**Finding: Confirmed — read mode avoids all geometry repair and triangulation.**

When `payload_cache_mode == "read"`, the executor branches exclusively into
`_read_prepared_payload_cache` (executor line 629–672). It sets `geometry_build_sec = 0.0`,
`payload_build_sec = 0.0`, and `parallel_payload_prepare_used = False` explicitly.
The `geometry_plus_payload_prepare` timing is aliased to `payload_cache_load_sec`
at executor line 1067–1072, making the accounting unambiguous.

The read artifact confirms:
```
geometry_build: 0.0
payload_build: 0.0
parallel_geometry_payload_prepare: 0.0
payload_cache_load: 0.355s
geometry_plus_payload_prepare: 0.355s  (equals payload_cache_load exactly)
```

The test at goal3507 test line 96–99 mechanically verifies this equality:
`read_data["timing_sec"]["geometry_plus_payload_prepare"] ==
read_data["timing_sec"]["payload_cache_load"]`.

The `1.441s → 0.355s` claim is cross-run: `1.441s` is Goal3505's best 8-worker parallel
rebuild on the same pod/dataset, and `0.355s` is Goal3507's cache-read time. The write-mode
refresh run in this goal shows `1.607s` (within normal run-to-run variability of
±15% for the parallel-process path). The comparison is correctly labeled as Goal3505
baseline vs Goal3507 cache read, and the report does not claim the improvement comes
from the refresh run itself.

The **4.07x** preparation-stage speedup (1.441s → 0.355s) is defensible for this pod and
dataset. Single-run timing is sufficient evidence for a caching win because the claim is
about load vs. rebuild cost, not about a kernel execution floor.

---

## Question 3: Correctness unchanged between write and read artifacts

**Finding: Confirmed — identical results across all correctness metrics.**

Direct comparison of the two JSON artifacts:

| Metric | Write (refresh) | Read |
|---|---|---|
| `total_area_abs_error` | `9.2278e-09` | `9.2278e-09` |
| `max_relation_abs_error` | `1.0414e-09` | `1.0414e-09` |
| `exact_positive_row_count` | 1086 | 1086 |
| `observed_positive_row_count` | 1086 | 1086 |
| `positive_row_count_match` | true | true |
| `relation_row_count` | 4543 | 4543 |
| `supported_relation_row_count` | 2149 | 2149 |
| `planned_triangle_pair_count` | 4,070,240 | 4,070,240 |
| `left_payload_triangle_count` | 41,178 | 41,178 |
| `right_payload_triangle_count` | 32,087 | 32,087 |
| `tile_task_count` | 11,617 | 11,617 |

The `largest_error_rows` differ in `relation_row` ordinal values (e.g., write row 522
vs. read row 540 for the same left_ordinal=384 / right_ordinal=143 pair). This is
expected: OptiX-based relation discovery produces a non-deterministic row ordering
between runs. The same shape pairs appear at the same error magnitudes — correctness
is confirmed.

The test at goal3507 test lines 69–89 mechanically enforces equality for all ten
structural count keys and the error thresholds.

---

## Question 4: Claim boundaries correct and conservative

**Finding: Confirmed — all prohibited claims are false in both artifacts and in code.**

Both JSON artifacts carry:
```json
"claim_boundary": {
    "full_overlay_area_claim_authorized": false,
    "public_speedup_claim_authorized": false,
    "rayjoin_paper_reproduction_claim_authorized": false,
    "release_authorized": false,
    "rt_core_speedup_claim_authorized": false,
    "rtdl_beats_rayjoin_claim_authorized": false,
    "true_zero_copy_claim_authorized": false
}
```

The test at goal3507 test lines 101–104 enforces that every claim boundary field is
`false` for both the write and read artifacts. The serialization functions in
`v2_8_overlay_area_prepared_payload.py` embed the same `claim_boundary` fields in
every output dict and metadata block (lines 881–885, 539–543, 644–648, etc.).

The author's report accurately states the cache is "host-side JSON/WKB reuse" and
does not attempt any of the seven prohibited claims. No boundary violation was found.

---

## Question 5: Design risks before the next step

Five risks are worth noting explicitly.

**Risk 1 — No content fingerprint for stale-cache detection (medium).**
The cache validates `source_cdb` path string and `selected_shape_ordinals` set
(executor lines 438–443 for JSON; 399–403 for binary). It does not hash the CDB
file content or verify that the Shapely-repaired geometry is reproducible. If the
CDB file at the same path is replaced with different geometry, the cache silently
serves stale triangles and the error will be invisible until a comparison run. For
the current controlled research workflow this is acceptable, but the risk should be
stated before any broader use.

**Risk 2 — JSON cache size is large (low severity, known).**
The write pod spends 1.356s serializing the JSON cache. Left side alone has 41,178
triangles × 6 float64 coordinates stored as text strings, plus 3,117 component
records, plus WKB hex blobs. The resulting files are likely 50–100MB range. The
binary/npz path (`--payload-cache-format binary`, Goal3509) addresses this.

**Risk 3 — Path-based validation is machine-specific (low severity).**
`source_cdb` is stored as an absolute path string (e.g., `/root/rtdl/data/...`).
Moving the cache to a different machine with a different mount point fails the
validation check unconditionally. A relative-path or content-hash scheme would
be more portable, but this is a benchmark tool, not a production artifact.

**Risk 4 — WKB duplication in JSON format (known, intentional).**
The JSON cache serializes both the prepared triangle columns and the WKB blobs of
the repaired Shapely geometries. The WKBs are needed to avoid repeating Shapely
geometry repair on cache reads (the exact oracle also needs the repaired geometry).
The duplication is correct but contributes to cache size; it is clearly labeled
and not accidentally redundant.

**Risk 5 — Gap between host file-cache and true device-resident persistence
(correctly scoped).**
The cache reduces the preparation stage from 1.44s to 0.35s by skipping geometry
repair and ear-clip triangulation. GPU upload still happens on every run when
`prepare_overlay_area_tile_task_cupy_inputs_from_relation_ordinals` copies the
payload columns to device. True device-resident persistence (keeping CuPy buffers
alive across runs) is not claimed and is not implemented. The report correctly names
this as "the next deeper target." The boundary is well-drawn.

---

## Evidence Quality

Two pod artifacts. The read/write pair is internally consistent (same schema, same
commit, same GPU, same dataset flags). The test suite mechanically enforces 10
structural equality keys and 2 error thresholds between the artifacts. The timing
accounting is unambiguous — `geometry_plus_payload_prepare` is aliased to the cache
load time in the read path at the executor level, not just asserted in the test.

One observation: the write pod used `--payload-workers 8` (parallel geometry repair),
while the read pod used `--payload-workers 1` (default, unused because the cache
short-circuits before the parallel path). The read pod's `payload_workers: 1` in the
artifact confirms the cache bypass, and `parallel_payload_prepare: false` is correct.

---

## Verdict

`accept-with-boundary`

Goal3507 is a clean, conservative workflow optimization. The serialization functions
are generic, the claim boundaries are respected throughout both the code and the
evidence artifacts, correctness is identical between write and read runs, and the
4.07x preparation-stage speedup is artifact-supported. The risks are pre-production
design notes (no content fingerprint, path portability, size) rather than correctness
or boundary concerns.

The improvement is **host-side file-cache reuse of prepared generic component payload
columns**, not true zero-copy, not device-resident persistence, not full polygon
overlay, and not a public speedup or release claim. The goal report, code metadata,
and test suite are consistent on this point.

Accepted as a valid, bounded benchmark-iteration tool. The next step (binary/device-
resident payload cache with a measured ownership contract) is clearly identified.
