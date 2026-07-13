# RTDL Next-Version Performance Blueprint — Layers 1-3 (Layer 4 deferred)

Date: 2026-07-03
Status: architecture blueprint — **not** implementation/POD/performance-claim
authorization. Appendix to `rtdl_programming_model_direction_charter_2026-07-03.md`.

## Scope decision

Do **Layers 1-3 now. Defer Layer 4 (in-traversal fusion / dataflow→PTX compiler).**
Layers 1-3 are the generic "get Python out of the hot pipeline" work: achievable,
lower-risk, and they speed up RayJoin **and every similar multi-stage spatial app**.
Layer 4 is the moonshot that alone can approach the author's fused kernel; it stays
a separate, gated R&D bet and is out of scope here.

## Honest baseline and ceiling

```text
RayJoin Australia warm hot body:   ~3.8-4.0 s
  - output writer (text/topology):  ~1.7-1.9 s   -> Layer 3
  - reprojection + sort (numeric):  ~0.8-0.9 s   -> Layer 2
  - Python row conversion / marshal: residual    -> Layer 1 (also enables 2,3)
  - native traversal (warm):         tiny
AuthorPatch query+output:            0.844 s
AuthorPatch core:                    0.0421 s
```

Honest target for Layers 1-3: **~4 s → ~1-1.5 s**, conditional on the Layer-0
measurement. Layers 1-3 **will not beat the author's fused single-launch** (that
needs Layer 4). Reaching the author's ballpark on wall time while remaining generic
is the win.

## Layer 0 — Prerequisite measurement (gates Layer 3 sizing)

Before committing Layer 3 effort, measure the composition of the ~1.7-1.9 s writer:

```text
writer = output-STRUCTURE assembly (grouping/chaining/aggregation from rows)
       + final byte FORMATTING (into the exact output text/topology format)
```

- If **assembly dominates** → most of the writer is generically recoverable (Layer 3
  compiles the assembly; only a thin format adapter stays app-side).
- If **byte formatting dominates** → less is generically recoverable; the app owns
  the format, and Layer 3's ceiling for RayJoin is lower.

Also confirm the warm-state phase breakdown (reconcile the Goal4888 cold vs Goal4896
warm PIP discrepancy). No implementation before Layer 0.

---

## Layer 1 — Device-resident row-buffer pipeline (the foundation)

**Attacks:** every stage boundary — the Python row conversion / marshalling between
LSI → reproj/sort → PIP → output. Keeps intermediate rows in device/native buffers
across stages; no Python objects, no host round-trips.

**Current cost / expected recovery:** direct recovery is the marshalling/row-conversion
residual (est. ~0.3-0.5 s). Its **larger value is indirect**: it is the prerequisite
that lets Layers 2 and 3 run device-resident. Without Layer 1, Layers 2-3 cannot
stay on device.

**Genericity criterion:** the row-buffer holds generic columnar data
(`id`, coordinates, `flags`, `face_id`, etc.) with explicit dtype/shape/ownership/
lifetime, consumable by any partner (Numba/CuPy) without ad-hoc glue. It must be
demonstrated on at least one **non-RayJoin** spatial app.

**App-specific red-line check:**
- ALLOWED: `LSIRows`, `PointLocationRows`, generic `{id, x, y, flags}` schemas.
- RED LINE: schemas named after RayJoin, or that encode overlay/output-chain
  structure in the core buffer. Test: *would a spatial-join or kNN app use the same
  buffer?* If no, it is app-specific — reject.

**Exit gate:** rows flow LSI→reproj→PIP→output without materializing to Python;
the same buffer serves one non-RayJoin app; byte-equality preserved.

---

## Layer 2 — Device numeric continuation (compile the reduces/maps/sort)

**Attacks:** reprojection + sort + dedupe/group (~0.8-0.9 s), currently Python.

**Current cost / expected recovery:** ~0.8-0.9 s → est. ~0.1-0.2 s on device.
**Recovery ~0.6-0.8 s.** (First check whether reproj/sort are already NumPy-vectorized;
if so, the gain is smaller and the real win is keeping them device-resident, not the
kernel itself.)

**Genericity criterion:** the continuation is expressed as **generic array/reduce
operators** (map, filter, compact, sort, dedupe, group, reduce, reproject) over the
Layer-1 buffers, run device-to-device. The user writes data-flow (Numba/CuPy or the
operator set); RTDL runs it on the resident buffers. Demonstrated on a non-RayJoin app.

