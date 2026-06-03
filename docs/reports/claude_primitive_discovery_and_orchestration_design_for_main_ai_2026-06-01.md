# RTDL Primitive Discovery & Orchestration — Design for Main AI

Author: Claude (independent design)
Date: 2026-06-01
Priority: TOP (user-designated)
Audience: Main AI (coordination / build), Gemini (second reviewer)
Status: design proposal / work definition. Authorizes nothing (no release, speedup, zero-copy, auto-partner, paper-reproduction, or app-specific-engine claims). Pure discovery/governance layer; does not touch the native engine.

Companion / source-of-truth:
- Code: `src/rtdsl/primitive_hierarchy.py` (`PrimitiveHierarchyNode`, `PRIMITIVE_HIERARCHY`, `primitive_hierarchy()`, `primitive_layer_map()`, `validate_primitive_hierarchy()`)
- Catalog: `docs/rtdl_primitive_catalog.md`
- Doctrine: `src/rtdsl/v2_5_execution_path_policy.py` (`v2_5_primitive_first_selection_doctrine`)

## 1. Problem statement

The primitive surface has grown across ~3000 goals. Two concrete failures:

1. **Users can't find the right primitive.** The hierarchy is organized by *execution layer* (`execution_residency → traversal → row_emission → bounded_materialization → reduction → continuation → candidate_experimental`) — i.e., by *how a primitive is built*, not by *what a user wants*. A user thinks "count points within a radius," not "a traversal-layer fixed-radius primitive."
2. **Even the Main AI forgets whether a similar primitive already exists**, so near-duplicates get proposed. There is no search-before-create step, no synonym resolution, and two drifting sources of truth (code + prose).

This is a discoverability/governance problem, not an engine problem. The fix is small, high-leverage, and app-agnostic. It is also the necessary companion to the primitive-first doctrine: "primitive-first" only works if people and agents can *find* the primitive.

## 2. Root-cause diagnosis

- **Wrong index direction.** The hierarchy provides forward lookup (layer → primitive). Discovery needs the inverse (intent → primitive).
- **No synonyms/aliases.** "knn / nearest-neighbor / top-k / ranked-summary" and "fixed-radius count / density / neighbor-count / DBSCAN core" name the same families differently across docs; keyword search for one misses the rest.
- **Two sources that drift.** `primitive_hierarchy.py` (code SoT) and `rtdl_primitive_catalog.md` (prose) are maintained separately; "is there already an X?" means reading prose — exactly where things get missed.
- **No duplicate gate.** Promotion checks app-agnosticism, capacity/overflow, and boundaries, but not "does a near-duplicate already exist?" Nothing forces the search.

## 3. Design overview (three layers, one source of truth)

Keep the execution-layer hierarchy (it is the right structure for dependency/governance). Add three things on top of the *same* nodes:

1. **Capability index** — an orthogonal, flat, faceted view answering "what does it do."
2. **Discovery API** — `find_primitive(...)` (inverse index) + `primitive_index()` (flat table) + a promotion **duplicate gate**.
3. **Orchestration** — named **composition recipes** + an **advisory planner** that emits plans but never dispatches.

The node remains the single source of truth; the catalog md is *generated* from nodes so it cannot drift.

## 4. Node schema additions (metadata-only, backward-compatible)

Extend `PrimitiveHierarchyNode` with optional, defaulted fields so existing nodes keep working:

```python
@dataclass(frozen=True)
class PrimitiveHierarchyNode:
    # existing
    id: str
    title: str
    layer: str
    status: str
    summary: str
    outputs: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()
    children: tuple["PrimitiveHierarchyNode", ...] = ()
    boundary: str = ""
    # NEW — discovery metadata
    capability_tags: tuple[str, ...] = ()      # controlled facets, see §5
    aliases: tuple[str, ...] = ()              # synonyms: ("knn","nearest_neighbor","top_k")
    intent_phrases: tuple[str, ...] = ()       # natural-language needs this answers
    reference_path: str = ""                   # the universal CPU/reference entrypoint (Principle 2)
    backends: tuple[str, ...] = ()             # ("cpu","embree","optix")
    partner_ops: tuple[str, ...] = ()          # continuation ops, if any (e.g. "segmented_sum_f64")
    considered_alternatives: tuple[str, ...] = ()  # node ids weighed before adding (anti-duplicate, §7)
    distinct_from: str = ""                     # why this is not a duplicate of the nearest existing node
```

`to_dict()` serializes the new fields. `validate_primitive_hierarchy()` gains checks (see §8).

## 5. Controlled capability facets (the taxonomy)

