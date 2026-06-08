# Claude Review: Goal3938 Current Benchmark Route Decision Registry

Date: 2026-06-08
Reviewer: Claude (read-only external review)
Scope: `src/rtdsl/current_benchmark_route_decisions.py`, `src/rtdsl/__init__.py`,
`docs/reports/goal3938_current_benchmark_route_decision_registry_2026-06-08.md`,
`tests/goal3938_current_benchmark_route_decision_registry_test.py`, plus Goal3936/Goal3937 evidence.

## Verdict: `accept-with-boundary`

## 1. Route doctrine encoding

The registry is structurally sound: `decision_kind` and `partner_policy` are
constrained enums validated both at construction (`__post_init__`) and via
`validate_current_benchmark_route_decisions`, every row carries non-empty
`evidence_refs`, and every claim-authorization flag defaults to `False` and is
asserted `False` both per-row and in the cross-cutting summary. The five
`decision_kind` values map cleanly onto the stated doctrine:

- `primitive_first` → `hausdorff_xhd`, `raydb_style`, `rtnn`, `triangle_counting`
  (fused generic RTDL primitive wins, partner only as an explicit baseline).
- `numba_continuation` → `rt_dbscan` (custom scalar/row-stream logic wins,
  Numba is the no-RawKernel continuation).
