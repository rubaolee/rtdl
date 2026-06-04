from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .primitive_hierarchy import PRIMITIVE_CAPABILITY_TAGS
from .primitive_hierarchy import find_primitive_hierarchy_node


COMPOSITION_RECIPE_VERSION = "rtdl.composition_recipe.v1"
COMPOSITION_RECIPE_STATUSES = ("advisory_recipe", "candidate_recipe")
COMPOSITION_RECIPE_AUTO_PARTNER_SELECTION_ALLOWED = False

_FACET_FAMILIES = ("intent", "shape", "dim", "output", "exactness", "keying")


@dataclass(frozen=True)
class CompositionRecipeStep:
    primitive_id: str
    role: str
    phase: str
    required: bool = True
    notes: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "primitive_id": self.primitive_id,
            "role": self.role,
            "phase": self.phase,
            "required": self.required,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class CompositionRecipe:
    id: str
    title: str
    status: str
    summary: str
    capability_tags: tuple[str, ...]
    steps: tuple[CompositionRecipeStep, ...]
    aliases: tuple[str, ...] = ()
    intent_phrases: tuple[str, ...] = ()
    recommended_when: str = ""
    partner_policy: str = ""
    claim_boundary: str = ""
    boundary: str = ""
    evidence_paths: tuple[str, ...] = ()
    automatic_partner_selection_allowed: bool = COMPOSITION_RECIPE_AUTO_PARTNER_SELECTION_ALLOWED

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "summary": self.summary,
            "capability_tags": self.capability_tags,
            "facets": _facet_map(self.capability_tags),
            "steps": tuple(step.to_dict() for step in self.steps),
            "aliases": self.aliases,
            "intent_phrases": self.intent_phrases,
            "recommended_when": self.recommended_when,
            "partner_policy": self.partner_policy,
            "claim_boundary": self.claim_boundary,
            "boundary": self.boundary,
            "evidence_paths": self.evidence_paths,
            "automatic_partner_selection_allowed": self.automatic_partner_selection_allowed,
        }


@dataclass(frozen=True)
class CompositionRecipeMatch:
    recipe_id: str
    title: str
    status: str
    score: int
    matched_on: tuple[str, ...]
    primitive_ids: tuple[str, ...]
    partner_policy: str
    claim_boundary: str

    def to_dict(self) -> dict[str, object]:
        return {
            "recipe_id": self.recipe_id,
            "title": self.title,
            "status": self.status,
            "score": self.score,
            "matched_on": self.matched_on,
            "primitive_ids": self.primitive_ids,
            "partner_policy": self.partner_policy,
            "claim_boundary": self.claim_boundary,
        }