`capability_tags` are drawn from a small controlled vocabulary so the index is queryable and lint-able, not free text. Proposed facet families (each tag is `family:value`):

| Facet family | Example values |
| --- | --- |
| `intent` | `exists`, `count`, `nearest`, `membership`, `intersection`, `components`, `reduce`, `topk`, `collect_rows`, `frontier` |
| `shape` | `fixed_radius`, `closed_shape`, `segment_pair`, `ray_triangle`, `aabb`, `point_in_polygon` |
| `dim` | `2d`, `3d` |
| `output` | `scalar`, `rows`, `grouped`, `mask`, `witness`, `columns` |
| `exactness` | `exact`, `approx`, `bounded` |
| `keying` | `none`, `by_group_id`, `by_query_id`, `by_ray_id` |

This is deliberately a closed set; new values require a one-line vocabulary addition, which is itself the moment to ask "is this really new?"

## 6. Discovery API

Three callables in a new `src/rtdsl/primitive_discovery.py` (built over the existing `iter_primitive_hierarchy_nodes()`):

### 6.1 `primitive_index() -> tuple[dict, ...]`
A flat table: one row per primitive with every facet, status, layer, backends, reference_path, aliases, intent_phrases, outputs, boundary. This is the single place the Main AI greps instead of reading prose across docs.

### 6.2 `find_primitive(query=None, *, intent=None, shape=None, dim=None, output=None, exactness=None, status=None, text=None) -> list[Match]`
Inverse index. Returns ranked candidate primitives. Ranking = exact facet matches first, then alias/intent_phrase hits, then summary text hits. Each `Match` carries: node id, title, status, layer, backends, reference_path, matched_on (which facet/alias/phrase), and `compose_hint` ("no exact primitive — compose these in layer order: …" when only a composition fits). Example:

```python
find_primitive(intent="count", shape="fixed_radius", dim="3d", output="scalar")
# -> [FIXED_RADIUS_COUNT_THRESHOLD_3D (stable, optix/cpu, ref=...), ...]
find_primitive(text="nearest neighbor ranked")
# -> resolves via aliases to the ranked-summary/top-k family
```

Pure tag + alias + substring matching delivers ~80% of the value with zero ML. Semantic/embedding search over `summary`+`intent_phrases` is an optional later upgrade, not a prerequisite.

### 6.3 `describe_primitive(node_id) -> dict`
Full record for one primitive (facets, backends, reference path, partner ops, boundary, depends_on, recipes-that-use-it). The "I found a candidate, tell me everything" call.

## 7. The duplicate gate (the core anti-redundancy mechanism)

This is what stops re-inventing existing primitives — for humans and the Main AI alike.

- **Promotion requirement:** a new candidate `PrimitiveHierarchyNode` must populate `considered_alternatives` (node ids returned by a `find_primitive` query on its own facets) and `distinct_from` (one sentence on why the nearest existing node does not suffice).
- **Lint:** `validate_primitive_hierarchy()` (or a dedicated `lint_new_primitive(node)`) computes the nearest existing nodes by facet overlap; if a new node shares all of `{intent, shape, dim, output, keying}` with an existing node and has empty `distinct_from`, it **fails closed** with "possible duplicate of `<id>`; set distinct_from or reuse it."
- **Agent workflow rule:** before proposing any new primitive, call `find_primitive(...)` and paste the result into the goal report. Make this a checklist item in the primitive-promotion handoff template.

This converts "the Main AI forgot to check" into "the build cannot proceed without the check."

## 8. Single source of truth + validation

- **Generate the catalog.** `docs/rtdl_primitive_catalog.md` becomes generated from `primitive_hierarchy()` (a `tools/generate_primitive_catalog.py`). A test asserts the committed md matches regenerated output, so code and prose can never drift.
- **Extend `validate_primitive_hierarchy()`** to require, for every node above a status threshold (e.g. `candidate_behavior` and stabler): non-empty `capability_tags` (all from the controlled vocab), a `reference_path` (Principle 2: every primitive has a partner-free path), and — for new nodes — the duplicate-gate fields. Unknown facet values fail closed.

## 9. Orchestration (advisory, never dispatch)

Most real needs are compositions, not atoms. Two additions:

### 9.1 Named composition recipes
Promote the pipelines the catalog already describes (e.g. "fixed-radius counts → threshold flags → grouped union → component labels") into first-class, queryable `CompositionRecipe` records: an ordered list of primitive node ids + the partner choice per phase + the claim boundary + the app pressure that motivated it. `find_recipe(intent=...)` returns matching recipes. This makes *combinations* discoverable, which is where users actually live.

