"""Provider-independent family-schema admission and compilation planning.

This module deliberately contains no application names and no dispatch on
concrete geometry families.  A family shape, a protocol instance, and an inert
behavior/template binding produce a target-neutral canonical plan.  Provider
execution is a separate concern and is not part of any identity in this
module.

The public values are immutable.  Their normative documents are retained only
as canonical bytes, and :attr:`document` returns a freshly decoded, recursively
read-only view.  Every identity is SHA-256 over a distinct domain separator and
canonical JSON bytes.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
import copy
import hashlib
import json
import re
from types import MappingProxyType
from typing import Any


FAMILY_SHAPE_SCHEMA = "rtdl.family_shape.v1"
PROTOCOL_INSTANCE_SCHEMA = "rtdl.protocol_instance.v1"
FAMILY_ADMISSION_SCHEMA = "rtdl.family_admission.v1"
FAMILY_COMPILATION_PLAN_SCHEMA = "rtdl.family_compilation_plan.v1"

_DOMAIN_SEPARATORS = {
    FAMILY_SHAPE_SCHEMA: b"rtdl.family_shape.v1\0",
    PROTOCOL_INSTANCE_SCHEMA: b"rtdl.protocol_instance.v1\0",
    FAMILY_ADMISSION_SCHEMA: b"rtdl.family_admission.v1\0",
    FAMILY_COMPILATION_PLAN_SCHEMA: b"rtdl.family_compilation_plan.v1\0",
}

_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9_.:-]{0,127}\Z")
_F32_BITS = re.compile(r"f32:[0-9a-f]{8}\Z")
_F64_BITS = re.compile(r"f64:[0-9a-f]{16}\Z")

_BINDER_FIELDS = {
    "parameter_id": "p",
    "node_id": "n",
    "buffer_id": "b",
    "channel_id": "h",
    "event_id": "e",
    "state_id": "s",
    "step_id": "o",
}
_REFERENCE_FIELDS = {
    "parameter_ref": "p",
    "node_ref": "n",
    "buffer_ref": "b",
    "channel_ref": "h",
    "index_channel_ref": "h",
    "event_ref": "e",
    "state_ref": "s",
    "from_state": "s",
    "to_state": "s",
    "initial_state": "s",
    "step_ref": "o",
}
_SET_REFERENCE_FIELDS = {"terminal_states": "s"}
_SHAPE_SET_FIELDS = {
    "capabilities",
    "allowed_effects",
    "required_effects",
    "terminal_states",
    "identity_bind_set",
    "algebra_properties",
}
_FORBIDDEN_NORMATIVE_KEYS = {
    "application_name",
    "dataset_name",
    "display_name",
    "file_path",
    "timestamp",
}

_ROLE_EFFECTS = {
    "bounds": {"aabb"},
    "make_ray": {"trace_request"},
    "intersection": {"hit", "no_hit"},
    "any_hit": {"accept_continue", "ignore", "terminate"},
    "closest_hit": {"payload"},
    "miss": {"payload"},
    "finalize": {"output"},
}
_VALUE_TYPES = {
    "bool",
    "u32",
    "u64",
    "i32",
    "i64",
    "f32_bits",
    "f64_bits",
    "u32x2",
    "u32x3",
    "vec3f_bits",
    "ray3f_bits",
    "aabb3f_bits",
    "namespaced_identifier",
}
_PARAMETER_TYPES = {
    "bool",
    "u32",
    "u64",
    "i32",
    "i64",
    "f32_bits",
    "f64_bits",
    "namespaced_identifier",
}
_RESULT_OPERATORS: dict[str, frozenset[str]] = {
    "emit_record": frozenset({"event_ref"}),
    "filter": frozenset({"event_ref", "predicate"}),
    "keyed_identical_deduplicate": frozenset({"key_fields"}),
    "lexicographic_sort": frozenset({"key_fields"}),
    "capacity_guard": frozenset({"parameter_ref"}),
    "checked_i64_sum": frozenset({"event_ref"}),
    "checked_u64_sum": frozenset({"event_ref"}),
    "checked_u64_product_sum": frozenset({"event_ref"}),
    "commit_ir_output": frozenset(),
    "commit_collected_rows": frozenset(),
    "commit_checked_reduction": frozenset(),
}
_PROVIDER_OPERATOR = "provider_operator"
_COMMIT_OPERATORS = {
    "commit_ir_output",
    "commit_collected_rows",
    "commit_checked_reduction",
}
_LIFECYCLE_STATE_KINDS = {
    "prepared",
    "launched",
    "status_ok",
    "status_failed",
    "committed",
}
_LIFECYCLE_EVENTS = {
    "launch",
    "observe_status_ok",
    "observe_status_failure",
    "copy_output",
}
_RESOURCE_LIMIT_KEYS = {
    "max_payload_u32_slots",
    "max_attribute_u32_slots",
    "max_trace_depth",
    "max_callable_depth",
    "max_static_loop_trip_count",
    "max_total_static_iterations",
    "max_helper_call_depth",
}

class FamilySchemaError(ValueError):
    """Fail-closed diagnostic with a stable code and document path."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"{code}:{path}:{message}")


def _fail(code: str, path: str, message: str) -> None:
    raise FamilySchemaError(code, path, message)


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail("FS001_DUPLICATE_JSON_KEY", "$", key)
        result[key] = value
    return result


def _parse_document(value: object, path: str = "$") -> dict[str, Any]:
    if isinstance(value, (bytes, bytearray, memoryview)):
        try:
            text = bytes(value).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise FamilySchemaError(
                "FS002_DOCUMENT_ENCODING", path, "document is not UTF-8"
            ) from exc
        return _parse_json_text(text, path)
    if isinstance(value, str):
        return _parse_json_text(value, path)
    if not isinstance(value, Mapping):
        _fail("FS003_DOCUMENT_TYPE", path, "document must be a mapping or JSON")
    # Round-tripping also detaches custom Mapping implementations and rejects
    # values outside the normative JSON subset before validation proceeds.
    _validate_normative_value(value, path)
    detached = json.loads(
        json.dumps(value, sort_keys=False, ensure_ascii=True, allow_nan=False)
    )
    if not isinstance(detached, dict):  # pragma: no cover - guarded above.
        _fail("FS003_DOCUMENT_TYPE", path, "document root must be an object")
    return detached


def _parse_json_text(text: str, path: str) -> dict[str, Any]:
    try:
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=lambda token: _fail(
                "FS004_NONFINITE_JSON", path, token
            ),
        )
    except FamilySchemaError:
        raise
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise FamilySchemaError(
            "FS005_INVALID_JSON", path, "invalid JSON document"
        ) from exc
    if not isinstance(value, dict):
        _fail("FS003_DOCUMENT_TYPE", path, "document root must be an object")
    return value