COMPOSITION_RECIPES = (
    CompositionRecipe(
        id="recipe.hit_existence_to_count_summary",
        title="Hit Existence To Count Summary",
        status="advisory_recipe",
        summary="Use a hit predicate followed by a scalar count when witness rows are not needed.",
        capability_tags=(
            "intent:exists",
            "intent:count",
            "shape:generic",
            "output:mask",
            "output:scalar",
            "exactness:exact",
            "keying:none",
        ),
        aliases=("hit_count_recipe", "exists_then_count", "any_hit_count", "scalar_hit_count"),
        intent_phrases=(
            "count positive hit predicates without witness rows",
            "turn any hit flags into a scalar count summary",
        ),
        steps=(
            CompositionRecipeStep("traversal.any_hit", "predicate traversal", "traversal"),
            CompositionRecipeStep("traversal.count_hits", "scalar hit count", "reduction"),
        ),
        recommended_when="The caller needs a scalar count or boolean summary and not per-hit witness rows.",
        partner_policy="Primitive-first. No partner is required by this recipe.",
        claim_boundary="Counts accepted primitive hit flags only; this is not a whole-app speedup claim.",
        boundary="Caller-owned interpretation of the hit predicate stays outside the recipe.",
        evidence_paths=("docs/features/ray_tri_hitcount/README.md",),
    ),
    CompositionRecipe(
        id="recipe.fixed_radius_ranked_candidates",
        title="Fixed-Radius Ranked Candidate Summary",
        status="advisory_recipe",
        summary="Compose fixed-radius counts, bounded neighbor rows, and ranked summaries by query id.",
        capability_tags=(
            "intent:nearest",
            "intent:topk",
            "intent:count",
            "intent:collect_rows",
            "shape:fixed_radius",
            "dim:2d",
            "dim:3d",
            "output:rows",
            "output:grouped",
            "output:scalar",
            "exactness:bounded",
            "keying:by_query_id",
        ),
        aliases=("nearest_neighbor_recipe", "top_k_candidate_recipe", "fixed_radius_ranked_summary"),
        intent_phrases=(
            "find fixed radius neighbor candidates and summarize nearest quality",
            "rank bounded nearest candidates by query id",
        ),
        steps=(
            CompositionRecipeStep("traversal.fixed_radius_count_threshold", "count or prefilter candidate pressure", "traversal"),
            CompositionRecipeStep("rows.fixed_radius_neighbor_rows", "emit bounded neighbor rows", "row_emission"),
            CompositionRecipeStep("continuation.ranked_summary", "summarize candidate quality by query", "continuation"),
        ),
        recommended_when="The caller needs nearest/top-k style summaries and can bound candidate rows.",
        partner_policy=(
            "Primitive-first for traversal and row contracts. Explicit partner continuation is advisory "
            "only when the app chooses unfused ranking logic."
        ),
        claim_boundary="Ranking quality follows the selected row and continuation contract; no ANN or paper-reproduction claim is implied.",
        boundary="Application ranking policy and recall interpretation stay outside the native engine.",
        evidence_paths=("docs/features/fixed_radius_neighbors/README.md", "docs/features/knn_rows/README.md"),
    ),
    CompositionRecipe(
        id="recipe.ray_triangle_hit_stream_grouped_summary",
        title="Ray/Triangle Hit Stream To Grouped Summary",
        status="advisory_recipe",
        summary="Compose ray/triangle traversal, bounded hit streams, and grouped reductions over caller-provided keys.",
        capability_tags=(
            "intent:collect_rows",
            "intent:reduce",
            "intent:count",
            "shape:ray_triangle",
            "dim:3d",
            "output:rows",
            "output:grouped",
            "exactness:bounded",
            "exactness:exact",
            "keying:by_ray_id",
            "keying:by_group_id",
        ),
        aliases=(
            "ray_triangle_grouped_summary",
            "ray_triangle_grouped_primitive_summary",
            "hit_stream_grouped_reduction",
            "primitive_payload_summary",
        ),
        intent_phrases=(
            "reduce ray triangle primitive hits by group id",
            "collect ray primitive witnesses then summarize caller payloads",
        ),
        steps=(
            CompositionRecipeStep("traversal.any_hit", "ray/primitive traversal predicate", "traversal"),
            CompositionRecipeStep("rows.ray_triangle_hit_stream_3d", "emit app-free hit stream rows", "row_emission"),
            CompositionRecipeStep("reduction.ray_triangle_primitive_grouped_i64", "grouped primitive payload summary", "reduction"),
        ),
        recommended_when="The caller has ray/triangle hits and wants grouped summaries over caller-owned primitive payloads.",
        partner_policy=(
            "Primitive-first for supported grouped summaries. Explicit partners are allowed only for "
            "caller-chosen unfused continuation and are never auto-selected."
        ),
        claim_boundary="Not SQL, not a paper-system reproduction, and not a broad RT-core or whole-app claim.",
        boundary="Primitive-to-group mapping, payload values, predicates, and app rows remain app or partner code.",
        evidence_paths=("examples/v2_0/research_benchmarks/raydb_style/README.md",),
    ),
    CompositionRecipe(
        id="recipe.aabb_candidate_rows_to_refinement",
        title="AABB Candidate Rows To Caller Refinement",
        status="advisory_recipe",
        summary="Use generic AABB predicates and candidate rows before caller-owned exact refinement.",
        capability_tags=(
            "intent:intersection",
            "intent:membership",
            "intent:collect_rows",
            "shape:aabb",
            "dim:2d",
            "output:rows",
            "exactness:bounded",
            "keying:by_query_id",
        ),
        aliases=("aabb_candidate_recipe", "range_intersection_rows_recipe", "candidate_pair_rows"),
        intent_phrases=(
            "emit AABB candidate rows for exact caller refinement",
            "find range intersection candidates without owning app semantics",
        ),
        steps=(
            CompositionRecipeStep("traversal.aabb_range_intersects", "generic range predicate", "traversal"),
            CompositionRecipeStep("rows.aabb_range_intersection_rows", "emit candidate id rows", "row_emission"),
            CompositionRecipeStep("continuation.segmented_chunked_rows", "page large candidate streams when needed", "continuation"),
        ),
        recommended_when="The caller needs reusable candidate pairs and will perform exact domain refinement outside RTDL.",
        partner_policy="Primitive-first for candidate discovery. Any exact-refinement partner is caller selected.",
        claim_boundary="Candidate discovery only; no broad overlay, GIS, or whole-app claim is implied.",
        boundary="Exact refinement and domain scoring remain caller-owned.",
        evidence_paths=("docs/rtdl_primitive_catalog.md",),
    ),
    CompositionRecipe(
        id="recipe.point_closed_shape_boundary_event_selection",
        title="Point / Closed-Shape Boundary Event Selection",
        status="candidate_recipe",
        summary=(
            "Use a generic first-crossing boundary-event contract when membership "
            "classification needs a representative boundary event instead of only "
            "positive membership counts."
        ),
        capability_tags=(
            "intent:membership",
            "intent:nearest",
            "intent:collect_rows",
            "shape:closed_shape",
            "dim:2d",
            "output:columns",
            "output:witness",
            "exactness:exact",
            "keying:by_query_id",
        ),
        aliases=(
            "closed_shape_boundary_event_recipe",
            "first_crossing_membership_recipe",
            "boundary_event_selection_recipe",
        ),
        intent_phrases=(
            "select first boundary crossing events for point closed shape probes",
            "use boundary event columns before caller owned membership classification",
        ),
        steps=(
            CompositionRecipeStep("traversal.closest_hit", "representative boundary-event traversal", "traversal"),
            CompositionRecipeStep(
                "rows.point_closed_shape_boundary_event_columns",
                "emit typed boundary-event columns",
                "row_emission",
            ),
        ),
        recommended_when=(
            "The caller needs the selected boundary event itself and scalar membership "
            "counts are too coarse for the downstream classification."
        ),
        partner_policy=(
            "Primitive-first for boundary-event selection. Explicit partners remain "
            "caller-selected for classification or grouping after the event columns."
        ),
        claim_boundary=(
            "Candidate recipe only. It does not authorize release, paper-reproduction, "
            "RT-core speedup, true-zero-copy, or whole-app speedup claims."
        ),
        boundary=(
            "Boundary-event interpretation, parity policy, entity lookup, and final app "
            "membership classification remain caller-owned."
        ),
        evidence_paths=("docs/reports/goal3295_rayjoin_pip_boundary_selection_gap_diagnosis_2026-06-04.md",),
    ),
    CompositionRecipe(
        id="recipe.segmented_rows_to_grouped_reduction",
        title="Segmented Rows To Grouped Reduction",
        status="advisory_recipe",
        summary="Page large generic row streams and reduce them by explicit group ids.",
        capability_tags=(
            "intent:collect_rows",
            "intent:reduce",
            "shape:generic",
            "output:rows",
            "output:columns",
            "output:grouped",
            "exactness:bounded",
            "exactness:exact",
            "keying:by_group_id",
            "keying:by_query_id",
        ),
        aliases=("segmented_grouped_reduction", "chunked_rows_grouped_summary", "paged_row_reduce"),
        intent_phrases=(
            "page large row streams before grouped reduction",
            "avoid unbounded materialization while reducing rows by group id",
        ),
        steps=(
            CompositionRecipeStep("rows.generic_candidate_rows", "generic row stream contract", "row_emission"),
            CompositionRecipeStep("continuation.segmented_chunked_rows", "bounded row paging", "continuation"),
            CompositionRecipeStep("reduction.grouped", "grouped reductions over explicit keys", "reduction"),
        ),
        recommended_when="The caller has large generic row streams and explicit grouping keys.",
        partner_policy="Primitive-first when a fused grouped primitive fits; otherwise list explicit partner options for the caller.",
        claim_boundary="A recipe is not a dispatch path and does not authorize zero-copy or performance wording.",
        boundary="Group meaning, value semantics, and final app interpretation remain caller-owned.",
        evidence_paths=("docs/features/reduce_rows/README.md", "docs/rtdl_primitive_catalog.md"),
    ),
)


