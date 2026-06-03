from __future__ import annotations

from .primitive_hierarchy import APP_OWNED_BOUNDARY_EXCLUSIONS
from .primitive_hierarchy import PRIMITIVE_CAPABILITY_TAGS
from .primitive_hierarchy import PRIMITIVE_HIERARCHY
from .primitive_hierarchy import PRIMITIVE_HIERARCHY_LAYER_ORDER
from .primitive_hierarchy import PRIMITIVE_HIERARCHY_STATUSES
from .primitive_hierarchy import PrimitiveHierarchyNode
from .primitive_hierarchy import validate_primitive_hierarchy
from .primitive_discovery import validate_primitive_semantic_search
from .primitive_planner import PRIMITIVE_ADVISORY_PLANNER_AUTO_PARTNER_SELECTION_ALLOWED
from .primitive_planner import PRIMITIVE_ADVISORY_PLANNER_CLAIM_BOUNDARY
from .primitive_planner import PRIMITIVE_ADVISORY_PLANNER_EXECUTES
from .primitive_planner import PRIMITIVE_ADVISORY_PLANNER_VERSION
from .primitive_planner import validate_primitive_advisory_planner
from .primitive_recipes import COMPOSITION_RECIPES
from .primitive_recipes import CompositionRecipe
from .primitive_recipes import validate_composition_recipes


PRIMITIVE_CATALOG_GENERATOR_VERSION = "rtdl.primitive_catalog.generated.v1"
PRIMITIVE_CATALOG_DATE = "2026-06-03"

_STATUS_MEANINGS = {
    "stable_primitive": "RTDL owns the app-independent behavior under stated backend and evidence boundaries.",
    "stable_behavior": "Stable governing behavior or contract, not necessarily a standalone external primitive.",
    "stable_compatibility_path": "Supported compatibility behavior with explicit naming and claim boundaries.",
    "internal_substrate": "Shared implementation contract used by RTDL paths, but not yet an externally stable primitive.",
    "internal_generic_path": "Generic internal path used by backend adapters or front doors.",
    "candidate_behavior": "Reusable pressure exists, but the primitive contract is not accepted yet.",
    "app_or_partner_code": "Domain semantics, custom math, or partner-specific implementation outside engine ownership.",
}