def _validate_normative_value(value: object, path: str = "$", depth: int = 0) -> None:
    if depth > 64:
        _fail("FS006_DEPTH", path, "document is too deeply nested")
    if value is None or isinstance(value, (str, bool)) or type(value) is int:
        return
    if isinstance(value, float):
        _fail("FS007_FLOAT", path, "JSON floats are forbidden; use exact bit text")
    if isinstance(value, Mapping):
        if len(value) > 4096:
            _fail("FS008_SIZE", path, "object is too large")
        for key, item in value.items():
            if not isinstance(key, str) or not key.isascii():
                _fail("FS009_KEY", path, "normative keys must be ASCII strings")
            if key in _FORBIDDEN_NORMATIVE_KEYS:
                _fail("FS010_NONNORMATIVE_KEY", f"{path}.{key}", key)
            _validate_normative_value(item, f"{path}.{key}", depth + 1)
        return
    if isinstance(value, (list, tuple)):
        if len(value) > 4096:
            _fail("FS008_SIZE", path, "array is too large")
        for index, item in enumerate(value):
            _validate_normative_value(item, f"{path}[{index}]", depth + 1)
        return
    _fail("FS011_VALUE_TYPE", path, f"unsupported {type(value).__name__}")


def _canonical_bytes(value: object) -> bytes:
    _validate_normative_value(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _domain_digest(schema_id: str, canonical: bytes) -> str:
    try:
        domain = _DOMAIN_SEPARATORS[schema_id]
    except KeyError as exc:  # pragma: no cover - all callers use constants.
        raise FamilySchemaError(
            "FS012_IDENTITY_DOMAIN", "schema", schema_id
        ) from exc
    return hashlib.sha256(domain + canonical).hexdigest()


def _readonly(value: object) -> object:
    if isinstance(value, dict):
        return MappingProxyType({key: _readonly(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_readonly(item) for item in value)
    return value


def _object(
    value: object,
    path: str,
    required: set[str] | frozenset[str],
    optional: set[str] | frozenset[str] = frozenset(),
) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail("FS013_OBJECT", path, "must be an object")
    missing = set(required) - set(value)
    extra = set(value) - set(required) - set(optional)
    if missing:
        _fail("FS014_MISSING_KEYS", path, repr(sorted(missing)))
    if extra:
        _fail("FS015_UNKNOWN_KEYS", path, repr(sorted(extra)))
    return value


def _array(value: object, path: str, *, nonempty: bool = False) -> list[Any]:
    if not isinstance(value, list):
        _fail("FS016_ARRAY", path, "must be an array")
    if nonempty and not value:
        _fail("FS017_EMPTY", path, "must not be empty")
    return value


def _string(value: object, path: str, *, identifier: bool = False) -> str:
    if not isinstance(value, str) or not value or not value.isascii():
        _fail("FS018_STRING", path, "must be a non-empty ASCII string")
    if identifier and _IDENTIFIER.fullmatch(value) is None:
        _fail("FS019_IDENTIFIER", path, "must be a bounded identifier")
    return value


def _integer(
    value: object,
    path: str,
    *,
    minimum: int = 0,
    maximum: int = (1 << 63) - 1,
) -> int:
    if type(value) is not int:
        _fail("FS020_INTEGER", path, "must be an integer, not bool or float")
    if value < minimum or value > maximum:
        _fail("FS021_INTEGER_RANGE", path, f"outside [{minimum}, {maximum}]")
    return value


def _boolean(value: object, path: str) -> bool:
    if type(value) is not bool:
        _fail("FS022_BOOLEAN", path, "must be a boolean")
    return value


def _digest(value: object, path: str) -> str:
    text = _string(value, path)
    if _HEX64.fullmatch(text) is None:
        _fail("FS023_SHA256", path, "must be a lowercase SHA-256 digest")
    return text


def _unique_identifiers(
    value: object,
    path: str,
    *,
    nonempty: bool = False,
    allowed: set[str] | None = None,
) -> list[str]:
    rows = _array(value, path, nonempty=nonempty)
    result = [
        _string(item, f"{path}[{index}]", identifier=True)
        for index, item in enumerate(rows)
    ]
    if len(result) != len(set(result)):
        _fail("FS024_DUPLICATE", path, "contains duplicate values")
    if allowed is not None and not set(result) <= allowed:
        _fail("FS025_UNSUPPORTED", path, repr(sorted(set(result) - allowed)))
    return result


def _walk_dicts(value: object) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from _walk_dicts(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_dicts(item)


def _validate_local_references(value: dict[str, Any]) -> None:
    declared: dict[str, set[str]] = {
        prefix: set() for prefix in _BINDER_FIELDS.values()
    }
    for obj in _walk_dicts(value):
        for field, prefix in _BINDER_FIELDS.items():
            if field not in obj:
                continue
            name = _string(obj[field], field, identifier=True)
            if name in declared[prefix]:
                _fail("FS026_DUPLICATE_BINDER", field, name)
            declared[prefix].add(name)
    for obj in _walk_dicts(value):
        for field, prefix in _REFERENCE_FIELDS.items():
            if field in obj and obj[field] not in declared[prefix]:
                _fail("FS027_DANGLING_REFERENCE", field, repr(obj[field]))
        for field, prefix in _SET_REFERENCE_FIELDS.items():
            if field not in obj:
                continue
            for item in _array(obj[field], field):
                if item not in declared[prefix]:
                    _fail("FS027_DANGLING_REFERENCE", field, repr(item))


def _validate_resource_limits(value: object, path: str) -> dict[str, int]:
    limits = _object(value, path, _RESOURCE_LIMIT_KEYS)
    result = {
        "max_payload_u32_slots": _integer(
            limits["max_payload_u32_slots"],
            f"{path}.max_payload_u32_slots",
            maximum=32,
        ),
        "max_attribute_u32_slots": _integer(
            limits["max_attribute_u32_slots"],
            f"{path}.max_attribute_u32_slots",
            maximum=8,
        ),
        "max_trace_depth": _integer(
            limits["max_trace_depth"],
            f"{path}.max_trace_depth",
            minimum=1,
            maximum=31,
        ),
        "max_callable_depth": _integer(
            limits["max_callable_depth"],
            f"{path}.max_callable_depth",
            maximum=31,
        ),
        "max_static_loop_trip_count": _integer(
            limits["max_static_loop_trip_count"],
            f"{path}.max_static_loop_trip_count",
            minimum=1,
            maximum=1 << 20,
        ),
        "max_total_static_iterations": _integer(
            limits["max_total_static_iterations"],
            f"{path}.max_total_static_iterations",
            minimum=1,
            maximum=1 << 24,
        ),
        "max_helper_call_depth": _integer(
            limits["max_helper_call_depth"],
            f"{path}.max_helper_call_depth",
            maximum=1024,
        ),
    }
    return result


def _validate_family_shape(shape: dict[str, Any]) -> None:
    _validate_normative_value(shape)
    root = _object(
        shape,
        "$",
        {
            "schema",
            "parameters",
            "graph_nodes",
            "buffers",
            "channels",
            "views",
            "events",
            "callback",
            "physical",
            "result_pipeline",
            "continuation",
            "capabilities",
            "identity_bind_set",
            "resource_limits",
        },
    )
    if root["schema"] != FAMILY_SHAPE_SCHEMA:
        _fail("FS028_SCHEMA", "$.schema", FAMILY_SHAPE_SCHEMA)

    for index, raw in enumerate(_array(root["parameters"], "$.parameters")):
        path = f"$.parameters[{index}]"
        item = _object(raw, path, {"parameter_id", "type"}, {"minimum", "maximum"})
        _string(item["parameter_id"], f"{path}.parameter_id", identifier=True)
        if item["type"] not in _PARAMETER_TYPES:
            _fail("FS025_UNSUPPORTED", f"{path}.type", repr(item["type"]))
        if "minimum" in item:
            _integer(item["minimum"], f"{path}.minimum", minimum=-(1 << 63))
        if "maximum" in item:
            _integer(item["maximum"], f"{path}.maximum", minimum=-(1 << 63))
        if item.get("minimum", -(1 << 63)) > item.get("maximum", (1 << 63) - 1):
            _fail("FS029_BOUNDS", path, "minimum exceeds maximum")

    nodes = _array(root["graph_nodes"], "$.graph_nodes", nonempty=True)
    node_children: dict[str, list[str]] = {}
    node_ordinals: list[int] = []
    for index, raw in enumerate(nodes):
        path = f"$.graph_nodes[{index}]"
        item = _object(
            raw,
            path,
            {
                "node_id",
                "kind",
                "primitive_kind",
                "ordinal",
                "update_policy",
                "sbt_record_stride",
                "children",
            },
        )
        node_id = _string(item["node_id"], f"{path}.node_id", identifier=True)
        kind = _string(item["kind"], f"{path}.kind", identifier=True)
        primitive = _string(
            item["primitive_kind"], f"{path}.primitive_kind", identifier=True
        )
        if kind not in {"gas", "ias"}:
            _fail("FS025_UNSUPPORTED", f"{path}.kind", kind)
        if item["update_policy"] not in {"static", "refit", "rebuild"}:
            _fail("FS025_UNSUPPORTED", f"{path}.update_policy", repr(item["update_policy"]))
        node_ordinals.append(_integer(item["ordinal"], f"{path}.ordinal"))
        _integer(item["sbt_record_stride"], f"{path}.sbt_record_stride", minimum=1)
        children: list[str] = []
        for child_index, child_raw in enumerate(
            _array(item["children"], f"{path}.children")
        ):
            child_path = f"{path}.children[{child_index}]"
            child = _object(child_raw, child_path, {"node_ref"})
            children.append(
                _string(child["node_ref"], f"{child_path}.node_ref", identifier=True)
            )
        if kind == "gas" and (primitive == "none" or children):
            _fail("FS030_GRAPH_SHAPE", path, "gas must be a primitive leaf")
        if kind == "ias" and (primitive != "none" or not children):
            _fail("FS030_GRAPH_SHAPE", path, "ias must contain children and no primitive")
        node_children[node_id] = children
    if node_ordinals != list(range(len(node_ordinals))):
        _fail("FS031_ORDINALS", "$.graph_nodes", "must be contiguous and ordered")

    buffer_ordinals: list[int] = []
    for index, raw in enumerate(_array(root["buffers"], "$.buffers")):
        path = f"$.buffers[{index}]"
        item = _object(
            raw,
            path,
            {
                "buffer_id",
                "ordinal",
                "semantic",
                "domain",
                "value_type",
                "access",
                "count_relation",
                "alignment_bytes",
                "contiguous",
                "residency",
            },
        )
        _string(item["buffer_id"], f"{path}.buffer_id", identifier=True)
        buffer_ordinals.append(_integer(item["ordinal"], f"{path}.ordinal"))
        _string(item["semantic"], f"{path}.semantic", identifier=True)
        if item["domain"] not in {"primitive", "query", "launch", "result"}:
            _fail("FS025_UNSUPPORTED", f"{path}.domain", repr(item["domain"]))
        if item["value_type"] not in _VALUE_TYPES:
            _fail("FS025_UNSUPPORTED", f"{path}.value_type", repr(item["value_type"]))
        if item["access"] not in {"read_only", "write_only", "read_write"}:
            _fail("FS025_UNSUPPORTED", f"{path}.access", repr(item["access"]))
        _string(item["count_relation"], f"{path}.count_relation", identifier=True)
        alignment = _integer(
            item["alignment_bytes"], f"{path}.alignment_bytes", minimum=1, maximum=4096
        )
        if alignment & (alignment - 1):
            _fail("FS032_ALIGNMENT", f"{path}.alignment_bytes", "must be a power of two")
        _boolean(item["contiguous"], f"{path}.contiguous")
        if item["residency"] not in {"device", "host", "unified"}:
            _fail("FS025_UNSUPPORTED", f"{path}.residency", repr(item["residency"]))
    if buffer_ordinals != list(range(len(buffer_ordinals))):
        _fail("FS031_ORDINALS", "$.buffers", "must be contiguous and ordered")

    callback = _object(root["callback"], "$.callback", {"roles"})
    role_rows = _array(callback["roles"], "$.callback.roles", nonempty=True)
    role_names: list[str] = []
    for index, raw in enumerate(role_rows):
        path = f"$.callback.roles[{index}]"
        item = _object(
            raw, path, {"role", "cardinality", "allowed_effects", "required_effects"}
        )
        role = _string(item["role"], f"{path}.role", identifier=True)
        if role not in _ROLE_EFFECTS:
            _fail("FS025_UNSUPPORTED", f"{path}.role", role)
        if item["cardinality"] not in {"zero", "zero_or_one", "exactly_one"}:
            _fail("FS025_UNSUPPORTED", f"{path}.cardinality", repr(item["cardinality"]))
        allowed = set(
            _unique_identifiers(
                item["allowed_effects"],
                f"{path}.allowed_effects",
                allowed=_ROLE_EFFECTS[role],
            )
        )
        required = set(
            _unique_identifiers(
                item["required_effects"],
                f"{path}.required_effects",
                allowed=_ROLE_EFFECTS[role],
            )
        )
        if not required <= allowed:
            _fail("FS033_ROLE_EFFECT", path, "required effects are not allowed")
        role_names.append(role)
    if len(role_names) != len(set(role_names)):
        _fail("FS024_DUPLICATE", "$.callback.roles", "duplicate roles")
    role_set = set(role_names)

    channel_ordinals: list[int] = []
    channel_producers: dict[str, tuple[str, str]] = {}
    for index, raw in enumerate(_array(root["channels"], "$.channels")):
        path = f"$.channels[{index}]"
        item = _object(
            raw,
            path,
            {
                "channel_id",
                "ordinal",
                "semantic",
                "value_type",
                "producer",
                "ownership",
                "consumers",
            },
        )
        channel_id = _string(
            item["channel_id"], f"{path}.channel_id", identifier=True
        )
        channel_ordinals.append(_integer(item["ordinal"], f"{path}.ordinal"))
        _string(item["semantic"], f"{path}.semantic", identifier=True)
        if item["value_type"] not in _VALUE_TYPES:
            _fail("FS025_UNSUPPORTED", f"{path}.value_type", repr(item["value_type"]))
        producer = _object(
            item["producer"], f"{path}.producer", {"kind"}, {"builtin", "role", "effect"}
        )
        if producer["kind"] == "provider_builtin":
            _object(producer, f"{path}.producer", {"kind", "builtin"})
            builtin = _string(
                producer["builtin"], f"{path}.producer.builtin", identifier=True
            )
            channel_producers[channel_id] = ("provider_builtin", builtin)
        elif producer["kind"] == "verified_effect":
            _object(producer, f"{path}.producer", {"kind", "role", "effect"})
            role = producer["role"]
            if role not in role_set or producer["effect"] not in _ROLE_EFFECTS[role]:
                _fail("FS033_ROLE_EFFECT", f"{path}.producer", "illegal role effect")
            channel_producers[channel_id] = ("verified_effect", role)
        else:
            _fail("FS025_UNSUPPORTED", f"{path}.producer.kind", repr(producer["kind"]))
        _string(item["ownership"], f"{path}.ownership", identifier=True)
        consumers: set[tuple[str, int]] = set()
        for consumer_index, raw_consumer in enumerate(
            _array(item["consumers"], f"{path}.consumers", nonempty=True)
        ):
            cpath = f"{path}.consumers[{consumer_index}]"
            consumer = _object(raw_consumer, cpath, {"role", "argument_index"})
            if consumer["role"] not in role_set:
                _fail("FS034_ROLE_REFERENCE", f"{cpath}.role", repr(consumer["role"]))
            key = (
                consumer["role"],
                _integer(consumer["argument_index"], f"{cpath}.argument_index", maximum=255),
            )
            if key in consumers:
                _fail("FS024_DUPLICATE", f"{path}.consumers", repr(key))
            consumers.add(key)
    if channel_ordinals != list(range(len(channel_ordinals))):
        _fail("FS031_ORDINALS", "$.channels", "must be contiguous and ordered")

    view_keys: set[tuple[str, int]] = set()
    buffer_lookup_views: dict[tuple[str, int], tuple[str, str]] = {}
    for index, raw in enumerate(_array(root["views"], "$.views")):
        path = f"$.views[{index}]"
        item = _object(raw, path, {"role", "argument_index", "source"})
        if item["role"] not in role_set:
            _fail("FS034_ROLE_REFERENCE", f"{path}.role", repr(item["role"]))
        view_key = (
            item["role"],
            _integer(item["argument_index"], f"{path}.argument_index", maximum=255),
        )
        if view_key in view_keys:
            _fail("FS024_DUPLICATE", "$.views", repr(view_key))
        view_keys.add(view_key)
        source = _object(
            item["source"],
            f"{path}.source",
            {"kind"},
            {"buffer_ref", "index_channel_ref", "channel_ref"},
        )
        if source["kind"] == "buffer_lookup":
            _object(source, f"{path}.source", {"kind", "buffer_ref", "index_channel_ref"})
            buffer_lookup_views[view_key] = (
                source["buffer_ref"], source["index_channel_ref"]
            )
        elif source["kind"] == "hit_channel":
            _object(source, f"{path}.source", {"kind", "channel_ref"})
        else:
            _fail("FS025_UNSUPPORTED", f"{path}.source.kind", repr(source["kind"]))

    event_ordinals: list[int] = []
    for index, raw in enumerate(_array(root["events"], "$.events", nonempty=True)):
        path = f"$.events[{index}]"
        item = _object(
            raw,
            path,
            {"event_id", "ordinal", "value_type", "source"},
            {"provider_builtin"},
        )
        _string(item["event_id"], f"{path}.event_id", identifier=True)
        event_ordinals.append(_integer(item["ordinal"], f"{path}.ordinal"))
        if item["value_type"] not in _VALUE_TYPES:
            _fail("FS025_UNSUPPORTED", f"{path}.value_type", repr(item["value_type"]))
        if item["source"] not in {"ir_output", "verified_effect", "provider_builtin"}:
            _fail("FS025_UNSUPPORTED", f"{path}.source", repr(item["source"]))
        if item["source"] == "provider_builtin":
            if "provider_builtin" not in item:
                _fail(
                    "FS046_CHANNEL_PRODUCER",
                    path,
                    "provider_builtin event source requires a named builtin",
                )
            _string(
                item["provider_builtin"],
                f"{path}.provider_builtin",
                identifier=True,
            )
        elif "provider_builtin" in item:
            _fail(
                "FS046_CHANNEL_PRODUCER",
                path,
                "named builtin is valid only for provider_builtin event source",
            )
    if event_ordinals != list(range(len(event_ordinals))):
        _fail("FS031_ORDINALS", "$.events", "must be contiguous and ordered")

    physical = _object(
        root["physical"],
        "$.physical",
        {"root", "metadata_bindings", "channel_bindings", "sbt"},
    )
    root_ref = _object(physical["root"], "$.physical.root", {"node_ref"})["node_ref"]
    metadata_bindings: dict[tuple[str, int], tuple[str, str]] = {}
    for index, raw in enumerate(
        _array(physical["metadata_bindings"], "$.physical.metadata_bindings")
    ):
        path = f"$.physical.metadata_bindings[{index}]"
        item = _object(
            raw, path, {"role", "argument_index", "buffer_ref", "index_channel_ref"}
        )
        if item["role"] not in role_set:
            _fail("FS034_ROLE_REFERENCE", f"{path}.role", repr(item["role"]))
        binding_key = (
            item["role"],
            _integer(item["argument_index"], f"{path}.argument_index", maximum=255),
        )
        if binding_key in metadata_bindings:
            _fail("FS024_DUPLICATE", "$.physical.metadata_bindings", repr(binding_key))
        metadata_bindings[binding_key] = (
            item["buffer_ref"], item["index_channel_ref"]
        )
    if metadata_bindings != buffer_lookup_views:
        _fail(
            "FS046_CHANNEL_PRODUCER",
            "$.physical.metadata_bindings",
            "physical metadata bindings must exactly match buffer_lookup views",
        )
    physical_channel_refs: set[str] = set()
    for index, raw in enumerate(
        _array(physical["channel_bindings"], "$.physical.channel_bindings")
    ):
        path = f"$.physical.channel_bindings[{index}]"
        item = _object(
            raw,
            path,
            {"channel_ref"},
            {"producer_role", "provider_builtin"},
        )
        channel_ref = _string(
            item["channel_ref"], f"{path}.channel_ref", identifier=True
        )
        if channel_ref in physical_channel_refs:
            _fail("FS024_DUPLICATE", "$.physical.channel_bindings", channel_ref)
        physical_channel_refs.add(channel_ref)
        has_role = "producer_role" in item
        has_builtin = "provider_builtin" in item
        if has_role == has_builtin:
            _fail(
                "FS046_CHANNEL_PRODUCER",
                path,
                "exactly one of producer_role or provider_builtin is required",
            )
        if has_role and item["producer_role"] not in role_set:
            _fail(
                "FS034_ROLE_REFERENCE",
                f"{path}.producer_role",
                repr(item["producer_role"]),
            )
        if has_builtin:
            _string(
                item["provider_builtin"],
                f"{path}.provider_builtin",
                identifier=True,
            )
        declared_producer = channel_producers.get(channel_ref)
        bound_producer = (
            ("verified_effect", item["producer_role"])
            if has_role else
            ("provider_builtin", item["provider_builtin"])
        )
        if declared_producer is not None and declared_producer != bound_producer:
            _fail(
                "FS046_CHANNEL_PRODUCER",
                path,
                "physical channel producer differs from channel declaration",
            )
    if physical_channel_refs != set(channel_producers):
        _fail(
            "FS046_CHANNEL_PRODUCER",
            "$.physical.channel_bindings",
            "every channel requires exactly one physical producer binding",
        )
    sbt = _object(
        physical["sbt"],
        "$.physical.sbt",
        {"record_stride", "record_count_relation", "ray_type_count"},
    )
    _integer(sbt["record_stride"], "$.physical.sbt.record_stride", minimum=1)
    _integer(sbt["ray_type_count"], "$.physical.sbt.ray_type_count", minimum=1)
    _string(
        sbt["record_count_relation"],
        "$.physical.sbt.record_count_relation",
        identifier=True,
    )

    pipeline = _array(root["result_pipeline"], "$.result_pipeline", nonempty=True)
    prior_steps: set[str] = set()
    operator_contracts: dict[str, str] = {}
    commit_flags: list[bool] = []
    for index, raw in enumerate(pipeline):
        path = f"$.result_pipeline[{index}]"
        if not isinstance(raw, dict) or "operator" not in raw:
            _fail("FS014_MISSING_KEYS", path, "operator")
        operator = raw["operator"]
        if operator == _PROVIDER_OPERATOR:
            item = _object(
                raw,
                path,
                {
                    "operator",
                    "step_id",
                    "operator_id",
                    "operator_contract_sha256",
                    "inputs",
                    "output_type",
                    "output_count_relation",
                    "algebra_properties",
                    "commits_output",
                },
            )
            step_id = _string(item["step_id"], f"{path}.step_id", identifier=True)
            operator_id = _string(
                item["operator_id"], f"{path}.operator_id", identifier=True
            )
            operator_contract = _digest(
                item["operator_contract_sha256"],
                f"{path}.operator_contract_sha256",
            )
            previous_contract = operator_contracts.setdefault(
                operator_id, operator_contract
            )
            if previous_contract != operator_contract:
                _fail(
                    "FS047_OPERATOR_IDENTITY",
                    f"{path}.operator_contract_sha256",
                    "one operator_id cannot name multiple contracts",
                )
            if item["output_type"] not in _VALUE_TYPES:
                _fail(
                    "FS025_UNSUPPORTED",
                    f"{path}.output_type",
                    repr(item["output_type"]),
                )
            _string(
                item["output_count_relation"],
                f"{path}.output_count_relation",
                identifier=True,
            )
            _unique_identifiers(
                item["algebra_properties"],
                f"{path}.algebra_properties",
            )
            inputs = _array(item["inputs"], f"{path}.inputs", nonempty=True)
            for input_index, raw_input in enumerate(inputs):
                input_path = f"{path}.inputs[{input_index}]"
                source = _object(
                    raw_input,
                    input_path,
                    {"kind"},
                    {"event_ref", "buffer_ref", "parameter_ref", "step_ref"},
                )
                reference_by_kind = {
                    "event": "event_ref",
                    "buffer": "buffer_ref",
                    "parameter": "parameter_ref",
                    "step": "step_ref",
                }
                reference = reference_by_kind.get(source["kind"])
                if reference is None:
                    _fail(
                        "FS025_UNSUPPORTED",
                        f"{input_path}.kind",
                        repr(source["kind"]),
                    )
                _object(source, input_path, {"kind", reference})
                _string(source[reference], f"{input_path}.{reference}", identifier=True)
                if reference == "step_ref" and source[reference] not in prior_steps:
                    _fail(
                        "FS045_PIPELINE_DATAFLOW",
                        f"{input_path}.step_ref",
                        "provider operator may reference only an earlier step",
                    )
            commits_output = _boolean(
                item["commits_output"], f"{path}.commits_output"
            )
            prior_steps.add(step_id)
            commit_flags.append(commits_output)
            continue
        if operator not in _RESULT_OPERATORS:
            _fail("FS025_UNSUPPORTED", f"{path}.operator", repr(operator))
        item = _object(raw, path, {"operator"} | set(_RESULT_OPERATORS[operator]))
        for key in ("event_ref", "parameter_ref", "predicate"):
            if key in item:
                _string(item[key], f"{path}.{key}", identifier=True)
        if "key_fields" in item:
            _unique_identifiers(item["key_fields"], f"{path}.key_fields", nonempty=True)
        commit_flags.append(operator in _COMMIT_OPERATORS)
    if not commit_flags[-1]:
        _fail("FS035_RESULT_COMMIT", "$.result_pipeline", "must end in a commit")
    if any(commit_flags[:-1]):
        _fail(
            "FS035_RESULT_COMMIT",
            "$.result_pipeline",
            "only the final result step may commit output",
        )

    continuation = _object(
        root["continuation"],
        "$.continuation",
        {"initial_state", "states", "transitions", "terminal_states", "invariants"},
    )
    state_kinds: dict[str, str] = {}
    for index, raw in enumerate(
        _array(continuation["states"], "$.continuation.states", nonempty=True)
    ):
        path = f"$.continuation.states[{index}]"
        item = _object(raw, path, {"state_id", "kind"})
        state_id = _string(item["state_id"], f"{path}.state_id", identifier=True)
        if item["kind"] not in _LIFECYCLE_STATE_KINDS:
            _fail("FS025_UNSUPPORTED", f"{path}.kind", repr(item["kind"]))
        state_kinds[state_id] = item["kind"]
    if set(state_kinds.values()) != _LIFECYCLE_STATE_KINDS:
        _fail("FS036_LIFECYCLE", "$.continuation.states", "all state kinds required")
    if state_kinds.get(continuation["initial_state"]) != "prepared":
        _fail("FS036_LIFECYCLE", "$.continuation.initial_state", "must be prepared")
    saw_copy = False
    saw_failure = False
    for index, raw in enumerate(
        _array(continuation["transitions"], "$.continuation.transitions", nonempty=True)
    ):
        path = f"$.continuation.transitions[{index}]"
        item = _object(raw, path, {"from_state", "event", "to_state"})
        if item["event"] not in _LIFECYCLE_EVENTS:
            _fail("FS025_UNSUPPORTED", f"{path}.event", repr(item["event"]))
        if item["event"] == "copy_output":
            saw_copy = True
            if state_kinds.get(item["from_state"]) != "status_ok" or state_kinds.get(
                item["to_state"]
            ) != "committed":
                _fail("FS036_LIFECYCLE", path, "copy_output must be status_ok -> committed")
        if item["event"] == "observe_status_failure":
            saw_failure = True
            if state_kinds.get(item["to_state"]) != "status_failed":
                _fail("FS036_LIFECYCLE", path, "failure must enter status_failed")
    terminal_kinds = {state_kinds.get(item) for item in continuation["terminal_states"]}
    if terminal_kinds != {"status_failed", "committed"}:
        _fail("FS036_LIFECYCLE", "$.continuation.terminal_states", "invalid terminals")
    invariants = set(
        _unique_identifiers(
            continuation["invariants"], "$.continuation.invariants", nonempty=True
        )
    )
    if invariants != {
        "copy_output_requires_status_ok",
        "status_failure_forbids_output_copy",
    }:
        _fail("FS036_LIFECYCLE", "$.continuation.invariants", "fail-closed invariants required")
    if not saw_copy or not saw_failure:
        _fail("FS036_LIFECYCLE", "$.continuation.transitions", "success and failure required")

    _unique_identifiers(root["capabilities"], "$.capabilities", nonempty=True)
    identity_bind_set = set(
        _unique_identifiers(root["identity_bind_set"], "$.identity_bind_set", nonempty=True)
    )
    if not {"callback_ir", "actual_executable"} <= identity_bind_set:
        _fail("FS037_IDENTITY_BINDING", "$.identity_bind_set", "required bindings absent")
    _validate_resource_limits(root["resource_limits"], "$.resource_limits")

    _validate_local_references(shape)
    if root_ref not in node_children:
        _fail("FS027_DANGLING_REFERENCE", "$.physical.root.node_ref", repr(root_ref))
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            _fail("FS038_GRAPH_CYCLE", "$.graph_nodes", node)
        if node in visited:
            return
        visiting.add(node)
        for child in node_children[node]:
            visit(child)
        visiting.remove(node)
        visited.add(node)

    visit(root_ref)
    if visited != set(node_children):
        _fail("FS039_UNREACHABLE_GRAPH", "$.graph_nodes", repr(sorted(set(node_children) - visited)))


def _alpha_normalize_shape(shape: dict[str, Any]) -> dict[str, Any]:
    _validate_family_shape(shape)
    normalized = copy.deepcopy(shape)
    maps: dict[str, dict[str, str]] = {
        prefix: {} for prefix in _BINDER_FIELDS.values()
    }
    for obj in _walk_dicts(normalized):
        for field, prefix in _BINDER_FIELDS.items():
            if field not in obj:
                continue
            original = obj[field]
            if original in maps[prefix]:
                _fail("FS026_DUPLICATE_BINDER", field, repr(original))
            maps[prefix][original] = f"{prefix}{len(maps[prefix])}"
            obj[field] = maps[prefix][original]
    for obj in _walk_dicts(normalized):
        for field, prefix in _REFERENCE_FIELDS.items():
            if field in obj:
                original = obj[field]
                if original not in maps[prefix]:
                    _fail("FS027_DANGLING_REFERENCE", field, repr(original))
                obj[field] = maps[prefix][original]
        for field in _SHAPE_SET_FIELDS:
            if field not in obj:
                continue
            items = obj[field]
            if field in _SET_REFERENCE_FIELDS:
                prefix = _SET_REFERENCE_FIELDS[field]
                items = [maps[prefix][item] for item in items]
            keyed = [(_canonical_bytes(item), item) for item in items]
            if len({key for key, _ in keyed}) != len(keyed):
                _fail("FS024_DUPLICATE", field, "duplicate set member")
            obj[field] = [item for _, item in sorted(keyed)]
    return normalized


def _validate_protocol_instance(instance: dict[str, Any]) -> None:
    _validate_normative_value(instance)
    root = _object(
        instance,
        "$",
        {
            "schema",
            "family_shape_sha256",
            "parameter_values",
            "nominal_semantics",
            "callback_source_sha256",
            "callback_ir_sha256",
            "effect_digest",
            "abi_sha256",
            "authorities",
        },
    )
    if root["schema"] != PROTOCOL_INSTANCE_SCHEMA:
        _fail("FS028_SCHEMA", "$.schema", PROTOCOL_INSTANCE_SCHEMA)
    for key in (
        "family_shape_sha256",
        "callback_source_sha256",
        "callback_ir_sha256",
        "effect_digest",
        "abi_sha256",
    ):
        _digest(root[key], f"$.{key}")
    refs: set[str] = set()
    for index, raw in enumerate(_array(root["parameter_values"], "$.parameter_values")):
        path = f"$.parameter_values[{index}]"
        item = _object(raw, path, {"parameter_ref", "value_type", "value"})
        ref = _string(item["parameter_ref"], f"{path}.parameter_ref", identifier=True)
        if ref in refs:
            _fail("FS024_DUPLICATE", "$.parameter_values", ref)
        refs.add(ref)
        _validate_parameter_value(item["value_type"], item["value"], path)
    semantics = root["nominal_semantics"]
    if not isinstance(semantics, dict) or not semantics:
        _fail("FS040_NOMINAL_SEMANTICS", "$.nominal_semantics", "non-empty object required")
    for key, value in semantics.items():
        _string(key, f"$.nominal_semantics.{key}", identifier=True)
        _string(value, f"$.nominal_semantics.{key}", identifier=True)
    authority_keys: set[tuple[str, str]] = set()
    for index, raw in enumerate(_array(root["authorities"], "$.authorities")):
        path = f"$.authorities[{index}]"
        item = _object(raw, path, {"authority_kind", "authority_sha256"})
        key = (
            _string(item["authority_kind"], f"{path}.authority_kind", identifier=True),
            _digest(item["authority_sha256"], f"{path}.authority_sha256"),
        )
        if key in authority_keys:
            _fail("FS024_DUPLICATE", "$.authorities", repr(key))
        authority_keys.add(key)


def _validate_parameter_value(value_type: object, value: object, path: str) -> None:
    if value_type not in _PARAMETER_TYPES:
        _fail("FS025_UNSUPPORTED", f"{path}.value_type", repr(value_type))
    if value_type == "bool":
        _boolean(value, f"{path}.value")
    elif value_type == "u32":
        _integer(value, f"{path}.value", maximum=(1 << 32) - 1)
    elif value_type == "u64":
        _integer(value, f"{path}.value", maximum=(1 << 64) - 1)
    elif value_type == "i32":
        _integer(value, f"{path}.value", minimum=-(1 << 31), maximum=(1 << 31) - 1)
    elif value_type == "i64":
        _integer(value, f"{path}.value", minimum=-(1 << 63), maximum=(1 << 63) - 1)
    elif value_type == "namespaced_identifier":
        _string(value, f"{path}.value", identifier=True)
    elif value_type == "f32_bits":
        if not isinstance(value, str) or _F32_BITS.fullmatch(value) is None:
            _fail("FS041_EXACT_BITS", f"{path}.value", "invalid f32 bit text")
    elif value_type == "f64_bits":
        if not isinstance(value, str) or _F64_BITS.fullmatch(value) is None:
            _fail("FS041_EXACT_BITS", f"{path}.value", "invalid f64 bit text")


def _normalize_protocol_instance(instance: dict[str, Any]) -> dict[str, Any]:
    normalized = copy.deepcopy(instance)
    normalized["authorities"] = sorted(
        normalized["authorities"], key=_canonical_bytes
    )
    return normalized


@dataclass(frozen=True, slots=True, init=False)
class FamilySchemaV1:
    """An exact, alpha-normalized, immutable family-shape declaration."""

    _canonical_document: bytes
    family_shape_sha256: str

    def __init__(self, document: object) -> None:
        raw = _parse_document(document)
        normalized = _alpha_normalize_shape(raw)
        canonical = _canonical_bytes(normalized)
        object.__setattr__(self, "_canonical_document", canonical)
        object.__setattr__(
            self,
            "family_shape_sha256",
            _domain_digest(FAMILY_SHAPE_SCHEMA, canonical),
        )

    @classmethod
    def from_document(cls, document: object) -> "FamilySchemaV1":
        return cls(document)

    @property
    def canonical_bytes(self) -> bytes:
        return self._canonical_document

    @property
    def document(self) -> Mapping[str, object]:
        return _readonly(json.loads(self._canonical_document))  # type: ignore[return-value]

    def to_dict(self) -> dict[str, Any]:
        return json.loads(self._canonical_document)


@dataclass(frozen=True, slots=True, init=False)
class ProtocolInstanceV1:
    """An immutable binding of a family shape to program semantics and proofs."""

    _canonical_document: bytes
    protocol_instance_sha256: str
    family_shape_sha256: str

    def __init__(self, document: object) -> None:
        raw = _parse_document(document)
        _validate_protocol_instance(raw)
        normalized = _normalize_protocol_instance(raw)
        canonical = _canonical_bytes(normalized)
        object.__setattr__(self, "_canonical_document", canonical)
        object.__setattr__(
            self,
            "protocol_instance_sha256",
            _domain_digest(PROTOCOL_INSTANCE_SCHEMA, canonical),
        )
        object.__setattr__(self, "family_shape_sha256", normalized["family_shape_sha256"])

    @classmethod
    def from_document(cls, document: object) -> "ProtocolInstanceV1":
        return cls(document)

    @property
    def canonical_bytes(self) -> bytes:
        return self._canonical_document

    @property
    def document(self) -> Mapping[str, object]:
        return _readonly(json.loads(self._canonical_document))  # type: ignore[return-value]

    def to_dict(self) -> dict[str, Any]:
        return json.loads(self._canonical_document)


def _validate_instance_against_schema(
    schema: FamilySchemaV1, instance: ProtocolInstanceV1
) -> None:
    if instance.family_shape_sha256 != schema.family_shape_sha256:
        _fail("FS042_SHAPE_BINDING", "instance.family_shape_sha256", "identity mismatch")
    shape = schema.to_dict()
    protocol = instance.to_dict()
    parameters = shape["parameters"]
    values = protocol["parameter_values"]
    expected_refs = [row["parameter_id"] for row in parameters]
    actual_refs = [row["parameter_ref"] for row in values]
    if actual_refs != expected_refs:
        _fail("FS043_PARAMETER_BINDING", "instance.parameter_values", "order or membership mismatch")
    for definition, binding in zip(parameters, values):
        if definition["type"] != binding["value_type"]:
            _fail("FS043_PARAMETER_BINDING", binding["parameter_ref"], "type mismatch")
        value = binding["value"]
        if type(value) is int:
            if "minimum" in definition and value < definition["minimum"]:
                _fail("FS043_PARAMETER_BINDING", binding["parameter_ref"], "below minimum")
            if "maximum" in definition and value > definition["maximum"]:
                _fail("FS043_PARAMETER_BINDING", binding["parameter_ref"], "above maximum")


def _derive_admission_document(
    schema: FamilySchemaV1,
    instance: ProtocolInstanceV1,
    behavior_schema_sha256: str,
    canonical_template_id: str,
    executable: bool,
) -> dict[str, Any]:
    # Reparse every immutable component.  This makes admission a reverification
    # boundary rather than trust in an earlier constructor call.
    schema = FamilySchemaV1(schema.canonical_bytes)
    instance = ProtocolInstanceV1(instance.canonical_bytes)
    _validate_instance_against_schema(schema, instance)
    behavior = _digest(behavior_schema_sha256, "behavior_schema_sha256")
    template = _string(
        canonical_template_id, "canonical_template_id", identifier=True
    )
    if type(executable) is not bool or executable:
        _fail(
            "FS044_EXECUTABLE_FORBIDDEN",
            "executable",
            "family plans are declarations and must be inert",
        )
    protocol = instance.to_dict()
    role_contracts = copy.deepcopy(schema.to_dict()["callback"]["roles"])
    return {
        "schema": FAMILY_ADMISSION_SCHEMA,
        "family_shape_sha256": schema.family_shape_sha256,
        "protocol_instance_sha256": instance.protocol_instance_sha256,
        "callback_source_sha256": protocol["callback_source_sha256"],
        "callback_ir_sha256": protocol["callback_ir_sha256"],
        "effect_digest": protocol["effect_digest"],
        "abi_sha256": protocol["abi_sha256"],
        "behavior_schema_sha256": behavior,
        "canonical_template_id": template,
        "role_contracts": role_contracts,
        "executable": False,
    }


@dataclass(frozen=True, slots=True, init=False)
class VerifiedFamilyAdmission:
    """A fully rederived, target-neutral shape/instance compatibility receipt."""

    family_schema: FamilySchemaV1
    protocol_instance: ProtocolInstanceV1
    behavior_schema_sha256: str
    canonical_template_id: str
    executable: bool
    _canonical_document: bytes
    admission_sha256: str

    def __init__(
        self,
        family_schema: FamilySchemaV1,
        protocol_instance: ProtocolInstanceV1,
        behavior_schema_sha256: str,
        canonical_template_id: str,
        executable: bool = False,
    ) -> None:
        if not isinstance(family_schema, FamilySchemaV1):
            _fail("FS048_API_TYPE", "family_schema", "FamilySchemaV1 required")
        if not isinstance(protocol_instance, ProtocolInstanceV1):
            _fail("FS048_API_TYPE", "protocol_instance", "ProtocolInstanceV1 required")
        document = _derive_admission_document(
            family_schema,
            protocol_instance,
            behavior_schema_sha256,
            canonical_template_id,
            executable,
        )
        canonical = _canonical_bytes(document)
        object.__setattr__(self, "family_schema", family_schema)
        object.__setattr__(self, "protocol_instance", protocol_instance)
        object.__setattr__(self, "behavior_schema_sha256", document["behavior_schema_sha256"])
        object.__setattr__(self, "canonical_template_id", document["canonical_template_id"])
        object.__setattr__(self, "executable", False)
        object.__setattr__(self, "_canonical_document", canonical)
        object.__setattr__(
            self,
            "admission_sha256",
            _domain_digest(FAMILY_ADMISSION_SCHEMA, canonical),
        )

    @property
    def canonical_bytes(self) -> bytes:
        return self._canonical_document

    @property
    def document(self) -> Mapping[str, object]:
        return _readonly(json.loads(self._canonical_document))  # type: ignore[return-value]

    def to_dict(self) -> dict[str, Any]:
        return json.loads(self._canonical_document)


def admit_family_schema(
    schema: FamilySchemaV1 | object,
    instance: ProtocolInstanceV1 | object,
    *,
    behavior_schema_sha256: str,
    canonical_template_id: str,
    executable: bool = False,
) -> VerifiedFamilyAdmission:
    """Strictly admit one target-neutral protocol instance and inert template."""

    family_schema = schema if isinstance(schema, FamilySchemaV1) else FamilySchemaV1(schema)
    protocol_instance = (
        instance if isinstance(instance, ProtocolInstanceV1) else ProtocolInstanceV1(instance)
    )
    return VerifiedFamilyAdmission(
        family_schema,
        protocol_instance,
        behavior_schema_sha256,
        canonical_template_id,
        executable,
    )


def reverify_family_admission(
    admission: VerifiedFamilyAdmission,
    *,
    schema: FamilySchemaV1 | object | None = None,
    instance: ProtocolInstanceV1 | object | None = None,
    behavior_schema_sha256: str | None = None,
    canonical_template_id: str | None = None,
    executable: bool | None = None,
) -> VerifiedFamilyAdmission:
    """Rebuild an admission and reject any identity or receipt drift."""

    if not isinstance(admission, VerifiedFamilyAdmission):
        _fail("FS048_API_TYPE", "admission", "VerifiedFamilyAdmission required")
    live_schema = FamilySchemaV1(
        admission.family_schema.canonical_bytes if schema is None else (
            schema.canonical_bytes if isinstance(schema, FamilySchemaV1) else schema
        )
    )
    live_instance = ProtocolInstanceV1(
        admission.protocol_instance.canonical_bytes if instance is None else (
            instance.canonical_bytes if isinstance(instance, ProtocolInstanceV1) else instance
        )
    )
    fresh = admit_family_schema(
        live_schema,
        live_instance,
        behavior_schema_sha256=(
            admission.behavior_schema_sha256
            if behavior_schema_sha256 is None
            else behavior_schema_sha256
        ),
        canonical_template_id=(
            admission.canonical_template_id
            if canonical_template_id is None
            else canonical_template_id
        ),
        executable=admission.executable if executable is None else executable,
    )
    if fresh.canonical_bytes != admission.canonical_bytes or fresh.admission_sha256 != admission.admission_sha256:
        _fail("FS049_ADMISSION_DRIFT", "admission", "canonical receipt changed")
    return fresh


def _derive_compilation_plan_document(
    admission: VerifiedFamilyAdmission,
) -> dict[str, Any]:
    verified = reverify_family_admission(admission)
    receipt = verified.to_dict()
    protocol = verified.protocol_instance.to_dict()
    return {
        "schema": FAMILY_COMPILATION_PLAN_SCHEMA,
        "family_admission_sha256": verified.admission_sha256,
        "family_shape_sha256": verified.family_schema.family_shape_sha256,
        "protocol_instance_sha256": verified.protocol_instance.protocol_instance_sha256,
        "callback_source_sha256": protocol["callback_source_sha256"],
        "callback_ir_sha256": protocol["callback_ir_sha256"],
        "effect_digest": protocol["effect_digest"],
        "abi_sha256": protocol["abi_sha256"],
        "behavior_schema_sha256": verified.behavior_schema_sha256,
        "canonical_template_id": verified.canonical_template_id,
        "role_contracts": receipt["role_contracts"],
        "family_shape": verified.family_schema.to_dict(),
        "protocol_instance": protocol,
        "executable": False,
    }


@dataclass(frozen=True, slots=True, init=False)
class CanonicalFamilyCompilationPlan:
    """A target-neutral canonical declaration; never an executable artifact."""

    admission: VerifiedFamilyAdmission
    _canonical_document: bytes
    plan_sha256: str

    def __init__(self, admission: VerifiedFamilyAdmission) -> None:
        if not isinstance(admission, VerifiedFamilyAdmission):
            _fail("FS048_API_TYPE", "admission", "VerifiedFamilyAdmission required")
        verified = reverify_family_admission(admission)
        document = _derive_compilation_plan_document(verified)
        canonical = _canonical_bytes(document)
        object.__setattr__(self, "admission", verified)
        object.__setattr__(self, "_canonical_document", canonical)
        object.__setattr__(
            self,
            "plan_sha256",
            _domain_digest(FAMILY_COMPILATION_PLAN_SCHEMA, canonical),
        )

    @property
    def canonical_bytes(self) -> bytes:
        return self._canonical_document

    @property
    def document(self) -> Mapping[str, object]:
        return _readonly(json.loads(self._canonical_document))  # type: ignore[return-value]

    def to_dict(self) -> dict[str, Any]:
        return json.loads(self._canonical_document)


def lower_canonical_compilation_plan(
    admission: VerifiedFamilyAdmission,
) -> CanonicalFamilyCompilationPlan:
    """Lower an admitted family without concrete-family dispatch."""

    return CanonicalFamilyCompilationPlan(admission)


def reverify_canonical_compilation_plan(
    plan: CanonicalFamilyCompilationPlan,
    *,
    schema: FamilySchemaV1 | object | None = None,
    instance: ProtocolInstanceV1 | object | None = None,
    behavior_schema_sha256: str | None = None,
    canonical_template_id: str | None = None,
    executable: bool | None = None,
) -> CanonicalFamilyCompilationPlan:
    """Rebuild a plan from live declarations and reject any canonical drift."""

    if not isinstance(plan, CanonicalFamilyCompilationPlan):
        _fail("FS048_API_TYPE", "plan", "CanonicalFamilyCompilationPlan required")
    admission = reverify_family_admission(
        plan.admission,
        schema=schema,
        instance=instance,
        behavior_schema_sha256=behavior_schema_sha256,
        canonical_template_id=canonical_template_id,
        executable=executable,
    )
    fresh = lower_canonical_compilation_plan(admission)
    if fresh.canonical_bytes != plan.canonical_bytes or fresh.plan_sha256 != plan.plan_sha256:
        _fail("FS050_PLAN_DRIFT", "plan", "canonical plan changed")
    return fresh


__all__ = [
    "CanonicalFamilyCompilationPlan",
    "FamilySchemaError",
    "FamilySchemaV1",
    "ProtocolInstanceV1",
    "VerifiedFamilyAdmission",
    "admit_family_schema",
    "lower_canonical_compilation_plan",
    "reverify_canonical_compilation_plan",
    "reverify_family_admission",
]