- `fastest_partner_with_numba_reference` → `barnes_hut` (CuPy honestly fastest
  measured, Numba exposed as the no-RawKernel reference — this is the one row
  where `partner_policy="cupy_fastest_numba_reference"` appears, matching the
  doctrine's narrow CuPy carve-out).
- `mixed_explicit` → `spatial_rayjoin` (explicit per-contract user choice,
  `partner_policy="mixed_explicit_user_choice"`).
- `no_partner_needed` → `robot_collision`, `contact_manifold`,
  `librts_spatial_index`.

`user_explicit_choice_required` is hard-pinned to `True` (constructor raises if
not), and `explain_current_benchmark_route` always returns
`automatic_partner_selection_authorized: False` and
`user_choice_remains_authority: True`, including for the unknown-app fallback
path. This correctly keeps the registry advisory rather than dispatching.

## 2. `spatial_rayjoin` row vs. Goal3936

Verified against `docs/reports/goal3936_clean_goal3933_cubin_pod_rerun_2026-06-08.md`
(lines 34-37):

| Contract | Goal3936 reading | Registry encoding |
| --- | --- | --- |
| PIP one-shot | RTDL/OptiX 0.247x → prefer Numba | "Use Numba for bounded PIP one-shot" ✓ |
| PIP repeated | Prepared OptiX batch route amortizes setup | "RTDL/OptiX prepared primitives for repeated PIP" ✓ |
| LSI scalar count | RTDL/OptiX 252.436x → prefer OptiX | "LSI scalar count" → RTDL/OptiX ✓ |
| Overlay active count | RTDL/OptiX 202.372x → prefer OptiX | "overlay active count" → RTDL/OptiX ✓ |

The row's `decision_kind="mixed_explicit"` plus `user_choice_guidance` text
("Do not auto-dispatch. Ask the user which contract they are running...")
correctly forbids auto-dispatch and frames the decision per-contract rather
than as a blanket winner. `rejected_or_unpromoted_candidates` explicitly lists
`"RayJoin paper reproduction"` and `"RTDL-beats-RayJoin whole-app claim"`,
matching the no-paper-reproduction / no-whole-app-claim boundary. `evidence_refs`
includes `Goal3936` and `Goal3937`, consistent with the cited evidence chain.

## 3. `rt_dbscan` row vs. Goal3936

Verified against Goal3936 lines 39-44: "the unblocked grouped stream is faster
than the blocked candidate" (0.0896s vs 0.3937s, "Slower; do not promote"). The
registry row states `decision_kind="numba_continuation"`,
`current_reader_decision="Use the unblocked RTDL/OptiX grouped stream plus Numba
column-signature continuation"`, `user_choice_guidance="...keep blocked mode off
until it wins"`, and `rejected_or_unpromoted_candidates=("blocked grouped stream
candidate from Goal3936",)`. This accurately keeps the blocked candidate
unpromoted and ties the rejection to the specific evidence goal rather than
making a permanent architectural claim ("until it wins" leaves room for future
re-evaluation, matching `next_runtime_action`).

## 4. Claim-boundary integrity

`CURRENT_BENCHMARK_ROUTE_DECISION_CLAIM_BOUNDARY` and the per-row boolean flags
cover: release, public speedup, whole-app acceleration, broad RT-core,
true-zero-copy, automatic partner selection, paper reproduction, and
app-specific native-engine logic. AMD performance wording is covered in the
markdown report's boundary section and in `summarize_current_benchmark_route_decisions`'s
prose claim-boundary string, though **AMD is not its own dataclass field** —
it rides inside the free-text `CURRENT_BENCHMARK_ROUTE_DECISION_CLAIM_BOUNDARY`
constant rather than a machine-checked boolean like the other eight claims.
This is a minor asymmetry (see Finding 1 below) but does not create a hole: the
constant is asserted into every row's metadata and the report text, and no row
or guidance string makes an AMD performance claim — several rows even
explicitly defer AMD validation to "later" (`robot_collision`,
`librts_spatial_index`).

I confirmed by reading every row's `current_reader_decision`,
`user_choice_guidance`, `rejected_or_unpromoted_candidates`, and
`next_runtime_action` string that none contains release, public-speedup,
whole-app, broad-RT-core, true-zero-copy, auto-dispatch, paper-reproduction, or
app-specific native-engine wording. The closest brushes are explicitly framed as
*rejections* (e.g., `triangle_counting`'s `"RT-core triangle-count paper claim"`,
`hausdorff_xhd`'s `"paper-reproduction claim"`, `barnes_hut`'s `"whole
Barnes-Hut speedup claim"`), which is the correct posture — naming the rejected
claim in a `rejected_or_unpromoted_candidates` tuple is governance, not an
assertion of the claim.

## 5. Findings before broader reliance (none release-blocking for internal use)

1. **AMD is text-only, not a typed flag.** Unlike the other eight
   claim-authorization booleans, "AMD performance wording" is only guarded by
   the prose `CURRENT_BENCHMARK_ROUTE_DECISION_CLAIM_BOUNDARY` string and by
   `validate_current_benchmark_route_decisions` not checking it at all. If a
   future row author adds AMD-performance wording to a guidance string, neither
   `__post_init__` nor `validate_current_benchmark_route_decisions` would catch
   it — only the report-level string match in the test would still pass (it
   doesn't scan row content for "AMD"). Recommend adding an
   `amd_performance_claim_authorized: bool = False` field for parity, the same
   way `app_specific_native_engine_logic_allowed` was added alongside the other
   flags. Not a blocker since no current row contains AMD wording, but it is the
   one boundary dimension that depends on prose discipline rather than a typed
   guard.
2. **`pod_needed_next` is uniformly `False`.** That's consistent with "this
   does not run new performance tests," but it does mean the registry currently
   carries no signal for when a row's evidence should be refreshed by a future
   pod run. This is fine as a snapshot-after-Goal3936 artifact; just note that
   nothing in the registry itself will flag staleness as new evidence arrives
   (e.g., if `rt_dbscan`'s blocked-mode gap narrows in a future rerun, a human
   has to notice and edit the row).
3. Both observations are advisory polish, not defects — the registry is
   internally consistent, fully validated, and the test suite exercises the
   exact claims in the review questions (rayjoin mixed-explicit wording,
   rt_dbscan unblocked/blocked wording, barnes_hut honest-fastest-partner
   wording, unknown-app fallback, and report boundary phrases).

## 6. `__init__.py` export check

`current_benchmark_route_decisions`, `explain_current_benchmark_route`,
`summarize_current_benchmark_route_decisions`,
`validate_current_benchmark_route_decisions`,
`CURRENT_BENCHMARK_ROUTE_DECISION_STATUS`, and
`CURRENT_BENCHMARK_ROUTE_DECISION_VERSION` are imported and re-exported in
`__all__` (lines 382-387, 2218-2221). This matches the four public entry points
documented in the report's Purpose section and exercised in the test file.

## Summary

The registry correctly encodes the route doctrine (primitive-first / Numba /
honest-CuPy-with-Numba-reference / mixed-explicit / no-partner), the
`spatial_rayjoin` and `rt_dbscan` rows accurately reflect Goal3936's clean pod
numbers without overclaiming, and every claim-authorization boolean defaults to
and is enforced as `False`. The verdict is `accept-with-boundary` rather than a
plain `accept` because of Finding 1 — AMD-performance-claim avoidance currently
relies on prose discipline rather than a typed/validated field, the only
boundary dimension without that symmetry. This is a polish item for a possible
follow-up goal, not a defect that should block treating Goal3938 as accepted
internal route-governance evidence; no row, guidance string, or report text
currently contains AMD performance wording, release authorization, public
speedup wording, or any of the other prohibited claim categories.
