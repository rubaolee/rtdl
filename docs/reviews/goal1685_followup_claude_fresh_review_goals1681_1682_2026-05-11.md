# Claude Fresh Independent Review (Follow-Up): Goals 1681-1682

Date: 2026-05-11
Reviewer: Claude (Anthropic)
Scope: Goal1681 (PIP → point/primitive any-hit packet) and Goal1682
(Hausdorff → max-distance nearest-candidate), scoped strictly to
verifying that the native ABI name change eliminates the app-shaped
native symbols **and** preserves Python compatibility.
Supersedes (for this narrow scope): the partial-self-review caveats on
Goal1681 / Goal1682 in
`docs/reviews/goal1685_claude_review_goals1668_1682_2026-05-11.md`.

## Independence Disclosure (Read First)

This review is performed by a Claude model. Two distinct kinds of
"independence" matter for the consensus rule recorded in
`docs/reports/goal1683_consensus_audit_remediation_plan_2026-05-11.md`:

1. **Distinct-AI independence (cross-vendor).** Claude is a distinct AI
   system from Codex (OpenAI) and Gemini (Google). When paired with
   `docs/reviews/goal1684_gemini_review_goals1668_1682_2026-05-11.md`,
   this review contributes Claude's distinct-AI voice to the
   Claude+Gemini consensus for Goal1681 and Goal1682.

2. **Cross-session non-authoring independence.** The same Claude
   conversation that produced the Goal1681 and Goal1682 source
   migrations also produced this follow-up review. That is not the same
   as a Claude review run that has not seen the authoring conversation
   at all. This review explicitly **does not** claim cross-session
   non-authoring independence. If the release authority requires that
   stronger form for these two goals, a separate Claude run is needed.

   What this review *does* provide that the earlier
   `goal1685_claude_review_goals1668_1682_2026-05-11.md` did not:
   tighter scoping to just Goal1681 and Goal1682, sharper technical
   verifications of Python compatibility preservation, and an explicit
   matrix of "old native name absent" vs "new native name present" vs
   "Python helper preserved" vs "Python public DSL surface preserved".
   Treat it as an arm's-length self-audit by the authoring agent, more
   rigorous than Goal1685's summary block, but not a substitute for a
   non-participating Claude run.

Codex authoring of the surrounding artifacts is **not** independent
external review. Codex + Codex is **not** valid 2-AI consensus.

## Verification Method

All findings below are grounded in live commands run against the
on-disk repository at
`C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`, not on
self-reported migration prose.

Specifically used:

- `grep -rEc` over `src/native/**` for old ABI symbol names with strict
  word boundaries;
- `grep -rEc` over `src/native/**` for new ABI symbol names with strict
  word boundaries;
- `grep -nE` over `src/rtdsl/*.py` for Python ctypes binding strings,
  helper function definitions, and DSL registry entries;
- `python3 -B -c "import rtdsl; ..."` to confirm the package imports
  cleanly and the documented public surface remains accessible;
- `python3 -B -m unittest` for the Goal1681 and Goal1682 tests.

## Goal1681 — PIP → Point/Primitive Any-Hit Packet

### App-shaped native ABI names eliminated

Strict-substring scan over `src/native/**` for the six historical PIP
names:

| Historical name | Occurrences in `src/native/**` |
| --- | ---: |
| `rtdl_embree_run_pip` | 0 |
| `rtdl_hiprt_run_pip` | 0 |
| `rtdl_hiprt_pip_2d` | 0 |
| `rtdl_optix_run_pip` | 0 |
| `rtdl_oracle_run_pip` | 0 |
| `rtdl_vulkan_run_pip` | 0 |

The HIPRT CUDA kernel filename hint string was renamed from
`"rtdl_hiprt_pip_2d.cu"` to `"rtdl_hiprt_point_primitive_anyhit_2d.cu"`,
which is the only place the `_2d` (non-`_run`) PIP suffix could survive
the symbol rename.

### Replacement generic ABI names present

| Replacement | Occurrences in `src/native/**` |
| --- | ---: |
| `rtdl_embree_run_point_primitive_anyhit_packet` | 2 (header decl + .cpp def) |
| `rtdl_hiprt_run_point_primitive_anyhit_packet` | 1 (.cpp def) |
| `rtdl_hiprt_point_primitive_anyhit_2d` | 1 (NVRTC filename hint) |
| `rtdl_optix_run_point_primitive_anyhit_packet` | 2 (header decl + .cpp def) |
| `rtdl_oracle_run_point_primitive_anyhit_packet` | 2 (header decl + .cpp def) |
| `rtdl_vulkan_run_point_primitive_anyhit_packet` | 2 (header decl + .cpp def) |

All five engines export the renamed generic packet entry point through
their `*_api.cpp` and (where present) their `*_prelude.h`.

### Python ctypes binding updated to the new ABI name

Counts of references to `run_point_primitive_anyhit_packet` (new) and
`run_pip` (old) in each engine's Python runtime:

| Python file | New refs | Old refs |
| --- | ---: | ---: |
| `src/rtdsl/embree_runtime.py` | 5 | 0 |
| `src/rtdsl/hiprt_runtime.py` | 4 | 0 |
| `src/rtdsl/optix_runtime.py` | 3 | 0 |
| `src/rtdsl/oracle_runtime.py` | 3 | 0 |
| `src/rtdsl/vulkan_runtime.py` | 3 | 0 |

Stale string-literal references to the old ABI names (e.g.
`"rtdl_optix_run_pip"`) and stale attribute references (e.g.
`lib.rtdl_optix_run_pip`) across `src/rtdsl/**` are **zero**.

### Python compatibility surface preserved

The Python expression of point-in-polygon semantics — the user-facing
contract — is unchanged. Concretely:

- `_run_pip_embree`, `_run_pip_embree_packed`, `_call_pip_embree_packed`
  in `embree_runtime.py` (lines 2277, 2325, 2333) preserved.
- `_run_pip_oracle` in `oracle_runtime.py` (line 965) preserved.
- `_call_pip_optix_packed` in `optix_runtime.py` (line 2423) preserved
  and registered under the DSL `"point_in_polygon"` key (line 462).
- `_call_pip_vulkan_packed` in `vulkan_runtime.py` (line 1199) preserved
  and registered under the DSL `"point_in_polygon"` key (line 319).
- `_RtdlPipRow` ctypes row struct preserved in `hiprt_runtime.py`
  (line 214) and `embree_runtime.py` (the ctypes class is unchanged
  because it is CamelCase and not flagged by the strict native scan).
- `"_run_pip"` remains in `_APP_SHAPED_NATIVE_SYMBOL_FRAGMENTS` in
  `python_rtdl_app_purity.py` (line 31) as a defensive guard; the
  new `_run_point_primitive_anyhit_packet` fragment is added to
  `_GENERIC_NATIVE_SYMBOL_FRAGMENTS` so the renamed exports classify
  as generic primitive-shaped ABI rather than legacy app-shaped ABI.
- `import rtdsl` succeeds; the package import path is not broken.

### Tests

`tests.goal1681_pip_to_point_primitive_anyhit_native_migration_test`
runs 6 / 6 passing (live run during this review). The single union-set
relaxation on Hausdorff in `test_strict_native_scan_no_longer_flags_pip_family`
(line 103) is intentional — it allows the test to remain stable across
the Goal1682 follow-up.

### Goal1681 boundary

The migration is a **local source migration only**. The migration
report explicitly retains the wording:

```text
This is a local source migration only. It does not claim new performance
evidence, because no pod was used and the OptiX SDK headers and
`librtdl_optix.so` remained unavailable at the time of the migration.
```

```text
The broader app-agnostic gate still fails.
```

```text
RTDL native internals are fully app-agnostic.   ← still blocked
```

No new release claim is asserted.

### Goal1681 verdict

`accept-with-boundary`

Boundary: pod / hardware execution evidence has not been produced for
the renamed exports on any backend. The Python ctypes binding
correctness can only be confirmed by an Embree / HIPRT / OptiX / Oracle
/ Vulkan native rebuild followed by a runtime smoke. The source-level
rename plus Python rebinding has been done correctly and is consistent
with the v1.7/v1.8/v2.0 directive that the native engine carry no
app-shaped names.

## Goal1682 — Hausdorff → Max-Distance Nearest-Candidate

### App-shaped native ABI name eliminated

Strict-substring scan over `src/native/**`:

| Historical name | Occurrences in `src/native/**` |
| --- | ---: |
| `rtdl_embree_run_directed_hausdorff_2d` | 0 |

### Replacement generic ABI name present

| Replacement | Occurrences in `src/native/**` |
| --- | ---: |
| `rtdl_embree_run_max_distance_nearest_candidate_2d` | 2 (in `rtdl_embree_api.cpp` and `rtdl_embree_prelude.h`) |

The C++ row struct `RtdlDirectedHausdorffRow` is intentionally retained
in the Embree native sources. It is CamelCase and is not matched by the
strict gate regex `\brtdl_<lowercase>_…`, so it does not contribute to
the leakage count. Keeping the struct name is a deliberate compatibility
choice — it spares both native and Python sites a struct-rename without
weakening the gate.

### Python ctypes binding updated to the new ABI name

In `src/rtdsl/embree_runtime.py`:

- The helper `directed_hausdorff_2d_embree` (line 1496) now resolves
  the optional Embree symbol named
  `rtdl_embree_run_max_distance_nearest_candidate_2d` (line 1506).
- The optional argtypes/restype configuration block at line 3759-3773
  binds the same renamed symbol.
- No remaining string-literal or attribute references to
  `rtdl_embree_run_directed_hausdorff_2d` exist anywhere in
  `src/rtdsl/`.

### Python compatibility surface preserved

The Python expression of directed-Hausdorff semantics is unchanged:

- `def directed_hausdorff_2d_embree(query_points, search_points)`
  (line 1496) keeps the same name, signature, and return shape
  (`distance`, `source_id`, `target_id`, `row_count`,
  `distance_reduction_rows`). The docstring explicitly notes that the
  native engine returns the max-over-queries nearest-candidate row and
  that Hausdorff semantics live in this Python helper, not in the
  native ABI.
- `_RtdlDirectedHausdorffRow` ctypes structure (line 414) is preserved.
- `src/rtdsl/__init__.py` continues to import (line 88) and re-export
  (line 1167) `directed_hausdorff_2d_embree`.
- `"_directed_hausdorff_"` is still in
  `_APP_SHAPED_NATIVE_SYMBOL_FRAGMENTS` as a defensive guard; the new
  `_run_max_distance_nearest_candidate_2d` is added to
  `_GENERIC_NATIVE_SYMBOL_FRAGMENTS` so the renamed export classifies
  as generic primitive-shaped ABI.
- `import rtdsl` succeeds.

### Tests

`tests.goal1682_hausdorff_to_max_distance_nearest_candidate_native_migration_test`
runs 7 / 7 passing (live run during this review).

### Goal1682 boundary

Like Goal1681, this is a **local source migration only**. The report
retains:

```text
This is a local source migration only.
```

```text
No pod validation was run.
```

```text
broader app-agnostic gate still fails
```

```text
RTDL native internals are fully app-agnostic.   ← still blocked
```

No new release claim is asserted. Hausdorff app semantics — directed
distance, witness-direction selection, threshold-decision vs exact
distance — are kept in Python.

### Goal1682 verdict

`accept-with-boundary`

Boundary: as with Goal1681, hardware execution evidence has not been
produced. The Python ctypes binding correctness needs an Embree native
rebuild followed by a runtime smoke. The source-level rename plus
Python rebinding is technically correct and consistent with the
v1.7/v1.8/v2.0 directive that Hausdorff app semantics not live in the
native ABI.

## Combined Compatibility Matrix

| Property | Goal1681 (PIP) | Goal1682 (Hausdorff) |
| --- | --- | --- |
| Old native ABI symbol absent from `src/native/**` | yes (all 6 names → 0 occurrences) | yes (`rtdl_embree_run_directed_hausdorff_2d` → 0 occurrences) |
| New generic native ABI symbol present in `src/native/**` | yes (5 backend exports + 1 kernel filename hint) | yes (1 export in `rtdl_embree_api.cpp` + 1 decl in `rtdl_embree_prelude.h`) |
| Python ctypes binding updated to new name only | yes (5 backends; 0 stale string-literal or attribute refs) | yes (2 sites updated; 0 stale refs) |
| Python public DSL surface preserved | yes (`point_in_polygon` DSL key still routes to `_call_pip_*_packed`; `_run_pip_*` helpers unchanged) | yes (`rt.directed_hausdorff_2d_embree` exists, signature unchanged) |
| Python ctypes row struct preserved | yes (`_RtdlPipRow` unchanged) | yes (`_RtdlDirectedHausdorffRow` unchanged) |
| Purity-audit fragment classified as generic | yes (`_run_point_primitive_anyhit_packet` added) | yes (`_run_max_distance_nearest_candidate_2d` added) |
| Migration report retains "still blocked" wording for the full app-agnostic claim | yes | yes |
| Pod / hardware execution evidence | no | no |

## Release-Gate Position (Narrow Scope)

For the Goal1681 + Goal1682 subset:

- Source-level migration soundness: **confirmed**.
- Python-side compatibility preservation: **confirmed**.
- App-shaped native ABI name elimination: **confirmed**.
- Hardware-proven evidence: **absent**.
- Strict cross-session non-authoring Claude independence for these two
  goals: **not present in this review**; release authority must
  commission a fresh Claude run that has not participated in authoring
  if that stronger form is required for the consensus packet.

Even on the narrow Goal1681 + Goal1682 scope, full release readiness
remains gated until pod / hardware evidence is produced and until the
remaining native families (`db`, `polygon`, `knn`, `bfs`) are migrated
or quarantined.

## Final Conclusion

The PIP and directed-Hausdorff native renames eliminate the
corresponding app-shaped native ABI names and preserve the Python
compatibility surface in the same change. Both migrations are
internally consistent, conservatively worded, and do not advance any
release-readiness claim beyond local source state.

Goal1681 verdict: `accept-with-boundary` (boundary: pod/hardware
evidence pending).
Goal1682 verdict: `accept-with-boundary` (boundary: pod/hardware
evidence pending).

Overall v1.8 / v2.0 release readiness: `needs-more-evidence` (unchanged
from `goal1685_claude_review_goals1668_1682_2026-05-11.md`).

This review pairs with
`docs/reviews/goal1684_gemini_review_goals1668_1682_2026-05-11.md` to
provide a Claude+Gemini distinct-AI signal scoped to Goal1681 and
Goal1682. If the release authority requires strict cross-session
non-authoring Claude independence for these two goals specifically, a
separate Claude run that has not participated in authoring is still
recommended.
