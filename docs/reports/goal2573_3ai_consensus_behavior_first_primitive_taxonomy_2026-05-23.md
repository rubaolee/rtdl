# Goal2573 3-AI Consensus: Behavior-First Primitive Taxonomy

Date: 2026-05-23

## Decision

Final verdict: `ACCEPT`.

Codex, Claude, and Gemini agree that the RTDL primitive catalog must be
organized by behavior first. Stability, maturity, backend coverage, and
implementation ownership are metadata on a behavior family; they are not the
top-level taxonomy.

This consensus supersedes any layer-first or maturity-first reading of the
primitive catalog. The catalog should not be organized as stable core,
experimental, substrate, adapter, or rejected layers. Those labels remain valid
only as status or promotion metadata.

## Review Inputs

| Reviewer | Artifact | Verdict |
| --- | --- | --- |
| Codex | `docs/rtdl_primitive_catalog.md` and `docs/reports/goal2572_primitive_catalog_and_promotion_rules_2026-05-23.md` | `ACCEPT` |
| Claude | `docs/reports/goal2573_claude_behavior_first_primitive_taxonomy_review_2026-05-23.md` | `ACCEPT` |
| Gemini | `docs/reports/goal2573_gemini_behavior_first_primitive_taxonomy_review_2026-05-23.md` | `ACCEPT` |

## Accepted Organization Rule

The primary taxonomy is:

```text
hit/traversal predicate
+ spatial neighborhood predicate
+ exact geometry summary
+ scalar reduction
+ grouped/keyed reduction
+ columnar compact summary
+ collection/row materialization
+ aggregate-frontier candidate
+ app/partner math boundary
```

Status is metadata:

```text
stable primitive | experimental primitive | internal substrate
| candidate behavior | app/partner code | rejected candidate
```

## Constraints

- Users select primitives by behavior first, not by benchmark app name.
- Users also should not start from maturity labels such as core, stable,
  experimental, or internal substrate.
- App-specific semantics remain outside the engine: DBSCAN cluster expansion,
  robot pose/link sampling, RayDB-style schema/query semantics, and Barnes-Hut
  inverse-square force law are not RTDL engine primitives.
- Grouped-reduction operations are reusable behavior, but not stable external
  primitives until separately promoted.
- `COLLECT_K_BOUNDED` remains experimental until the dedicated fail-closed
  collection promotion track completes.
- Compatibility names such as `DB_COMPACT_SUMMARY` do not authorize external
  ABI stability or broad DB claims.
- The catalog does not authorize public release wording, public speedup
  claims, authors-code parity, paper reproduction, or external ABI stability.

## Conclusion

The behavior-first taxonomy is the accepted primitive-catalog organization.
Future primitive work should add or promote behavior families, then attach
status, backend, ownership, evidence, and claim-boundary metadata to each
behavior.