**App-specific red-line check:**
- ALLOWED: `sort`, `dedupe`, `group`, `reduce(sum/count/min/max)`, coordinate
  `reproject` as a generic map.
- RED LINE: a "compute overlay midpoints" or "assign overlay faces" operator baked
  into the core as a named primitive. Test: *is it a generic array op, or does it
  encode RayJoin/overlay semantics?* App semantics stay in the app's Numba kernel,
  not in RTDL's operator set.

**Exit gate:** reproj/sort/dedupe run on-device over Layer-1 buffers; the operator
set is generic and used by a non-RayJoin app; byte-equality preserved.

---

## Layer 3 — Generic compiled output-assembly (the big prize, the hardest boundary)

**Attacks:** the output writer (~1.7-1.9 s), the single largest remaining cost.

**Current cost / expected recovery:** **conditional on Layer 0.** If assembly
dominates: recover ~1.0-1.3 s (compile the structure assembly; thin format adapter
stays ~0.4-0.6 s). If byte-formatting dominates: recovery is smaller and app-bound.

**The design (this is the whole point):** RTDL provides a **generic compiled
output-assembly path** — from device-resident rows to a grouped/chained/aggregated
**compact binary / columnar** structure (and common generic sinks: CSV / Arrow /
row-dump). The **exact app output format is a thin adapter the app owns**, over the
generic assembled structure.

```text
resident rows --(RTDL, compiled/device)--> assembled structure (binary/columnar)
                                        --(app, thin adapter)--> exact author text
```

**Genericity criterion:** the compiled writer produces a **generic output shape**
(grouped rows / chains / aggregates / columnar / a small set of standard formats)
that any spatial app can consume. Demonstrated on a non-RayJoin app (e.g. a spatial
join emitting grouped result rows).

**App-specific red-line check (the crux):**
- ALLOWED: RTDL core contains "assemble grouped/chained structure from rows +
  serialize to binary/columnar/CSV/Arrow."
- RED LINE: RTDL core contains "write the RayJoin overlay text/topology format," or
  any output-chain format rule keyed on RayJoin. Test: *does the compiled writer
  produce a format any app could use, with the RayJoin-specific bytes as a thin
  app-owned adapter?* If the exact author format lives in RTDL core, red line crossed
  — it belongs in the RayJoin app package.

**Exit gate:** the expensive structure-assembly is compiled/generic and used by a
non-RayJoin app; the RayJoin exact-text format is a thin app-side adapter over the
generic assembled output; byte-equality preserved; Layer-0 split reported.

---

## Cross-cutting governance

- **Prove generic on a non-RayJoin app.** Every layer must be demonstrated on at
  least one structurally different spatial app (spatial join / kNN+aggregate /
  DBSCAN-like), not only RayJoin. **RayJoin is the exam, not the model.**
- **Byte-equality is a hard gate** at every layer (correctness never regresses for a
  speed change).
- **Phase accounting** on every run: what moved, what did not, denominators + scale.
- **No app-identity in core** (the red-line checks above are the concrete tests).
- **No hot-path claim** without the measured before/after and the comparator named.

## Sequencing & gates

```text
Layer 0  measure writer split + confirm warm breakdown   (gates Layer 3 sizing)
Layer 1  device-resident row-buffer pipeline             (foundation)
Layer 2  device numeric continuation                     (needs Layer 1)
Layer 3  generic compiled output-assembly                (needs Layer 1; sized by Layer 0)
--- Layer 4 (in-traversal fusion) DEFERRED — separate gated spike ---
```

Each layer: measure → implement generic → prove on a non-RayJoin app → phase-account
→ external review → only then the next layer.

## Expected end-state (honest)

Layers 1-3, generic, should take RayJoin-like apps from ~4 s toward ~1-1.5 s warm hot
body — a large, honest, generic speedup that benefits the whole class of multi-stage
spatial apps. It will **not** beat the author's 0.844 s fused route; that last gap is
Layer 4 (deferred). If the honest end-state after Layers 1-3 is "generic, fast,
device-resident spatial pipeline, still short of the author's single fused launch,"
that is a real product win — and Layer 4 remains the optional moonshot.

## Non-authorization

Authorizes no implementation, no POD spend, no performance claim, no app-identity
output format in core, and no Layer 4 work. It sets the Layer 1-3 direction only,
gated by Layer 0 measurement and the per-layer red-line checks.
