from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any


@dataclass(frozen=True)
class PredicateClause:
    field: str
    op: str
    value: Any
    value_hi: Any | None = None


@dataclass(frozen=True)
class PredicateBundle:
    clauses: tuple[PredicateClause, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class GroupedAggregateQuery:
    predicates: tuple[PredicateClause, ...] = field(default_factory=tuple)
    group_keys: tuple[str, ...] = field(default_factory=tuple)
    value_field: str | None = None


def normalize_predicate_bundle(payload) -> PredicateBundle:
    if isinstance(payload, PredicateBundle):
        _validate_predicate_bundle(payload)
        return payload
    if isinstance(payload, dict):
        payload = payload.get("clauses", ())
    clauses = tuple(_normalize_predicate_clause(item) for item in payload)
    bundle = PredicateBundle(clauses=clauses)
    _validate_predicate_bundle(bundle)
    return bundle


def normalize_grouped_query(payload) -> GroupedAggregateQuery:
    if isinstance(payload, GroupedAggregateQuery):
        return payload
    if not isinstance(payload, dict):
        raise ValueError("grouped query input must be a mapping or GroupedAggregateQuery")
    predicates = tuple(_normalize_predicate_clause(item) for item in payload.get("predicates", ()))
    group_keys = tuple(str(value) for value in payload.get("group_keys", ()))
    value_field = payload.get("value_field")
    if value_field is not None:
        value_field = str(value_field)
    return GroupedAggregateQuery(
        predicates=predicates,
        group_keys=group_keys,
        value_field=value_field,
    )


def normalize_denorm_table(payload) -> tuple[dict[str, Any], ...]:
    if isinstance(payload, dict):
        payload = payload.get("rows", ())
    rows = []
    for index, record in enumerate(payload):
        if not isinstance(record, dict):
            raise ValueError(f"denorm table row {index} must be a mapping")
        normalized = {str(key): value for key, value in record.items()}
        if "row_id" not in normalized:
            raise ValueError(f"denorm table row {index} is missing required field `row_id`")
        rows.append(normalized)
    return tuple(rows)


def conjunctive_scan_cpu(
    table_rows: tuple[dict[str, Any], ...],
    predicates: PredicateBundle,
) -> tuple[dict[str, Any], ...]:
    matched = []
    for row in table_rows:
        if all(_row_matches_clause(row, clause) for clause in predicates.clauses):
            matched.append({"row_id": int(row["row_id"])})
    return tuple(matched)


def grouped_count_cpu(
    table_rows: tuple[dict[str, Any], ...],
    query: GroupedAggregateQuery,
) -> tuple[dict[str, Any], ...]:
    if not query.group_keys:
        raise ValueError("grouped_count requires at least one group key")
    counts: dict[tuple[Any, ...], int] = {}
    for row in table_rows:
        if all(_row_matches_clause(row, clause) for clause in query.predicates):
            key = tuple(row[group_key] for group_key in query.group_keys)
            counts[key] = counts.get(key, 0) + 1
    rows = []
    for key in sorted(counts):
        result = {group_key: key[index] for index, group_key in enumerate(query.group_keys)}
        result["count"] = counts[key]
        rows.append(result)
    return tuple(rows)


def grouped_sum_cpu(
    table_rows: tuple[dict[str, Any], ...],
    query: GroupedAggregateQuery,
) -> tuple[dict[str, Any], ...]:
    if not query.group_keys:
        raise ValueError("grouped_sum requires at least one group key")
    if not query.value_field:
        raise ValueError("grouped_sum requires a value_field")
    sums: dict[tuple[Any, ...], float] = {}
    for row in table_rows:
        if all(_row_matches_clause(row, clause) for clause in query.predicates):
            key = tuple(row[group_key] for group_key in query.group_keys)
            sums[key] = sums.get(key, 0.0) + float(row[query.value_field])
    rows = []
    for key in sorted(sums):
        result = {group_key: key[index] for index, group_key in enumerate(query.group_keys)}
        total = sums[key]
        if float(total).is_integer():
            result["sum"] = int(total)
        else:
            result["sum"] = total
        rows.append(result)
    return tuple(rows)


def _normalize_predicate_clause(item) -> PredicateClause:
    if isinstance(item, PredicateClause):
        return item
    if isinstance(item, dict):
        field_name = str(item["field"])
        op = str(item["op"])
        value = item["value"]
        value_hi = item.get("value_hi")
        return PredicateClause(field=field_name, op=op, value=value, value_hi=value_hi)
    if isinstance(item, tuple):
        if len(item) == 3:
            field_name, op, value = item
            return PredicateClause(field=str(field_name), op=str(op), value=value)
        if len(item) == 4:
            field_name, op, value, value_hi = item
            return PredicateClause(field=str(field_name), op=str(op), value=value, value_hi=value_hi)
    raise ValueError("predicate clause must be a PredicateClause, mapping, or tuple")


def _validate_predicate_bundle(bundle: PredicateBundle) -> None:
    for clause in bundle.clauses:
        if clause.op not in {"eq", "lt", "le", "gt", "ge", "between"}:
            raise ValueError(f"unsupported predicate operator: {clause.op}")
        if clause.op == "between" and clause.value_hi is None:
            raise ValueError("between predicate requires value_hi")


def _row_matches_clause(row: dict[str, Any], clause: PredicateClause) -> bool:
    if clause.field not in row:
        raise ValueError(f"row is missing predicate field `{clause.field}`")
    value = row[clause.field]
    if clause.op == "eq":
        return value == clause.value
    if clause.op == "lt":
        return value < clause.value
    if clause.op == "le":
        return value <= clause.value
    if clause.op == "gt":
        return value > clause.value
    if clause.op == "ge":
        return value >= clause.value
    if clause.op == "between":
        return clause.value <= value <= clause.value_hi
    raise ValueError(f"unsupported predicate operator: {clause.op}")