def recipe_index(*, status: str | None = None) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for recipe in COMPOSITION_RECIPES:
        if status is not None and recipe.status != status:
            continue
        rows.append(recipe.to_dict())
    return tuple(rows)


def describe_recipe(recipe_id: str) -> dict[str, object]:
    for recipe in COMPOSITION_RECIPES:
        if recipe.id == recipe_id:
            return recipe.to_dict()
    raise KeyError(f"unknown composition recipe: {recipe_id}")


def find_recipe(
    query: str | None = None,
    *,
    intent: str | None = None,
    shape: str | None = None,
    dim: str | None = None,
    output: str | None = None,
    exactness: str | None = None,
    keying: str | None = None,
    status: str | None = None,
    text: str | None = None,
) -> tuple[CompositionRecipeMatch, ...]:
    requested_facets = {
        "intent": intent,
        "shape": shape,
        "dim": dim,
        "output": output,
        "exactness": exactness,
        "keying": keying,
    }
    normalized_query = _normalize_text(" ".join(part for part in (query, text) if part))
    matches: list[CompositionRecipeMatch] = []
    for recipe in COMPOSITION_RECIPES:
        if status is not None and recipe.status != status:
            continue
        score = 0
        matched_on: list[str] = []
        tag_map = _facet_map(recipe.capability_tags)
        for family, value in requested_facets.items():
            if value is None:
                continue
            normalized_value = _normalize_token(value)
            if normalized_value in tag_map.get(family, ()):
                score += 10
                matched_on.append(f"{family}:{normalized_value}")
        if normalized_query:
            alias_hits = _text_hits(normalized_query, recipe.aliases)
            phrase_hits = _text_hits(normalized_query, recipe.intent_phrases)
            body_hits = _text_hits(
                normalized_query,
                (recipe.id, recipe.title, recipe.summary, *recipe.capability_tags),
            )
            if alias_hits:
                score += 7 * len(alias_hits)
                matched_on.extend(f"alias:{hit}" for hit in alias_hits)
            if phrase_hits:
                score += 5 * len(phrase_hits)
                matched_on.extend(f"intent_phrase:{hit}" for hit in phrase_hits)
            if body_hits:
                score += 2 * len(body_hits)
                matched_on.extend(f"text:{hit}" for hit in body_hits)
        if score:
            matches.append(
                CompositionRecipeMatch(
                    recipe_id=recipe.id,
                    title=recipe.title,
                    status=recipe.status,
                    score=score,
                    matched_on=tuple(dict.fromkeys(matched_on)),
                    primitive_ids=tuple(step.primitive_id for step in recipe.steps),
                    partner_policy=recipe.partner_policy,
                    claim_boundary=recipe.claim_boundary,
                )
            )
    return tuple(sorted(matches, key=lambda match: (-match.score, match.recipe_id)))


