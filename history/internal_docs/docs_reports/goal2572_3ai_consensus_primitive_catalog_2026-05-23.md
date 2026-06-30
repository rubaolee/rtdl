# Goal2572 3-AI Consensus: Primitive Catalog And Promotion Rules

Date: 2026-05-23

## Decision

Final verdict: `ACCEPT-WITH-BOUNDARY`.

Codex, Claude, and Gemini agree that `docs/rtdl_primitive_catalog.md` correctly
organizes the current RTDL primitive surface by behavior and maturity, explains
the difference between primitives and app-specific code, records how benchmark
apps created primitive pressure, and blocks public/release/performance/ABI
overclaims.

This consensus is internal architecture documentation only. It does not
authorize public release wording, public speedup claims, external ABI stability,
stable grouped-reduction promotion, `COLLECT_K_BOUNDED` promotion, app-adapter
promotion, or Barnes-Hut native aggregate-frontier support.

## Review Inputs

| Reviewer | Artifact | Verdict |
| --- | --- | --- |
| Codex | `docs/reports/goal2572_primitive_catalog_and_promotion_rules_2026-05-23.md` | `ACCEPT-WITH-BOUNDARY` |
| Claude | `docs/reports/goal2572_claude_primitive_catalog_review_2026-05-23.md` | `ACCEPT-WITH-BOUNDARY` |
| Gemini | `docs/reports/goal2572_gemini_primitive_catalog_review_2026-05-23.md` | `ACCEPT` |

## Consensus Findings

### 1. Source-Of-Truth Alignment

The catalog matches current source constants:

- 4 stable core execution primitives from
  `src/rtdsl/v1_5_migration_inventory.py`;
- 6 stable scalar reductions from the same inventory;
- 1 experimental primitive, `COLLECT_K_BOUNDED`;
- 8 grouped-reduction operations from `src/rtdsl/grouped_reduction.py`.

### 2. Primitive Versus App-Code Boundary

The accepted definition is:

```text
A primitive is app-independent runtime behavior RTDL owns, schedules,
optimizes, and tests across supported execution paths.
```

The following remain app or partner code:

- DBSCAN cluster expansion;
- robot pose/link sampling;
- RayDB-style SQL/schema/query semantics;
- Barnes-Hut inverse-square force law.

### 3. Organization Model

The accepted organization is behavior plus maturity:

```text
stable core execution primitive
+ stable scalar reduction
+ experimental collection primitive
+ shared grouped-reduction substrate
+ app adapter / partner operator
+ rejected candidate
```

Users should select primitives by behavior, not app name.

### 4. Benchmark-App Injection Rule

Benchmark apps may inject pressure but not stable engine primitives. The
promotion path is:

```text
app code -> candidate primitive -> experimental primitive -> stable primitive
```

The control example is Barnes-Hut Goal2549: the native inverse-square scalar
candidate was rejected because it hardcoded app/workload math.

### 5. Accepted Claude Fix

Claude identified one test gap: the report blocked Barnes-Hut native
aggregate-frontier support, but the test did not assert that exact phrase.
The test now includes:

```text
claiming Barnes-Hut native aggregate-frontier support
```

## Final Constraints

Future docs and implementation goals should follow these constraints unless a
later reviewed goal supersedes them:

- Do not flatten all primitive-like surfaces into one list.
- Do not call shared grouped-reduction operations stable external primitives
  until backend support and ABI stability are separately reviewed.
- Do not promote `COLLECT_K_BOUNDED` without the dedicated fail-closed
  collection promotion track.
- Do not treat app adapters as engine primitives.
- Do not move app-specific math into native engines under generic-looking
  names.
- Do not claim Barnes-Hut native aggregate-frontier support from the current
  catalog.
- Do not claim public speedup, release readiness, authors-code parity, or paper
  reproduction from this catalog.

## Consensus Conclusion

Goal2572 closes the immediate organization problem: RTDL now has a documented
primitive catalog, user selection guide, benchmark-injection history, and
promotion rule. The catalog is suitable for internal architecture work and
external review, but not for public release or external ABI stability claims.
