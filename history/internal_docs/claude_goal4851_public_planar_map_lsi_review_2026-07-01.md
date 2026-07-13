# Claude Review — Goal4851 Public Planar-Map LSI Front Door

Date: 2026-07-01
Reviewer: Claude (independent second seat; Antigravity already approved)
Under review: `goal4851_public_planar_map_lsi_front_door_result_2026-07-01.md` and impl in
`src/rtdsl/optix_runtime.py`, `src/rtdsl/__init__.py`.

## Verdict

```text
verdict: approve_with_required_amendments
(does not simply co-sign Antigravity's clean approve — see AM1-AM3)
bounded claim (public generic planar-map LSI count front door, available pairs): accepted
not authorized: full 8/8, Section 5.7 overlay, speedup, author-correctness (vs internal-consistency), V3/V4, Embree
```

Genuinely good, gap-filling work: it exposes a public generic LSI primitive so a
user no longer has to call the bundled `rtdsl.rayjoin_overlay` helper — directly
resolving the Goal4807 circularity — and it did a proper **synthetic semantic-
delta test** (contract-first discipline). But it is not a clean pass. Three
amendments are substantive.

## Code verification (I checked the implementation, not just the report)

- `prepare_planar_map_lsi_2d_optix` / `PreparedOptixPlanarMapLsi2D` in
  `optix_runtime.py` do **not** import or call `rtdsl.rayjoin_overlay` — the
  "avoids bundled helper" claim holds. ✅
- **But** the primitive internally runs
  `_optix_segment_pair_predicate_mode("rayjoin_lsi")` (lines 3833, 3933), a
  context manager that sets/restores the process-global env var
  `RTDL_OPTIX_SEGMENT_PAIR_PREDICATE` (line 3784). The docstring (3818-3819)
  honestly admits it "uses `rayjoin_lsi` internally."

## Required amendments

### AM1 — "Generic" is true at the API boundary, but the native predicate still wears the RayJoin name
The primitive's native predicate is literally `rayjoin_lsi`. So
`public_generic_rtdl_primitive: true` is honest about the *API* (generic name, no
bundled-helper import) but the *internals* are RayJoin-identity-named. A skeptic
reads "generic wrapper over the RayJoin kernel." **Fix:** rename the native
predicate to a generic name (e.g. `planar_map_lsi`), or explicitly document that
the generic planar-map LSI predicate **is** the native predicate historically
labeled `rayjoin_lsi` (same semantics, renamed). Planar-map LSI genuinely is a
general operation (shared-endpoint rejection is standard arrangement semantics,
as your synthetic delta shows) — so the genericity is *defensible*; make the
internals match the claim.

### AM2 — The env-var toggle is thread-unsafe and fragile for a public primitive
Selecting the predicate by setting/restoring a **process-global** env var around
the native call means two concurrent `prepare_planar_map_lsi_2d_optix` calls race
on `RTDL_OPTIX_SEGMENT_PAIR_PREDICATE`, and any non-context-managed exit leaves
global state changed. For a *public* primitive users may call concurrently, the
predicate must be a **first-class parameter threaded into the native call**, not a
global toggle. At minimum, document the concurrency limitation prominently.

### AM3 — State the provenance of each "expected count": this is internal-consistency, not author-correctness
Australia's expected `13622` came from RTDL's **own** AuthorPatch/bundled LSI path
(result §79). So "public API count matches expected" = "the new generic API
agrees with the old bundled API" — a real and useful **internal-consistency**
result, but **not** independent RayJoin-author validation. County×Zipcode
(`961165`) and Block×Water (`649605`) inputs were **restored from RTDL's own
/dev/shm caches**, so their expected counts are likely also RTDL-side. **Fix:**
for each pair, state whether the expected count is (a) an independent author-
produced ground truth or (b) an RTDL-earlier/bundled count. Re-word the claim to
"count-consistent with the existing bundled LSI path and the restored same-source
expectation," and do not let it read as "matches the RayJoin author's counts"
unless an independent author count is the source.

## Secondary points

### AM4 — Count-only ≠ correctness (your own Goal4816/4833 rule)
Two different-but-wrong implementations can share a count. The synthetic delta
partially compensates on tiny cases, but keep `section52_lsi_count_only: true`
prominent; the bounded LSI-count claim is fine, "correct LSI" is not proven.

### AM5 — Confirm the `8e-14` rayjoin exact-paper test failure is benign, not a regression
`tests.goal4374_rayjoin_exact_paper_suite_test` failing with an `~8e-14` float
mismatch is dismissed as unrelated. But the **core is being actively modified in
the parallel Goal4833 line** (SoS point-location). A mismatch in the RayJoin
exact-paper suite while the core changes must be **confirmed** as pre-existing
float tolerance, not a silent semantic drift from recent core edits. Do not
hand-wave it.

### AM6 — Doc integration + re-audit of the public surface
This adds a new public symbol to the v2.14 API surface I approved as "clean" on
2026-06-30. The new primitive must be added to the user-facing primitive
catalog / feature guide, and the public-surface cleanliness re-checked after doc
integration. Right now it is an undocumented public export.

## Notes (non-blocking, correctly handled by the doc)

- `/dev/shm` cache restoration is transient; the doc correctly disclaims
  "cache recovery ≠ durable dataset management" and lists durable dataset storage
  as remaining data-engineering debt. AM3 is the sharper (provenance) version of
  this concern.
- `tests.goal3728_...` failing on a moved `docs/reports/...` file is test-hygiene
  debt from the public-surface cleanup (which I approved) — a small side effect,
  not a Goal4851 defect. Fix the test path.

## Credit

Fills a real gap (public LSI without the bundled helper); proper synthetic
semantic-delta test proving it is a distinct contract, not an alias; honest
classification flags (`bundled_rayjoin_helper_used: false`, count-only); bounded
claim with correct non-authorizations. This is materially better discipline than
the earlier lines.

## Non-authorization

Authorizes only the bounded public-planar-map-LSI-count front door for the
available pairs, as internal-consistency evidence. Not full 8/8 Section 5.2, not
Section 5.7 overlay, not author-correctness, not speedup, not V3/V4, not Embree,
not "cache recovery = durable dataset management."
