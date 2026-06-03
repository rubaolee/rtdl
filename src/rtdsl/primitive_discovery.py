from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .primitive_hierarchy import PRIMITIVE_DISCOVERY_VERSION
from .primitive_hierarchy import PrimitiveHierarchyNode
from .primitive_hierarchy import find_primitive_hierarchy_node
from .primitive_hierarchy import iter_primitive_hierarchy_nodes


_FACET_FAMILIES = ("intent", "shape", "dim", "output", "exactness", "keying")
_DUPLICATE_KEY_FAMILIES = ("intent", "shape", "dim", "output", "keying")


@dataclass(frozen=True)
class PrimitiveDiscoveryMatch:
    node_id: str
    title: str
    status: str
    layer: str
    score: int
    matched_on: tuple[str, ...]
    backends: tuple[str, ...]
    reference_path: str
    compose_hint: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "node_id": self.node_id,
            "title": self.title,
            "status": self.status,
            "layer": self.layer,
            "score": self.score,
            "matched_on": self.matched_on,
            "backends": self.backends,
            "reference_path": self.reference_path,
            "compose_hint": self.compose_hint,
        }


def primitive_index(*, status: str | None = None) -> tuple[dict[str, object], ...]:
    """Return one flat discovery row per primitive hierarchy node."""

    rows: list[dict[str, object]] = []
    for node in iter_primitive_hierarchy_nodes():
        if status is not None and node.status != status:
            continue
        rows.append(_index_row(node))
    return tuple(rows)


def describe_primitive(node_id: str) -> dict[str, object]:
    """Return the discovery record for one primitive node."""

    node = find_primitive_hierarchy_node(node_id)
    row = _index_row(node)
    row["depends_on"] = node.depends_on
    row["children"] = tuple(child.id for child in node.children)
    return row


def find_primitive(
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
) -> tuple[PrimitiveDiscoveryMatch, ...]:
    """Find primitives by controlled facets plus alias/phrase text.

    This is deliberately deterministic and simple: exact facet hits outrank
    alias/intent-phrase hits, which outrank summary/title substring hits.
    """

    requested_facets = {
        "intent": intent,
        "shape": shape,
        "dim": dim,
        "output": output,
        "exactness": exactness,
        "keying": keying,
    }
    normalized_query = _normalize_text(" ".join(part for part in (query, text) if part))
    matches: list[PrimitiveDiscoveryMatch] = []

    for node in iter_primitive_hierarchy_nodes():
        if status is not None and node.status != status:
            continue

        score = 0
        matched_on: list[str] = []
        tag_map = _facet_map(node.capability_tags)
        for family, value in requested_facets.items():
            if value is None:
                continue
            normalized_value = _normalize_token(value)
            if normalized_value in tag_map.get(family, ()):
                score += 10
                matched_on.append(f"{family}:{normalized_value}")

        if normalized_query:
            alias_hits = _text_hits(normalized_query, node.aliases)
            phrase_hits = _text_hits(normalized_query, node.intent_phrases)
            body_hits = _text_hits(
                normalized_query,
                (node.id, node.title, node.summary, *node.outputs, *node.capability_tags),
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
                PrimitiveDiscoveryMatch(
                    node_id=node.id,
                    title=node.title,
                    status=node.status,
                    layer=node.layer,
                    score=score,
                    matched_on=tuple(dict.fromkeys(matched_on)),
                    backends=node.backends,
                    reference_path=node.reference_path,
                    compose_hint=_compose_hint(node),
                )
            )

    return tuple(sorted(matches, key=lambda match: (-match.score, match.layer, match.node_id)))


def lint_new_primitive(
    candidate: PrimitiveHierarchyNode,
    *,
    existing_nodes: Iterable[PrimitiveHierarchyNode] | None = None,
) -> dict[str, object]:
    """Fail closed when a promoted node looks like an existing primitive.

    The lint is intentionally metadata-only. It does not mutate the hierarchy and
    can be used in design reports before a primitive is added.
    """

    existing = tuple(existing_nodes or iter_primitive_hierarchy_nodes())
    candidate_map = _facet_map(candidate.capability_tags)
    nearest: list[tuple[str, int, tuple[str, ...]]] = []
    for node in existing:
        overlap: list[str] = []
        existing_map = _facet_map(node.capability_tags)
        for family in _DUPLICATE_KEY_FAMILIES:
            shared = sorted(set(candidate_map.get(family, ())) & set(existing_map.get(family, ())))
            overlap.extend(f"{family}:{value}" for value in shared)
        if overlap:
            nearest.append((node.id, len(overlap), tuple(overlap)))

    nearest_sorted = tuple(
        {
            "node_id": node_id,
            "shared_key_facets": shared,
            "overlap_score": score,
        }
        for node_id, score, shared in sorted(nearest, key=lambda item: (-item[1], item[0]))[:5]
    )

    candidate_key_family_count = sum(1 for family in _DUPLICATE_KEY_FAMILIES if candidate_map.get(family))
    possible_duplicates = tuple(
        entry
        for entry in nearest_sorted
        if int(entry["overlap_score"]) >= max(3, candidate_key_family_count)
    )
    promotion_metadata_present = bool(candidate.considered_alternatives and candidate.distinct_from.strip())
    errors: list[str] = []
    if possible_duplicates and not promotion_metadata_present:
        errors.append(
            "possible duplicate primitive; set considered_alternatives and distinct_from or reuse an existing node"
        )

    return {
        "version": PRIMITIVE_DISCOVERY_VERSION,
        "valid": not errors,
        "candidate_id": candidate.id,
        "errors": tuple(errors),
        "nearest": nearest_sorted,
        "possible_duplicates": possible_duplicates,
        "promotion_metadata_present": promotion_metadata_present,
    }


def _index_row(node: PrimitiveHierarchyNode) -> dict[str, object]:
    facets = _facet_map(node.capability_tags)
    return {
        "id": node.id,
        "title": node.title,
        "layer": node.layer,
        "status": node.status,
        "summary": node.summary,
        "outputs": node.outputs,
        "boundary": node.boundary,
        "capability_tags": node.capability_tags,
        "facets": {family: facets.get(family, ()) for family in _FACET_FAMILIES},
        "aliases": node.aliases,
        "intent_phrases": node.intent_phrases,
        "reference_path": node.reference_path,
        "backends": node.backends,
        "partner_ops": node.partner_ops,
        "considered_alternatives": node.considered_alternatives,
        "distinct_from": node.distinct_from,
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


def _compose_hint(node: PrimitiveHierarchyNode) -> str:
    if node.depends_on:
        return "compose in dependency order: " + " -> ".join(node.depends_on + (node.id,))
    return ""


__all__ = [
    "PrimitiveDiscoveryMatch",
    "describe_primitive",
    "find_primitive",
    "lint_new_primitive",
    "primitive_index",
]