def render_primitive_catalog_markdown() -> str:
    """Render the primitive catalog from the Python hierarchy source of truth."""

    validation = validate_primitive_hierarchy()
    discovery_validation = validate_primitive_hierarchy(require_discovery_metadata=True)
    semantic_validation = validate_primitive_semantic_search()
    recipe_validation = validate_composition_recipes()
    planner_validation = validate_primitive_advisory_planner()
    lines: list[str] = [
        "# RTDL Primitive Catalog And Promotion Rules",
        "",
        f"Date: {PRIMITIVE_CATALOG_DATE}",
        "",
        "Status: generated internal architecture catalog. This document organizes",
        "the current RTDL primitive surface; it does not authorize public release",
        "wording, public speedup claims, external ABI stability, authors-code",
        "parity, or paper reproduction claims.",
        "",
        "> Generated from `src/rtdsl/primitive_hierarchy.py` by",
        "> `scripts/generate_rtdl_primitive_catalog.py`. Do not hand-edit this",
        "> file; change the Python hierarchy or renderer and regenerate it.",
        "",
        "## What Primitive Means",
        "",
        "An RTDL primitive is an app-independent runtime operation that RTDL agrees",
        "to own, schedule, optimize, and test across supported execution paths.",
        "",
        "A primitive must have:",
        "",
        "- app-independent semantics;",
        "- typed inputs and outputs;",
        "- explicit result layout;",
        "- backend or partner lowering rules;",
        "- deterministic, tolerance, capacity, and overflow behavior;",
        "- correctness tests and evidence boundaries;",
        "- claim wording that blocks app/product overreach.",
        "",
        "If removing operation `X` would force multiple apps to reimplement the",
        "same low-level behavior, `X` is a primitive candidate. If removing `X`",
        "only breaks one domain's interpretation, `X` is app code.",
        "",
        "| Operation | Classification | Reason |",
        "| --- | --- | --- |",
        "| `ANY_HIT` | Primitive | Many apps need existence over rays, segments, or primitives. |",
        "| `COUNT_HITS` | Primitive | Many apps need count summary without materializing hit rows. |",
        "| `group_sum_i64` | Shared grouped-reduction operation | Reusable grouped aggregation across columnar and app-adapter paths. |",
        "| DBSCAN cluster expansion | App code | It is DBSCAN domain semantics. |",
        "| Robot pose/link sampling | App code | It is robotics domain lowering. |",
        "| Barnes-Hut inverse-square force law | App or partner code | It is workload math, even if given a generic-looking name. |",
        "",
        "## Hierarchical Primitive Organization",
        "",
        "The top-level organization is a dependency hierarchy. Lower layers provide",
        "runtime substrate for higher layers. Stability, maturity, backend coverage,",
        "and implementation owner are metadata on each node; they are not the hierarchy.",
        "",
        "The source-of-truth code for this hierarchy is",
        "`src/rtdsl/primitive_hierarchy.py` and is exported as:",
        "",
        "```python",
        "rtdsl.primitive_hierarchy()",
        "rtdsl.primitive_layer_map()",
        "rtdsl.validate_primitive_hierarchy()",
        "```",
        "",
        "For v2.7 discovery work, the same node data also carries a metadata overlay",
        "for user-intent search. The hierarchy remains the governance/dependency",
        "source of truth; the discovery API is only an index over those nodes:",
        "",
        "```python",
        "rtdsl.primitive_index()",
        'rtdsl.find_primitive(intent="count", shape="fixed_radius", dim="3d")',
        'rtdsl.describe_primitive("traversal.fixed_radius_count_threshold")',
        "rtdsl.lint_new_primitive(candidate_node)",
        "```",
        "",
        "Discovery facets use the controlled families `intent:*`, `shape:*`,",
        "`dim:*`, `output:*`, `exactness:*`, and `keying:*`. New promoted",
        "primitives that overlap an existing primitive's key facets must record",
        "`considered_alternatives` and `distinct_from`; otherwise the duplicate",
        "gate fails closed. This keeps the catalog searchable without turning RTDL",
        "into an app-shaped library.",
        "",
        "Approved layer order:",
        "",
        "```text",
    ]
    lines.extend(f"{index}. {_title_from_layer(layer)}" for index, layer in enumerate(PRIMITIVE_HIERARCHY_LAYER_ORDER, 1))
    lines.extend(
        [
            "```",
            "",
            "Dependency rule:",
            "",
            "```text",
            "Execution / Residency",
            "-> Traversal",
            "-> Row Emission",
            "-> Bounded Materialization or Reduction",
            "-> Continuation",
            "-> App semantics",
            "```",
            "",
            "App semantics are deliberately outside the hierarchy. If a proposed",
            "native node needs DBSCAN, robot, contact, collision, RayDB, RayJoin,",
            "RTNN, Barnes-Hut force-law, SQL, or graph-domain meaning, it is",
            "app/partner code unless it is redesigned as an app-independent behavior.",
            "",
            "## Generated Validation Snapshot",
            "",
            f"- Generator version: `{PRIMITIVE_CATALOG_GENERATOR_VERSION}`",
            f"- Hierarchy validation valid: `{validation['valid']}`",
            f"- Node count: `{validation['node_count']}`",
            f"- Unknown capability tags: `{_format_tuple(validation['unknown_capability_tags'])}`",
            f"- Missing dependencies: `{_format_tuple(validation['missing_dependencies'])}`",
            f"- Backward dependencies: `{_format_tuple(validation['backward_dependencies'])}`",
            f"- Strict discovery metadata validation valid: `{discovery_validation['valid']}`",
            f"- Strict discovery metadata missing: `{_format_tuple(discovery_validation['discovery_metadata_missing'])}`",
            f"- Semantic search preview validation valid: `{semantic_validation['valid']}`",
            f"- Semantic search preview executes: `{semantic_validation['executes']}`",
            f"- Semantic search preview uses embeddings: `{semantic_validation['uses_embeddings']}`",
            f"- Semantic search preview auto partner selection: `{semantic_validation['automatic_partner_selection_allowed']}`",
            f"- Composition recipe validation valid: `{recipe_validation['valid']}`",
            f"- Composition recipe count: `{recipe_validation['recipe_count']}`",
            f"- Advisory planner validation status: `{planner_validation['status']}`",
            f"- Advisory planner executes: `{planner_validation['executes']}`",
            f"- Advisory planner auto partner selection: `{planner_validation['automatic_partner_selection_allowed']}`",
            f"- Promotion metadata enforced by default: `{validation['promotion_metadata_enforced']}`",
            "",
            "## Current Hierarchy",
            "",
            "```text",
        ]
    )
    for root in PRIMITIVE_HIERARCHY:
        lines.extend(_render_tree(root))
    lines.extend(
        [
            "```",
            "",
            "## Status Metadata",
            "",
            "| Status | Meaning |",
            "| --- | --- |",
        ]
    )
    for status in PRIMITIVE_HIERARCHY_STATUSES:
        lines.append(f"| `{status}` | {_escape(_STATUS_MEANINGS[status])} |")

    lines.extend(
        [
            "",
            "## Layer Details",
            "",
            "The sections below are generated from every hierarchy node. Users should",
            "first identify the behavior they need, then check status, backend",
            "coverage, capability tags, and claim boundaries.",
        ]
    )
    for root in PRIMITIVE_HIERARCHY:
        lines.extend(_render_layer_section(root))

    lines.extend(_render_recipe_section())
    lines.extend(_render_planner_section())

    lines.extend(
        [
            "",
            "## Controlled Discovery Facets",
            "",
            "| Facet |",
            "| --- |",
        ]
    )
    for tag in PRIMITIVE_CAPABILITY_TAGS:
        lines.append(f"| `{tag}` |")

    lines.extend(
        [
            "",
            "## App-Owned Boundary Exclusions",
            "",
            "The following semantics stay outside native engine primitive ownership:",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in APP_OWNED_BOUNDARY_EXCLUSIONS)
    lines.extend(
        [
            "",
            "## Promotion Guardrails",
            "",
            "- New primitive proposals must preserve app-independent semantics.",
            "- New promoted nodes with overlapping key facets must record",
            "  `considered_alternatives` and `distinct_from`.",
            "- Proposals must paste the `rtdsl.find_primitive(...)` alternatives",
            "  query that was run before creating the node.",
            "- `rtdsl.lint_new_primitive(candidate_node)` is the pre-addition",
            "  duplicate gate.",
            "- Promotion candidates already inserted in a local tree must run",
            "  `rtdsl.validate_primitive_hierarchy(..., enforce_promotion_metadata=True,",
            "  promotion_candidate_ids=(candidate_id,))`; the candidate-scoped gate",
            "  fails closed if near-duplicate metadata is missing.",
            "- Catalog generation and orchestration recipes are separate concerns;",
            "  this catalog records primitive contracts and discovery metadata only.",
            "",
            "## Claim Boundary",
            "",
            "This catalog does not authorize release readiness, public speedup wording,",
            "zero-copy claims, broad RT-core claims, paper-reproduction claims, or",
            "app-specific native engine logic.",
        ]
    )
    return "\n".join(lines) + "\n"


def _render_layer_section(root: PrimitiveHierarchyNode) -> list[str]:
    lines = [
        "",
        f"### {_escape(root.title)}",
        "",
        _escape(root.summary),
        "",
        "| Node | Status | Summary | Outputs | Depends on | Capabilities | Backends / partners | Boundary |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for node in _descendants(root):
        lines.append(
            "| "
            + " | ".join(
                (
                    f"`{_escape(node.id)}`",
                    f"`{_escape(node.status)}`",
                    _escape(node.summary),
                    _format_tuple(node.outputs),
                    _format_tuple(node.depends_on),
                    _format_tuple(node.capability_tags),
                    _format_backends_and_partners(node),
                    _escape(node.boundary or "-"),
                )
            )
            + " |"
        )
    discovery_nodes = [node for node in _descendants(root) if node.aliases or node.intent_phrases or node.reference_path]
    if discovery_nodes:
        lines.extend(
            [
                "",
                "Discovery metadata:",
                "",
                "| Node | Aliases | Intent phrases | Reference | Distinction |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for node in discovery_nodes:
            lines.append(
                "| "
                + " | ".join(
                    (
                        f"`{_escape(node.id)}`",
                        _format_tuple(node.aliases),
                        _format_tuple(node.intent_phrases),
                        _escape(node.reference_path or "-"),
                        _escape(node.distinct_from or "-"),
                    )
                )
                + " |"
            )
    return lines


def _render_recipe_section() -> list[str]:
    lines = [
        "",
        "## Composition Recipes",
        "",
        "Recipes are advisory composition metadata over existing primitive nodes.",
        "They do not execute, dispatch, auto-select partners, or authorize",
        "performance claims.",
        "",
        "| Recipe | Status | Summary | Primitive steps | Partner policy | Claim boundary |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for recipe in COMPOSITION_RECIPES:
        lines.append(
            "| "
            + " | ".join(
                (
                    f"`{_escape(recipe.id)}`",
                    f"`{_escape(recipe.status)}`",
                    _escape(recipe.summary),
                    _format_recipe_steps(recipe),
                    _escape(recipe.partner_policy),
                    _escape(recipe.claim_boundary),
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Recipe discovery metadata:",
            "",
            "| Recipe | Capabilities | Aliases | Intent phrases | Recommended when | Boundary |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for recipe in COMPOSITION_RECIPES:
        lines.append(
            "| "
            + " | ".join(
                (
                    f"`{_escape(recipe.id)}`",
                    _format_tuple(recipe.capability_tags),
                    _format_tuple(recipe.aliases),
                    _format_tuple(recipe.intent_phrases),
                    _escape(recipe.recommended_when or "-"),
                    _escape(recipe.boundary or "-"),
                )
            )
            + " |"
        )
    return lines


def _render_planner_section() -> list[str]:
    return [
        "",
        "## Advisory Planner",
        "",
        "The v2.7 planner is an explain-only layer over primitive discovery and",
        "composition recipes:",
        "",
        "```python",
        'rtdsl.plan_continuation(intent="nearest", shape="fixed_radius", dim="3d")',
        "rtdsl.validate_primitive_advisory_planner()",
        "```",
        "",
        "| Property | Value |",
        "| --- | --- |",
        f"| Planner version | `{PRIMITIVE_ADVISORY_PLANNER_VERSION}` |",
        f"| Executes or dispatches | `{PRIMITIVE_ADVISORY_PLANNER_EXECUTES}` |",
        f"| Auto-selects partners | `{PRIMITIVE_ADVISORY_PLANNER_AUTO_PARTNER_SELECTION_ALLOWED}` |",
        f"| Claim boundary | {_escape(PRIMITIVE_ADVISORY_PLANNER_CLAIM_BOUNDARY)} |",
        "",
        "Every returned plan exposes the matched recipe, each primitive step, each",
        "step's primitive status, non-stable step warnings, optional partner-support",
        "cells, and a `selected_partner=None` field. A plan can recommend",
        "primitive-first execution or list explicit partner options, but it cannot",
        "make the runtime choice for the user.",
    ]


def _render_tree(node: PrimitiveHierarchyNode, indent: int = 0) -> list[str]:
    prefix = "  " * indent
    lines = [f"{prefix}{node.title} ({node.id})"]
    for child in node.children:
        lines.extend(_render_tree(child, indent + 1))
    return lines


def _descendants(node: PrimitiveHierarchyNode) -> tuple[PrimitiveHierarchyNode, ...]:
    found: list[PrimitiveHierarchyNode] = []
    for child in node.children:
        found.append(child)
        found.extend(_descendants(child))
    return tuple(found)


def _format_backends_and_partners(node: PrimitiveHierarchyNode) -> str:
    pieces: list[str] = []
    if node.backends:
        pieces.append("backends: " + ", ".join(f"`{_escape(item)}`" for item in node.backends))
    if node.partner_ops:
        pieces.append("partner ops: " + ", ".join(f"`{_escape(item)}`" for item in node.partner_ops))
    return "<br>".join(pieces) if pieces else "-"


def _format_recipe_steps(recipe: CompositionRecipe) -> str:
    return "<br>".join(
        f"`{_escape(step.primitive_id)}` ({_escape(step.phase)}: {_escape(step.role)})"
        for step in recipe.steps
    )


def _format_tuple(values: object) -> str:
    if not values:
        return "-"
    if isinstance(values, tuple):
        return ", ".join(f"`{_escape(str(value))}`" for value in values)
    return _escape(str(values))


def _title_from_layer(layer: str) -> str:
    if layer == "execution_residency":
        return "Execution / Residency"
    if layer == "candidate_experimental":
        return "Candidate / Experimental"
    return " ".join(part.capitalize() for part in layer.split("_"))


def _escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


__all__ = [
    "PRIMITIVE_CATALOG_DATE",
    "PRIMITIVE_CATALOG_GENERATOR_VERSION",
    "render_primitive_catalog_markdown",
]
