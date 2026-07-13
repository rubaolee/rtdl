# Claude Review — Goal4857 Planar-Map Point-Location Public Front Door Cleanup

Date: 2026-07-01
Reviewer: Claude (independent second seat; Antigravity already reviewed)
Under review: `goal4857_planar_map_point_location_public_front_door_cleanup_2026-07-01.md`,
impl in `src/rtdsl/optix_runtime.py`, `docs/features/pip/README.md`.

## Verdict

```text
verdict: approve_with_required_amendments
(close to a clean approve; the amendments are claim-scoping, not code defects)
```

Genuinely good, and more disciplined than Goal4851. It moves the RayJoin-ness
**off the user boundary** (where it was a leak) and **into a hidden, locked
internal bridge** (an implementation detail), and it is honest about that. The
one thing that must be stated more sharply: this is an **API-boundary cleanup
over a PIP route whose correctness is still open in Goal4833** — it must not read
as "PIP is now correct."

## Code/doc verification (I checked, not just the report)

- `_PLANAR_MAP_POINT_LOCATION_ENV_LOCK = threading.RLock()` (optix_runtime.py:3823)
  guards the env bridge — this **fixes my Goal4851 thread-safety amendment (AM2)**.
  Credit: they carried the LSI-review lesson forward.
- The bridge still sets `RTDL_RAYJOIN_CDB_QUERY_MAP_ID` / `..._SCALE_MIN_X` etc.
  (lines 4008-4016) — the native bridge is still RayJoin-named, now hidden and
  locked. The report discloses this honestly (Boundaries §165-167).
- No `import rayjoin_overlay`; metadata `bundled_rayjoin_helper_used: false`. ✅
- `docs/features/pip/README.md` is honest: "hides the legacy CDB point-location
  execution bridge," "Application code should not set `RTDL_RAYJOIN_CDB_*`
  directly," "point-location/PIP, not polygon overlay," and — importantly —
  "current paths are float-based, not robust exact geometry." No "fully
  generalized ABI" overclaim. ✅

## Answer to the specific skeptical point

> Public name is generic, native bridge is still RayJoin-shaped. Honest enough,
> or does it mislead users into thinking RTDL has a fully generalized ABI?

**Honest enough for a v2.14 cleanup** — because both the internal report AND the
user-facing README explicitly say it is a *front door that hides a legacy
bridge*, not a generalized ABI, and disclose the float/non-exact limitation. The
mislead-risk is real but is genuinely mitigated by the wording. This is the right
way to do an incremental cleanup: relocate the RayJoin-ness from a user leak to a
disclosed, guarded implementation detail. (Contrast Goal4851, where I had to
*catch* the `rayjoin_lsi` internal name; here it is proactively disclosed.)

## Required amendments

### AM1 — State that this is API-boundary cleanup only; PIP correctness is inherited and STILL OPEN
Goal4857 adds **no new PIP correctness evidence**: its 11 tests are all
API-shape (export, feature-matrix, metadata, "no old env helper"). It "delegates
to the already repaired directed point-location native path" — but that native
PIP path is **still under active repair in Goal4833** (the County×Zipcode
chain-30138 mismatch is not resolved). So the authorized claim must say
explicitly: **"clean public PIP front door" does not mean "PIP is correct."**
Correctness is inherited from an open line, not established here.

### AM2 — Bound the claim to "front door over a historical native route," not "generalized ABI"
The native bridge is still `RTDL_RAYJOIN_CDB_*` env-var based. Acceptable for the
cleanup, but ensure the feature-matrix / catalog wording matches the README's
honesty and does not imply a first-class generalized ABI. When the native ABI
cleanup is eventually done, rename `RTDL_RAYJOIN_CDB_*` → a generic
(`RTDL_PLANAR_MAP_CDB_*`) name so the internals match the generic claim (this is
the same predicate-naming debt as Goal4851 AM1, carried forward as real future
work — track it, don't lose it).

### AM3 (minor) — Document the serialization + backend-scope
The `RLock` makes the primitive **thread-safe but serialized** (concurrent
point-location calls cannot overlap) — document this limitation. Also, pip/README
lists OptiX/Vulkan/HIPRT/Apple RT for the general PIP feature, while the new
`prepare_planar_map_point_location_2d_optix` front door is OptiX-only
(`native` OptiX, `unsupported_explicit` others). Clarify that the general PIP
predicate and this specific planar-map front door have different backend scope.

## Exactly what is authorized / not authorized

**Authorized:**
- RTDL exposes a public, generic-named planar-map point-location/PIP front door
  (`prepare_planar_map_point_location_2d_optix`).
- User/application code no longer sets RayJoin-era `RTDL_RAYJOIN_CDB_*` env vars;
  the front door hides and (thread-safely) locks the legacy bridge.
- The front door does not import the bundled `rtdsl.rayjoin_overlay` helper.
- Generic dataset adapters (`chains_to_planar_map_segments/points`) added while
  preserving the old `chains_to_rayjoin_cdb_*` compat names.

**Not authorized:**
- "RTDL has a fully generalized / first-class native planar-map point-location
  ABI" — the native bridge is still RayJoin-named env vars, hidden and guarded,
  pending future native cleanup.
- "The PIP route is correct/complete" — no correctness evidence added here;
  correctness is inherited and still open in Goal4833.
- Section 5.3 all-eight; Section 5.7 overlay; broad RayJoin or RTDL performance.

## Answers to the nine questions

1. **Legitimate public generic front door?** Yes, at the API boundary.
2. **Merely a RayJoin helper under a generic name?** No — it doesn't call the
   bundled helper, and planar-map point-location is a general operation. But the
   native bridge is still RayJoin-named (disclosed).
3. **Acceptable that impl still uses `RTDL_RAYJOIN_CDB_*` internally?** Yes for
   this cleanup — hidden, locked, restored, and disclosed. Not a generalized-ABI
   claim.
4. **Must the native bridge be fixed now?** No — it is legitimate optional future
   work (AM2). The cleanup can close without it, provided the claim is bounded.
5. **Do the new dataset aliases help without erasing compat?** Yes — generic
   names added, old `rayjoin_cdb` names preserved.
6. **Do the Section 5.3 runners avoid the old user-side env helper?** Per the
   report's scan, yes (no `_point_location_env`, no direct `RTDL_RAYJOIN_CDB_*`).
7. **Docs bounded correctly?** Yes — pip/README refuses overlay, is honest about
   the hidden bridge and float/non-exact limitation. Apply AM3 for backend-scope
   clarity.
8. **Tests sufficient?** For an API-boundary cleanup, yes (they gate the boundary
   and the metadata). They are **not** correctness tests — hence AM1: do not let
   the passing tests imply PIP correctness.
9. **Close with `completed_..._cleanup`?** Yes, with the AM1 correctness-scope
   caveat recorded in the exit note.

## Non-authorization

Authorizes only the bounded API-boundary cleanup as stated above. No PIP
correctness claim, no generalized-ABI claim, no Section 5.3 all-eight, no
Section 5.7 overlay, no performance claim, no V3/V4, no Embree.