### 9.2 Advisory planner / explain
A `plan_continuation(intent, ...)` that returns a *plan*, consistent with the primitive-first doctrine and Principles 1–2:
- if a fused generic primitive exactly expresses the work → recommend primitive-first (no partner);
- else → recommend the composition recipe and, per unfused phase, list candidate partners with the same-contract evidence pointer (never an auto-selected one);
- always emit the claim boundary.

Hard rule: the planner **advises**; the app **chooses**. No hidden dispatch, no auto-partner selection — this is the existing `automatic_triton_selection_allowed = False` discipline extended to all partners. The rt_dbscan `plan/explain` modes are the working precedent.

## 10. Sequenced work (goal numbers are placeholders)

| # | Item | Type | Exit gate |
| --- | --- | --- | --- |
| D-1 | Add discovery fields to `PrimitiveHierarchyNode` + controlled facet vocabulary | schema | nodes accept new fields; `to_dict` serializes; existing tests pass |
| D-2 | Backfill `capability_tags`/`aliases`/`intent_phrases`/`reference_path`/`backends` for current stable + candidate nodes | data | every node ≥ candidate has tags from the vocab and a reference_path |
| D-3 | `primitive_discovery.py`: `primitive_index()`, `find_primitive()`, `describe_primitive()` | API | sample intent queries return the expected nodes; covered by tests |
| D-4 | Duplicate gate: `lint_new_primitive()` + extend `validate_primitive_hierarchy()`; add the checklist to the promotion handoff template | governance | a synthetic near-duplicate node fails closed without `distinct_from` |
| D-5 | Generate `rtdl_primitive_catalog.md` from nodes + drift test | docs | committed md == regenerated md (test enforced) |
| D-6 | `CompositionRecipe` + `find_recipe()`; encode the known app pipelines as recipes | orchestration | the RT-DBSCAN / RayJoin / Hausdorff pipelines are queryable recipes |
| D-7 | `plan_continuation()` advisory planner (primitive-first aware, partner-advisory) | orchestration | planner recommends primitive-first for fusible intents, recipe+advisory partners otherwise; never auto-selects |
| D-8 (optional) | Embedding semantic search over `summary`+`intent_phrases` | enhancement | text queries resolve fuzzy intents; behind a flag |

D-1…D-5 are the high-leverage core and could land quickly; D-6…D-7 add orchestration; D-8 is a later nicety.

## 11. Acceptance criteria

- `find_primitive(intent=..., shape=..., dim=..., output=...)` returns the correct existing primitive(s) for a representative set of needs (count-within-radius, nearest/top-k, point-in-polygon, grouped reduction, components, bounded row collection).
- A proposed near-duplicate primitive **cannot be added** without `considered_alternatives` + `distinct_from`; the lint fails closed otherwise.
- The catalog md is generated and a test prevents drift from the node SoT.
- Every node ≥ candidate has controlled-vocab `capability_tags` and a `reference_path`.
- The planner recommends primitive-first when a fused primitive fits and an advisory recipe+partner list otherwise, and **never** auto-selects a partner.

## 12. Boundaries / non-goals

- App-agnostic only: facets and recipes describe generic behavior; no app-domain vocabulary enters node tags (the `APP_OWNED_BOUNDARY_EXCLUSIONS` list still governs).
- No engine changes; this is a discovery/governance/orchestration layer in Python + docs.
- The planner is advisory; it authorizes nothing and selects nothing automatically.
- Not a release, performance, zero-copy, or paper-reproduction artifact.

## 13. Questions for Main AI / Gemini

1. Accept the three-layer approach (capability index + discovery API + advisory orchestration) over the existing layer hierarchy, keeping the hierarchy as the dependency/governance structure?
2. Is the controlled facet vocabulary (§5) the right starting set, or should it start even smaller?
3. Is the duplicate gate (`considered_alternatives` + `distinct_from` + fail-closed lint) acceptable as a hard promotion requirement?
4. Generate the catalog md from nodes (single source of truth) — agreed?
5. Keep the planner strictly advisory (no auto-selection), consistent with the primitive-first / no-auto-Triton doctrine — agreed?
6. Sequence: land D-1…D-5 (discovery core) first, defer D-6…D-8 (orchestration + semantic search)?

## 14. Bottom line

The hierarchy is the right *governance* structure but the wrong *discovery* structure. Add an orthogonal capability index over the same nodes, a `find_primitive` inverse-index API, and a fail-closed duplicate gate, all driven from a single generated source of truth — then layer named composition recipes and an advisory primitive-first planner on top. This directly fixes both failures (users can't find primitives; the Main AI forgets duplicates exist), is small and app-agnostic, touches no engine code, and is the natural enabler of the primitive-first doctrine: you can only go primitive-first if you can find the primitive.
