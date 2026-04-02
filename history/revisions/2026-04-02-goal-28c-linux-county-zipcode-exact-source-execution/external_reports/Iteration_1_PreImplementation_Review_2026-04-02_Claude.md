---

## Findings (severity order)

### HIGH-1 — Ring-to-chain mapping rule is unspecified

The planned ArcGIS-JSON → CDB converter must decide how to handle multi-ring polygons. ArcGIS `f=json` uses an Esri `rings` array where the first ring is the outer boundary and subsequent rings are holes. The plan says "add a converter" but nowhere specifies:
- one chain per ring, or one chain per edge run?
- how to assign `left_face_id` / `right_face_id` across hole rings (the inner ring's interior is face 0 — outer universe — not the feature's face)
- how to handle multi-part features (disjoint polygons under one OBJECTID, common in county/zipcode data)

This is not a blocker because Codex can make the reasonable choice (one chain per ring, hole rings set right_face_id = 0, multipart features get sequential face IDs), but it must be *declared* before conversion code is written and the report must say what rule was applied. Without that declaration, the "exact-source" claim is unverifiable.

### HIGH-2 — `chains_to_polygon_refs` does not produce polygon geometry; the bridge helper is absent

`datasets.py:418–431` — `chains_to_polygon_refs` returns chain-count-per-face metadata, not vertex sequences. `reference.py:22–26` — `pip_cpu` requires `Polygon` objects with actual `vertices: tuple[tuple[float,float],...]`. The Pre-Implementation Report (step 2) proposes "expose a public helper for converting CDB chains into logical polygons" but this function does not exist yet. Without it, no PiP execution is possible. This is the most structurally load-bearing new piece and the spec does not describe what it should do (simple ring-closed vertex concatenation? winding-order sort?).

### MEDIUM-1 — `chains_to_probe_points` uses boundary points as PiP probes

`datasets.py:402–415` — probe points are taken from `chain.points[0]`, which is a chain endpoint and therefore *on the polygon boundary*, not interior. PiP for a boundary point is numerically degenerate (result depends on boundary-mode convention). The plan says "boundary_mode=inclusive" (reference.py:92), which will count these as hits, but the report must explicitly state that the zipcode-side probe points are chain-start boundary points, not centroid-equivalent interior samples.

### MEDIUM-2 — No explicit statement of which `lsi` runtime is used on Linux

The plan says "lsi and pip runs" on 192.168.1.20. It is not stated whether this means:
- the brute-force `lsi_cpu` / `pip_cpu` from `reference.py` (O(N×M) — with 3144 county polygons × ~7250 zipcode polygons, each with tens of chains, segment pair count is ~10–100M, feasible in Python but slow)
- or the compiled Embree binary on the Linux host

This matters because "CPU vs Embree parity comparison" is a closure requirement. If both paths mean the reference.py pure-Python code vs the Embree C++ binary, that must be explicit. If both use Embree with different geometry backends, that is a different claim. The execution script design depends on this.

### LOW-1 — `build_arcgis_geojson_query_url` is a transparent pass-through

`datasets.py:274–296` — this function duplicates `build_arcgis_query_url` with no modification. Not a blocker, but Codex should eliminate it rather than build more code on top of the duplication.

---

## Verdict

The closure boundary is technically honest. The county-full / zipcode-partial / chain-derived-polygon distinction is clearly declared and matches the evidence from Goal 28B. The repo has the CDB read/write/slice infrastructure that Goal 28C needs. The staged pages on `192.168.1.20` are the correct starting point.

The two HIGH findings are both *known planned deliverables*, not unknown gaps. They need design decisions stated at the top of implementation — not discovered mid-run. Codex must commit in the first commit message to: (a) the ring-to-chain mapping rule it applied, and (b) what "lsi/pip CPU" means in the execution script. Both are resolvable before writing the first converter line.

**Consensus to begin execution**