def validate_composition_recipes(
    recipes: Iterable[CompositionRecipe] = COMPOSITION_RECIPES,
) -> dict[str, object]:
    recipe_tuple = tuple(recipes)
    ids = [recipe.id for recipe in recipe_tuple]
    duplicate_ids = tuple(sorted({recipe_id for recipe_id in ids if ids.count(recipe_id) > 1}))
    unknown_statuses = tuple(sorted({recipe.status for recipe in recipe_tuple if recipe.status not in COMPOSITION_RECIPE_STATUSES}))
    unknown_capability_tags = tuple(
        sorted(
            {
                tag
                for recipe in recipe_tuple
                for tag in recipe.capability_tags
                if tag not in PRIMITIVE_CAPABILITY_TAGS
            }
        )
    )
    missing_primitive_steps: list[tuple[str, str]] = []
    for recipe in recipe_tuple:
        for step in recipe.steps:
            try:
                find_primitive_hierarchy_node(step.primitive_id)
            except KeyError:
                missing_primitive_steps.append((recipe.id, step.primitive_id))
    auto_partner_selection = tuple(
        sorted(recipe.id for recipe in recipe_tuple if recipe.automatic_partner_selection_allowed)
    )
    missing_boundaries = tuple(
        sorted(
            recipe.id
            for recipe in recipe_tuple
            if not (recipe.partner_policy and recipe.claim_boundary and recipe.boundary)
        )
    )
    return {
        "version": COMPOSITION_RECIPE_VERSION,
        "valid": (
            not duplicate_ids
            and not unknown_statuses
            and not unknown_capability_tags
            and not missing_primitive_steps
            and not auto_partner_selection
            and not missing_boundaries
        ),
        "recipe_count": len(recipe_tuple),
        "duplicate_ids": duplicate_ids,
        "unknown_statuses": unknown_statuses,
        "unknown_capability_tags": unknown_capability_tags,
        "missing_primitive_steps": tuple(missing_primitive_steps),
        "automatic_partner_selection_allowed": auto_partner_selection,
        "missing_boundaries": missing_boundaries,
    }


def _facet_map(tags: Iterable[str]) -> dict[str, tuple[str, ...]]:
    by_family: dict[str, list[str]] = {}
    for tag in tags:
        if ":" not in tag:
            continue
        family, value = tag.split(":", 1)
        by_family.setdefault(family, []).append(value)
    return {family: tuple(sorted(set(values))) for family, values in by_family.items()}


def _normalize_token(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _normalize_text(value: str) -> str:
    return _normalize_token(value).replace("/", "_")


def _text_hits(query: str, values: Iterable[str]) -> tuple[str, ...]:
    hits: list[str] = []
    query_parts = tuple(part for part in query.split("_") if part)
    for value in values:
        normalized = _normalize_text(value)
        if not normalized:
            continue
        if normalized in query or query in normalized:
            hits.append(value)
            continue
        if query_parts and all(part in normalized for part in query_parts):
            hits.append(value)
    return tuple(hits)


__all__ = [
    "COMPOSITION_RECIPE_AUTO_PARTNER_SELECTION_ALLOWED",
    "COMPOSITION_RECIPE_STATUSES",
    "COMPOSITION_RECIPE_VERSION",
    "COMPOSITION_RECIPES",
    "CompositionRecipe",
    "CompositionRecipeMatch",
    "CompositionRecipeStep",
    "describe_recipe",
    "find_recipe",
    "recipe_index",
    "validate_composition_recipes",
]
