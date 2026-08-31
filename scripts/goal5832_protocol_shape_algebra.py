"""Goal5832 protocol-shape algebra and repository-scope validator.

This is a research-specification reference implementation, not an RTDL GPU
compiler or a product extension point.  It freezes three identity domains:
family shape, protocol instance, and deployment.  It also checks that the
machine-readable Goal5832 authority agrees with the current public source and
the pinned OptiX 9 header.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable


class AlgebraError(ValueError):
    """Fail-closed Goal5832 specification diagnostic."""


_DOMAINS = {
    "family_shape": b"rtdl.family_shape.v1\0",
    "protocol_instance": b"rtdl.protocol_instance.v1\0",
    "deployment": b"rtdl.protocol_deployment.v1\0",
}
_SCHEMAS = {
    "family_shape": "rtdl.family_shape.v1",
    "protocol_instance": "rtdl.protocol_instance.v1",
    "deployment": "rtdl.protocol_deployment.v1",
}
_BINDER_FIELDS = {
    "parameter_id": "p",
    "node_id": "n",
    "buffer_id": "b",
    "channel_id": "h",
    "event_id": "e",
    "state_id": "s",
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
}
_SET_FIELDS = {
    "capabilities",
    "allowed_effects",
    "required_effects",
    "terminal_states",
    "identity_bind_set",
    "authorities",
    "invariants",
}
_SET_REFERENCE_FIELDS = {"terminal_states": "s"}
_FORBIDDEN_NORMATIVE_KEYS = {
    "application_name",
    "dataset_name",
    "display_name",
    "file_path",
    "timestamp",
}
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9_.:-]{0,127}\Z")

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
    "bool", "u32", "u64", "i32", "i64", "f32_bits", "f64_bits",
    "u32x2", "u32x3", "ray3f_bits", "aabb3f_bits", "namespaced_identifier",
}
_PARAMETER_TYPES = {
    "bool", "u32", "u64", "i32", "i64", "f32_bits", "f64_bits",
    "namespaced_identifier",
}
_PRIMITIVE_KINDS = {
    "builtin_triangle", "custom_primitive", "builtin_curve", "builtin_sphere",
    "none",
}
_RESULT_OPERATORS: dict[str, tuple[frozenset[str], frozenset[str]]] = {
    "emit_record": (frozenset({"event_ref"}), frozenset()),
    "filter": (frozenset({"event_ref", "predicate"}), frozenset()),
    "keyed_identical_deduplicate": (
        frozenset({"key_fields"}), frozenset()),
    "lexicographic_sort": (frozenset({"key_fields"}), frozenset()),
    "capacity_guard": (frozenset({"parameter_ref"}), frozenset()),
    "checked_i64_sum": (frozenset({"event_ref"}), frozenset()),
    "checked_u64_sum": (frozenset({"event_ref"}), frozenset()),
    "checked_u64_product_sum": (frozenset({"event_ref"}), frozenset()),
    "commit_ir_output": (frozenset(), frozenset()),
    "commit_collected_rows": (frozenset(), frozenset()),
    "commit_checked_reduction": (frozenset(), frozenset()),
}


def _object(
    value: Any,
    path: str,
    required: set[str] | frozenset[str],
    optional: set[str] | frozenset[str] = frozenset(),
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AlgebraError(f"{path} must be an object")
    missing = set(required) - set(value)
    extra = set(value) - set(required) - set(optional)
    if missing:
        raise AlgebraError(f"{path} missing keys: {sorted(missing)}")
    if extra:
        raise AlgebraError(f"{path} unknown keys: {sorted(extra)}")
    return value


def _array(value: Any, path: str, *, nonempty: bool = False) -> list[Any]:
    if not isinstance(value, list):
        raise AlgebraError(f"{path} must be a list")
    if nonempty and not value:
        raise AlgebraError(f"{path} must not be empty")
    return value


def _string(value: Any, path: str, *, identifier: bool = False) -> str:
    if not isinstance(value, str) or not value:
        raise AlgebraError(f"{path} must be a non-empty string")
    if not value.isascii():
        raise AlgebraError(f"{path} must be ASCII")
    if identifier and _IDENTIFIER.fullmatch(value) is None:
        raise AlgebraError(f"{path} is not a bounded identifier")
    return value


def _integer(
    value: Any,
    path: str,
    *,
    minimum: int = 0,
    maximum: int = (1 << 63) - 1,
) -> int:
    if type(value) is not int:  # bool is deliberately rejected.
        raise AlgebraError(f"{path} must be an integer, not bool or float")
    if not minimum <= value <= maximum:
        raise AlgebraError(f"{path} integer out of range")
    return value


def _boolean(value: Any, path: str) -> bool:
    if type(value) is not bool:
        raise AlgebraError(f"{path} must be a boolean")
    return value


def _hex_digest(value: Any, path: str) -> str:
    text = _string(value, path)
    if _HEX64.fullmatch(text) is None:
        raise AlgebraError(f"{path} must be a lowercase SHA-256 digest")
    return text


def _unique_strings(
    value: Any,
    path: str,
    *,
    nonempty: bool = False,
    allowed: set[str] | None = None,
) -> list[str]:
    items = _array(value, path, nonempty=nonempty)
    result = [_string(item, f"{path}[{index}]", identifier=True)
              for index, item in enumerate(items)]
    if len(result) != len(set(result)):
        raise AlgebraError(f"{path} contains duplicates")
    if allowed is not None and not set(result) <= allowed:
        raise AlgebraError(f"{path} contains unsupported values")
    return result


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AlgebraError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json_exact(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=lambda token: (_ for _ in ()).throw(
                AlgebraError(f"non-finite JSON value: {token}")),
        )
    except UnicodeDecodeError as exc:
        raise AlgebraError("authority is not UTF-8") from exc
    if not isinstance(value, dict):
        raise AlgebraError("authority root must be an object")
    return value


def _validate_normative_value(value: Any, path: str = "$", depth: int = 0) -> None:
    if depth > 64:
        raise AlgebraError(f"normative object too deep at {path}")
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        raise AlgebraError(
            f"floating JSON number forbidden at {path}; use exact bit text")
    if isinstance(value, list):
        if len(value) > 4096:
            raise AlgebraError(f"normative array too large at {path}")
        for index, item in enumerate(value):
            _validate_normative_value(item, f"{path}[{index}]", depth + 1)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or not key.isascii():
                raise AlgebraError(f"non-ASCII normative key at {path}")
            if key in _FORBIDDEN_NORMATIVE_KEYS:
                raise AlgebraError(f"non-normative key {key} at {path}")
            _validate_normative_value(item, f"{path}.{key}", depth + 1)
        return
    raise AlgebraError(f"unsupported normative value at {path}: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    _validate_normative_value(value)
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False,
    ).encode("ascii")


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
                raise AlgebraError(f"duplicate local binder {field}={name}")
            declared[prefix].add(name)
    for obj in _walk_dicts(value):
        for field, prefix in _REFERENCE_FIELDS.items():
            if field in obj and obj[field] not in declared[prefix]:
                raise AlgebraError(
                    f"dangling local reference {field}={obj[field]!r}")
        for field, prefix in _SET_REFERENCE_FIELDS.items():
            if field not in obj:
                continue
            for item in _array(obj[field], field):
                if item not in declared[prefix]:
                    raise AlgebraError(
                        f"dangling local reference in {field}: {item!r}")


def validate_family_shape(shape: dict[str, Any]) -> None:
    """Validate the exact typed v1 protocol-shape document."""
    _validate_normative_value(shape)
    root_keys = {
        "schema", "parameters", "graph_nodes", "buffers", "channels",
        "views", "events", "callback", "physical", "result_pipeline",
        "continuation", "capabilities", "identity_bind_set",
        "resource_limits",
    }
    root = _object(shape, "$", root_keys)
    if root["schema"] != _SCHEMAS["family_shape"]:
        raise AlgebraError("family shape schema mismatch")

    for index, raw in enumerate(_array(root["parameters"], "$.parameters")):
        path = f"$.parameters[{index}]"
        item = _object(raw, path, {"parameter_id", "type"}, {"minimum", "maximum"})
        _string(item["parameter_id"], f"{path}.parameter_id", identifier=True)
        value_type = _string(item["type"], f"{path}.type", identifier=True)
        if value_type not in _VALUE_TYPES:
            raise AlgebraError(f"{path}.type unsupported")
        if "minimum" in item:
            _integer(item["minimum"], f"{path}.minimum", minimum=-(1 << 63))
        if "maximum" in item:
            _integer(item["maximum"], f"{path}.maximum", minimum=-(1 << 63))
        if "minimum" in item and "maximum" in item \
                and item["minimum"] > item["maximum"]:
            raise AlgebraError(f"{path} has inverted bounds")

    nodes = _array(root["graph_nodes"], "$.graph_nodes", nonempty=True)
    node_children: dict[str, list[str]] = {}
    node_ordinals: list[int] = []
    for index, raw in enumerate(nodes):
        path = f"$.graph_nodes[{index}]"
        item = _object(raw, path, {
            "node_id", "kind", "primitive_kind", "ordinal", "update_policy",
            "sbt_record_stride", "children",
        })
        node_id = _string(item["node_id"], f"{path}.node_id", identifier=True)
        kind = _string(item["kind"], f"{path}.kind", identifier=True)
        primitive = _string(
            item["primitive_kind"], f"{path}.primitive_kind", identifier=True)
        if kind not in {"gas", "ias"} or primitive not in _PRIMITIVE_KINDS:
            raise AlgebraError(f"{path} has unsupported graph kind")
        if item["update_policy"] not in {"static", "refit", "rebuild"}:
            raise AlgebraError(f"{path}.update_policy unsupported")
        node_ordinals.append(_integer(item["ordinal"], f"{path}.ordinal"))
        _integer(item["sbt_record_stride"], f"{path}.sbt_record_stride", minimum=1)
        children: list[str] = []
        for child_index, child_raw in enumerate(_array(item["children"], f"{path}.children")):
            child = _object(
                child_raw, f"{path}.children[{child_index}]", {"node_ref"})
            children.append(_string(
                child["node_ref"], f"{path}.children[{child_index}].node_ref",
                identifier=True))
        if kind == "gas" and (primitive == "none" or children):
            raise AlgebraError(f"{path} GAS must be a leaf with a primitive")
        if kind == "ias" and (primitive != "none" or not children):
            raise AlgebraError(f"{path} IAS must have children and no primitive")
        node_children[node_id] = children
    if node_ordinals != list(range(len(node_ordinals))):
        raise AlgebraError("$.graph_nodes ordinals must be contiguous and ordered")

    buffer_ordinals: list[int] = []
    for index, raw in enumerate(_array(root["buffers"], "$.buffers")):
        path = f"$.buffers[{index}]"
        item = _object(raw, path, {
            "buffer_id", "ordinal", "semantic", "domain", "value_type",
            "access", "count_relation", "alignment_bytes", "contiguous",
            "residency",
        })
        _string(item["buffer_id"], f"{path}.buffer_id", identifier=True)
        buffer_ordinals.append(_integer(item["ordinal"], f"{path}.ordinal"))
        _string(item["semantic"], f"{path}.semantic", identifier=True)
        if item["domain"] not in {"primitive", "query", "launch", "result"}:
            raise AlgebraError(f"{path}.domain unsupported")
        if item["value_type"] not in _VALUE_TYPES:
            raise AlgebraError(f"{path}.value_type unsupported")
        if item["access"] not in {"read_only", "write_only", "read_write"}:
            raise AlgebraError(f"{path}.access unsupported")
        _string(item["count_relation"], f"{path}.count_relation", identifier=True)
        alignment = _integer(
            item["alignment_bytes"], f"{path}.alignment_bytes", minimum=1,
            maximum=4096)
        if alignment & (alignment - 1):
            raise AlgebraError(f"{path}.alignment_bytes must be a power of two")
        _boolean(item["contiguous"], f"{path}.contiguous")
        if item["residency"] not in {"device", "host", "unified"}:
            raise AlgebraError(f"{path}.residency unsupported")
    if buffer_ordinals != list(range(len(buffer_ordinals))):
        raise AlgebraError("$.buffers ordinals must be contiguous and ordered")

    callback = _object(root["callback"], "$.callback", {"roles"})
    role_rows = _array(callback["roles"], "$.callback.roles", nonempty=True)
    role_names: list[str] = []
    for index, raw in enumerate(role_rows):
        path = f"$.callback.roles[{index}]"
        item = _object(raw, path, {
            "role", "cardinality", "allowed_effects", "required_effects",
        })
        role = _string(item["role"], f"{path}.role", identifier=True)
        if role not in _ROLE_EFFECTS:
            raise AlgebraError(f"{path}.role unsupported")
        if item["cardinality"] not in {"zero", "zero_or_one", "exactly_one"}:
            raise AlgebraError(f"{path}.cardinality unsupported")
        allowed = set(_unique_strings(
            item["allowed_effects"], f"{path}.allowed_effects",
            allowed=_ROLE_EFFECTS[role]))
        required = set(_unique_strings(
            item["required_effects"], f"{path}.required_effects",
            allowed=_ROLE_EFFECTS[role]))
        if not required <= allowed:
            raise AlgebraError(f"{path}.required_effects not allowed")
        role_names.append(role)
    if len(role_names) != len(set(role_names)):
        raise AlgebraError("$.callback.roles contains duplicate roles")
    role_set = set(role_names)

    channel_ordinals: list[int] = []
    for index, raw in enumerate(_array(root["channels"], "$.channels")):
        path = f"$.channels[{index}]"
        item = _object(raw, path, {
            "channel_id", "ordinal", "semantic", "value_type", "producer",
            "ownership", "consumers",
        })
        _string(item["channel_id"], f"{path}.channel_id", identifier=True)
        channel_ordinals.append(_integer(item["ordinal"], f"{path}.ordinal"))
        _string(item["semantic"], f"{path}.semantic", identifier=True)
        if item["value_type"] not in _VALUE_TYPES:
            raise AlgebraError(f"{path}.value_type unsupported")
        producer = _object(
            item["producer"], f"{path}.producer", {"kind"},
            {"builtin", "role", "effect"})
        producer_kind = producer["kind"]
        if producer_kind == "provider_builtin":
            _object(producer, f"{path}.producer", {"kind", "builtin"})
            _string(producer["builtin"], f"{path}.producer.builtin", identifier=True)
        elif producer_kind == "verified_effect":
            _object(producer, f"{path}.producer", {"kind", "role", "effect"})
            producer_role = producer["role"]
            if producer_role not in role_set or producer["effect"] not in _ROLE_EFFECTS[producer_role]:
                raise AlgebraError(f"{path}.producer is not a legal role effect")
        else:
            raise AlgebraError(f"{path}.producer.kind unsupported")
        _string(item["ownership"], f"{path}.ownership", identifier=True)
        seen_consumers: set[tuple[str, int]] = set()
        for consumer_index, consumer_raw in enumerate(_array(
                item["consumers"], f"{path}.consumers", nonempty=True)):
            consumer_path = f"{path}.consumers[{consumer_index}]"
            consumer = _object(
                consumer_raw, consumer_path, {"role", "argument_index"})
            if consumer["role"] not in role_set:
                raise AlgebraError(f"{consumer_path}.role not admitted")
            argument_index = _integer(
                consumer["argument_index"], f"{consumer_path}.argument_index",
                maximum=255)
            key = (consumer["role"], argument_index)
            if key in seen_consumers:
                raise AlgebraError(f"{path}.consumers contains duplicates")
            seen_consumers.add(key)
    if channel_ordinals != list(range(len(channel_ordinals))):
        raise AlgebraError("$.channels ordinals must be contiguous and ordered")

    for index, raw in enumerate(_array(root["views"], "$.views")):
        path = f"$.views[{index}]"
        item = _object(raw, path, {"role", "argument_index", "source"})
        if item["role"] not in role_set:
            raise AlgebraError(f"{path}.role not admitted")
        _integer(item["argument_index"], f"{path}.argument_index", maximum=255)
        source = _object(
            item["source"], f"{path}.source", {"kind"},
            {"buffer_ref", "index_channel_ref", "channel_ref"})
        if source["kind"] == "buffer_lookup":
            _object(source, f"{path}.source", {
                "kind", "buffer_ref", "index_channel_ref"})
        elif source["kind"] == "hit_channel":
            _object(source, f"{path}.source", {"kind", "channel_ref"})
        else:
            raise AlgebraError(f"{path}.source.kind unsupported")

    event_ordinals: list[int] = []
    for index, raw in enumerate(_array(root["events"], "$.events", nonempty=True)):
        path = f"$.events[{index}]"
        item = _object(raw, path, {"event_id", "ordinal", "value_type", "source"})
        _string(item["event_id"], f"{path}.event_id", identifier=True)
        event_ordinals.append(_integer(item["ordinal"], f"{path}.ordinal"))
        if item["value_type"] not in _VALUE_TYPES:
            raise AlgebraError(f"{path}.value_type unsupported")
        if item["source"] not in {"ir_output", "verified_effect", "provider_builtin"}:
            raise AlgebraError(f"{path}.source unsupported")
    if event_ordinals != list(range(len(event_ordinals))):
        raise AlgebraError("$.events ordinals must be contiguous and ordered")

    physical = _object(root["physical"], "$.physical", {
        "root", "metadata_bindings", "channel_bindings", "sbt",
    })
    root_ref = _object(physical["root"], "$.physical.root", {"node_ref"})["node_ref"]
    for index, raw in enumerate(_array(
            physical["metadata_bindings"], "$.physical.metadata_bindings")):
        path = f"$.physical.metadata_bindings[{index}]"
        item = _object(raw, path, {
            "role", "argument_index", "buffer_ref", "index_channel_ref"})
        if item["role"] not in role_set:
            raise AlgebraError(f"{path}.role not admitted")
        _integer(item["argument_index"], f"{path}.argument_index", maximum=255)
    for index, raw in enumerate(_array(
            physical["channel_bindings"], "$.physical.channel_bindings")):
        path = f"$.physical.channel_bindings[{index}]"
        item = _object(raw, path, {"channel_ref", "producer_role"})
        if item["producer_role"] not in role_set:
            raise AlgebraError(f"{path}.producer_role not admitted")
    sbt = _object(physical["sbt"], "$.physical.sbt", {
        "record_stride", "record_count_relation", "ray_type_count"})
    _integer(sbt["record_stride"], "$.physical.sbt.record_stride", minimum=1)
    _integer(sbt["ray_type_count"], "$.physical.sbt.ray_type_count", minimum=1)
    _string(sbt["record_count_relation"], "$.physical.sbt.record_count_relation",
            identifier=True)

    pipeline = _array(root["result_pipeline"], "$.result_pipeline", nonempty=True)
    for index, raw in enumerate(pipeline):
        path = f"$.result_pipeline[{index}]"
        if not isinstance(raw, dict) or "operator" not in raw:
            raise AlgebraError(f"{path} missing operator")
        operator = raw["operator"]
        if operator not in _RESULT_OPERATORS:
            raise AlgebraError(f"{path}.operator unsupported")
        required, optional = _RESULT_OPERATORS[operator]
        item = _object(raw, path, {"operator"} | set(required), set(optional))
        for key in ("event_ref", "parameter_ref"):
            if key in item:
                _string(item[key], f"{path}.{key}", identifier=True)
        for key in ("predicate",):
            if key in item:
                _string(item[key], f"{path}.{key}", identifier=True)
        if "key_fields" in item:
            _unique_strings(item["key_fields"], f"{path}.key_fields", nonempty=True)
    if pipeline[-1]["operator"] not in {
            "commit_ir_output", "commit_collected_rows", "commit_checked_reduction"}:
        raise AlgebraError("$.result_pipeline must end in an output commit")

    continuation = _object(root["continuation"], "$.continuation", {
        "initial_state", "states", "transitions", "terminal_states", "invariants",
    })
    states = _array(continuation["states"], "$.continuation.states", nonempty=True)
    state_kinds: dict[str, str] = {}
    for index, raw in enumerate(states):
        path = f"$.continuation.states[{index}]"
        item = _object(raw, path, {"state_id", "kind"})
        state_id = _string(item["state_id"], f"{path}.state_id", identifier=True)
        if item["kind"] not in {
                "prepared", "launched", "status_ok", "status_failed", "committed"}:
            raise AlgebraError(f"{path}.kind unsupported")
        state_kinds[state_id] = item["kind"]
    if set(state_kinds.values()) != {
            "prepared", "launched", "status_ok", "status_failed", "committed"}:
        raise AlgebraError("$.continuation must declare all five lifecycle state kinds")
    if state_kinds.get(continuation["initial_state"]) != "prepared":
        raise AlgebraError("$.continuation.initial_state must be prepared")
    transitions = _array(
        continuation["transitions"], "$.continuation.transitions", nonempty=True)
    saw_copy = saw_failure = False
    for index, raw in enumerate(transitions):
        path = f"$.continuation.transitions[{index}]"
        item = _object(raw, path, {"from_state", "event", "to_state"})
        if item["event"] not in {
                "launch", "observe_status_ok", "observe_status_failure", "copy_output"}:
            raise AlgebraError(f"{path}.event unsupported")
        if item["event"] == "copy_output":
            saw_copy = True
            if state_kinds.get(item["from_state"]) != "status_ok" \
                    or state_kinds.get(item["to_state"]) != "committed":
                raise AlgebraError("copy_output must be status_ok -> committed")
        if item["event"] == "observe_status_failure":
            saw_failure = True
            if state_kinds.get(item["to_state"]) != "status_failed":
                raise AlgebraError("status failure must enter status_failed")
    terminal_kinds = {state_kinds.get(item) for item in continuation["terminal_states"]}
    if terminal_kinds != {"status_failed", "committed"}:
        raise AlgebraError("terminal states must be status_failed and committed")
    invariants = set(_unique_strings(
        continuation["invariants"], "$.continuation.invariants", nonempty=True))
    if invariants != {
            "copy_output_requires_status_ok", "status_failure_forbids_output_copy"}:
        raise AlgebraError("continuation invariants drift")
    if not saw_copy or not saw_failure:
        raise AlgebraError("continuation lacks success or fail-closed transition")

    _unique_strings(root["capabilities"], "$.capabilities", nonempty=True)
    bind_set = set(_unique_strings(
        root["identity_bind_set"], "$.identity_bind_set", nonempty=True))
    if not {"callback_ir", "actual_executable"} <= bind_set:
        raise AlgebraError("identity bind set omits callback_ir or actual_executable")
    limits = _object(root["resource_limits"], "$.resource_limits", {
        "max_payload_u32_slots", "max_attribute_u32_slots", "max_trace_depth",
        "max_callable_depth", "max_static_loop_trip_count",
        "max_total_static_iterations", "max_helper_call_depth",
    })
    _integer(limits["max_payload_u32_slots"], "$.resource_limits.max_payload_u32_slots",
             maximum=32)
    _integer(limits["max_attribute_u32_slots"],
             "$.resource_limits.max_attribute_u32_slots", maximum=8)
    _integer(limits["max_trace_depth"], "$.resource_limits.max_trace_depth",
             minimum=1, maximum=31)
    _integer(limits["max_callable_depth"], "$.resource_limits.max_callable_depth",
             maximum=31)
    _integer(limits["max_static_loop_trip_count"],
             "$.resource_limits.max_static_loop_trip_count", minimum=1,
             maximum=1 << 20)
    _integer(limits["max_total_static_iterations"],
             "$.resource_limits.max_total_static_iterations", minimum=1,
             maximum=1 << 24)
    _integer(limits["max_helper_call_depth"],
             "$.resource_limits.max_helper_call_depth", maximum=1024)

    _validate_local_references(shape)
    if root_ref not in node_children:
        raise AlgebraError("$.physical.root is not a graph node")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise AlgebraError("$.graph_nodes contains a cycle")
        if node in visited:
            return
        visiting.add(node)
        for child in node_children[node]:
            visit(child)
        visiting.remove(node)
        visited.add(node)

    visit(root_ref)
    if visited != set(node_children):
        raise AlgebraError("$.graph_nodes contains unreachable nodes")


def validate_protocol_instance(instance: dict[str, Any]) -> None:
    _validate_normative_value(instance)
    root = _object(instance, "$", {
        "schema", "family_shape_sha256", "parameter_values", "nominal_semantics",
        "callback_source_sha256", "callback_ir_sha256", "effect_digest",
        "abi_sha256", "authorities",
    })
    if root["schema"] != _SCHEMAS["protocol_instance"]:
        raise AlgebraError("protocol instance schema mismatch")
    for key in (
            "family_shape_sha256", "callback_source_sha256", "callback_ir_sha256",
            "effect_digest", "abi_sha256"):
        _hex_digest(root[key], f"$.{key}")
    seen_parameter_refs: set[str] = set()
    for index, raw in enumerate(_array(
            root["parameter_values"], "$.parameter_values")):
        path = f"$.parameter_values[{index}]"
        item = _object(raw, path, {"parameter_ref", "value_type", "value"})
        parameter_ref = _string(
            item["parameter_ref"], f"{path}.parameter_ref", identifier=True)
        if parameter_ref in seen_parameter_refs:
            raise AlgebraError("$.parameter_values contains duplicate parameter_ref")
        seen_parameter_refs.add(parameter_ref)
        value_type = item["value_type"]
        if value_type not in _PARAMETER_TYPES:
            raise AlgebraError(f"{path}.value_type unsupported")
        value = item["value"]
        if value_type == "bool":
            _boolean(value, f"{path}.value")
        elif value_type == "u32":
            _integer(value, f"{path}.value", maximum=(1 << 32) - 1)
        elif value_type == "u64":
            _integer(value, f"{path}.value", maximum=(1 << 64) - 1)
        elif value_type == "i32":
            _integer(value, f"{path}.value", minimum=-(1 << 31),
                     maximum=(1 << 31) - 1)
        elif value_type == "i64":
            _integer(value, f"{path}.value", minimum=-(1 << 63),
                     maximum=(1 << 63) - 1)
        elif value_type == "namespaced_identifier":
            _string(value, f"{path}.value", identifier=True)
        elif value_type == "f32_bits":
            if not isinstance(value, str) or re.fullmatch(r"f32:[0-9a-f]{8}", value) is None:
                raise AlgebraError(f"{path}.value must be exact f32 bits")
        elif value_type == "f64_bits":
            if not isinstance(value, str) or re.fullmatch(r"f64:[0-9a-f]{16}", value) is None:
                raise AlgebraError(f"{path}.value must be exact f64 bits")
    semantics = _object(root["nominal_semantics"], "$.nominal_semantics", set(),
                        set(root["nominal_semantics"]) if isinstance(root["nominal_semantics"], dict) else set())
    if not semantics:
        raise AlgebraError("$.nominal_semantics must not be empty")
    for key, value in semantics.items():
        _string(key, f"$.nominal_semantics.{key}", identifier=True)
        _string(value, f"$.nominal_semantics.{key}", identifier=True)
    authorities = _array(root["authorities"], "$.authorities")
    seen: set[tuple[str, str]] = set()
    for index, raw in enumerate(authorities):
        path = f"$.authorities[{index}]"
        item = _object(raw, path, {"authority_kind", "authority_sha256"})
        key = (
            _string(item["authority_kind"], f"{path}.authority_kind", identifier=True),
            _hex_digest(item["authority_sha256"], f"{path}.authority_sha256"),
        )
        if key in seen:
            raise AlgebraError("$.authorities contains duplicates")
        seen.add(key)


def validate_instance_against_shape(
    instance: dict[str, Any], shape: dict[str, Any],
) -> None:
    validate_family_shape(shape)
    validate_protocol_instance(instance)
    if instance["family_shape_sha256"] != identity("family_shape", shape):
        raise AlgebraError("instance family-shape identity mismatch")
    normalized = alpha_normalize_shape(shape)
    expected = {
        item["parameter_id"]: item["type"] for item in normalized["parameters"]
    }
    actual = {
        item["parameter_ref"]: item["value_type"]
        for item in instance["parameter_values"]
    }
    if actual != expected:
        raise AlgebraError("instance typed parameter binding mismatch")


def validate_deployment(deployment: dict[str, Any]) -> None:
    _validate_normative_value(deployment)
    root = _object(deployment, "$", {
        "schema", "protocol_instance_sha256", "target_profile_sha256",
        "physical_schema_sha256", "provider", "actual_executable_sha256",
    })
    if root["schema"] != _SCHEMAS["deployment"]:
        raise AlgebraError("deployment schema mismatch")
    for key in (
            "protocol_instance_sha256", "target_profile_sha256",
            "physical_schema_sha256", "actual_executable_sha256"):
        _hex_digest(root[key], f"$.{key}")
    provider = _object(root["provider"], "$.provider", {
        "provider_id", "provider_version", "provider_binary_sha256",
        "generated_device_source_sha256", "generated_host_source_sha256",
    })
    _string(provider["provider_id"], "$.provider.provider_id", identifier=True)
    _string(provider["provider_version"], "$.provider.provider_version")
    for key in (
            "provider_binary_sha256", "generated_device_source_sha256",
            "generated_host_source_sha256"):
        _hex_digest(provider[key], f"$.provider.{key}")


def _normalize_protocol_instance(instance: dict[str, Any]) -> dict[str, Any]:
    normalized = copy.deepcopy(instance)
    authorities = normalized["authorities"]
    normalized["authorities"] = sorted(
        authorities, key=canonical_bytes)
    return normalized


def domain_digest(domain: str, value: Any) -> str:
    try:
        prefix = _DOMAINS[domain]
    except KeyError as exc:
        raise AlgebraError(f"unknown identity domain: {domain}") from exc
    return hashlib.sha256(prefix + canonical_bytes(value)).hexdigest()


def _walk_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from _walk_dicts(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_dicts(item)


def alpha_normalize_shape(shape: dict[str, Any]) -> dict[str, Any]:
    validate_family_shape(shape)
    normalized = copy.deepcopy(shape)
    maps: dict[str, dict[str, str]] = {prefix: {} for prefix in _BINDER_FIELDS.values()}

    # Canonical traversal order, not spelling, determines local binder identity.
    for obj in _walk_dicts(normalized):
        for field, prefix in _BINDER_FIELDS.items():
            if field not in obj:
                continue
            original = obj[field]
            if not isinstance(original, str) or not original:
                raise AlgebraError(f"invalid local binder {field}")
            if original in maps[prefix]:
                raise AlgebraError(f"duplicate local binder {field}={original}")
            maps[prefix][original] = f"{prefix}{len(maps[prefix])}"
            obj[field] = maps[prefix][original]

    for obj in _walk_dicts(normalized):
        for field, prefix in _REFERENCE_FIELDS.items():
            if field not in obj:
                continue
            original = obj[field]
            if not isinstance(original, str) or original not in maps[prefix]:
                raise AlgebraError(f"dangling local reference {field}={original!r}")
            obj[field] = maps[prefix][original]
        for field in _SET_FIELDS:
            if field in obj:
                items = obj[field]
                if not isinstance(items, list):
                    raise AlgebraError(f"set-valued field {field} must be a list")
                if field in _SET_REFERENCE_FIELDS:
                    prefix = _SET_REFERENCE_FIELDS[field]
                    if any(not isinstance(item, str) or item not in maps[prefix]
                           for item in items):
                        raise AlgebraError(f"dangling local reference in {field}")
                    items = [maps[prefix][item] for item in items]
                keyed = [(canonical_bytes(item), item) for item in items]
                if len({key for key, _ in keyed}) != len(keyed):
                    raise AlgebraError(f"duplicate set member in {field}")
                obj[field] = [item for _, item in sorted(keyed, key=lambda pair: pair[0])]
    return normalized


def identity(domain: str, value: dict[str, Any]) -> str:
    expected = _SCHEMAS.get(domain)
    if expected is None:
        raise AlgebraError(f"unknown identity domain: {domain}")
    if value.get("schema") != expected:
        raise AlgebraError(f"{domain} schema mismatch")
    if domain == "family_shape":
        validate_family_shape(value)
        normalized = alpha_normalize_shape(value)
    elif domain == "protocol_instance":
        validate_protocol_instance(value)
        normalized = _normalize_protocol_instance(value)
    else:
        validate_deployment(value)
        normalized = value
    return domain_digest(domain, normalized)


def same_family_shape(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return identity("family_shape", left) == identity("family_shape", right)


def _enum_values(path: Path, class_name: str) -> list[str]:
    module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in module.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            values: list[str] = []
            for statement in node.body:
                if isinstance(statement, ast.Assign) and len(statement.targets) == 1 \
                        and isinstance(statement.targets[0], ast.Name) \
                        and isinstance(statement.value, ast.Constant) \
                        and isinstance(statement.value.value, str):
                    values.append(statement.value.value)
            return values
    raise AlgebraError(f"enum {class_name} not found in {path}")


def _literal_string_sequence(node: ast.AST, path: str) -> list[str]:
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
            and node.func.id == "sorted" and len(node.args) == 1:
        node = node.args[0]
    if not isinstance(node, (ast.List, ast.Tuple)):
        raise AlgebraError(f"{path} is not a literal string sequence")
    values: list[str] = []
    for element in node.elts:
        if not isinstance(element, ast.Constant) or not isinstance(element.value, str):
            raise AlgebraError(f"{path} contains a non-string literal")
        values.append(element.value)
    if len(values) != len(set(values)):
        raise AlgebraError(f"{path} contains duplicate exports")
    return values


def _module_surface(path: Path) -> tuple[dict[str, set[str]], set[str], set[str]]:
    module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: dict[str, set[str]] = {}
    definitions: set[str] = set()
    exports: set[str] | None = None
    for node in module.body:
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imports.setdefault(node.module, set()).update(
                alias.asname or alias.name for alias in node.names)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            definitions.add(node.name)
        elif isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "__all__"
                for target in node.targets):
            exports = set(_literal_string_sequence(node.value, f"{path}.__all__"))
    if exports is None:
        raise AlgebraError(f"{path} has no literal __all__")
    return imports, exports, definitions


def _literal_lazy_exports(path: Path) -> dict[str, tuple[str, str]]:
    module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in module.body:
        if not isinstance(node, ast.Assign) or not any(
                isinstance(target, ast.Name) and target.id == "_LAZY_EXPORTS"
                for target in node.targets):
            continue
        if not isinstance(node.value, ast.Dict):
            raise AlgebraError(f"{path}._LAZY_EXPORTS is not a literal dict")
        result: dict[str, tuple[str, str]] = {}
        for key_node, value_node in zip(node.value.keys, node.value.values):
            if not isinstance(key_node, ast.Constant) or not isinstance(key_node.value, str):
                raise AlgebraError(f"{path}._LAZY_EXPORTS has a non-string key")
            try:
                values = _literal_string_sequence(value_node, f"{path}._LAZY_EXPORTS")
            except AlgebraError:
                # Historical compatibility entries may contain expression-valued
                # aliases.  They are outside this census; required V4 entries are
                # checked below and must be literal two-string pairs.
                continue
            if len(values) != 2:
                raise AlgebraError(f"{path}._LAZY_EXPORTS value is not a pair")
            result[key_node.value] = (values[0], values[1])
        return result
    raise AlgebraError(f"{path} has no literal _LAZY_EXPORTS")


def _rehash_entry(repo: Path, raw: Any, path: str) -> str:
    row = _object(raw, path, {"path", "bytes", "sha256"})
    relative = Path(_string(row["path"], f"{path}.path"))
    if relative.is_absolute() or ".." in relative.parts:
        raise AlgebraError(f"{path}.path is unsafe")
    target = repo / relative
    if not target.is_file():
        raise AlgebraError(f"{path}.path is not a regular file")
    expected_bytes = _integer(row["bytes"], f"{path}.bytes")
    expected_sha = _hex_digest(row["sha256"], f"{path}.sha256")
    payload = target.read_bytes()
    if len(payload) != expected_bytes:
        raise AlgebraError(f"{path} byte count drift")
    if hashlib.sha256(payload).hexdigest() != expected_sha:
        raise AlgebraError(f"{path} SHA-256 drift")
    return relative.as_posix()


def _validate_custody_manifests(repo: Path) -> None:
    goal5831_path = repo / (
        "history/internal_docs/"
        "goal5831_public_gpu_surface_terminology_and_denominator_result_20260830.json")
    goal5831 = load_json_exact(goal5831_path)
    _require(goal5831.get("verdict") == "PASS_EXACT_CURRENT_SCOPE_FACTUAL_REPAIR",
             "Goal5831 custody result verdict drift")
    seen: set[str] = set()
    for section in ("source_authorities", "changed_scientific_documents"):
        for index, row in enumerate(_array(goal5831.get(section), f"goal5831.{section}")):
            relative = _rehash_entry(repo, row, f"goal5831.{section}[{index}]")
            if relative in seen:
                raise AlgebraError("Goal5831 custody manifest has duplicate paths")
            seen.add(relative)

    manifest_path = repo / (
        "history/internal_docs/goal5831_goal5832_artifact_manifest_v2_20260830.json")
    manifest = load_json_exact(manifest_path)
    _object(manifest, "artifact_manifest_v2", {
        "schema", "date", "supersedes", "repo_head_text", "git_object_status",
        "external_review_requested", "file_count_excluding_this_manifest",
        "artifacts",
    })
    _require(manifest["schema"] == "rtdl.goal5831_goal5832.artifact_manifest.v2",
             "artifact manifest v2 schema drift")
    _require(manifest["date"] == "2026-08-30", "artifact manifest date drift")
    _require(manifest["supersedes"] == {
        "path": "history/internal_docs/goal5831_goal5832_artifact_manifest_20260830.json",
        "bytes": 2471,
        "sha256": "a31f7491f3320734c99a07a4e506b801453eb4dbf8c8af804c681b9e66d3bc7d",
        "reason": "V1_PRECEDED_HOSTILE_P1_REPAIR_AND_BECAME_STALE",
    }, "artifact manifest v1 supersession drift")
    _require(manifest["external_review_requested"] is False,
             "artifact manifest review status drift")
    artifacts = _array(manifest["artifacts"], "artifact_manifest_v2.artifacts",
                       nonempty=True)
    _require(manifest["file_count_excluding_this_manifest"] == len(artifacts),
             "artifact manifest v2 count mismatch")
    paths = [
        _rehash_entry(repo, row, f"artifact_manifest_v2.artifacts[{index}]")
        for index, row in enumerate(artifacts)
    ]
    _require(len(paths) == len(set(paths)), "artifact manifest v2 duplicate path")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AlgebraError(message)


def validate_scope_authority(authority: dict[str, Any], repo: Path) -> None:
    _object(authority, "authority", {
        "schema", "date", "scope", "implementation_status", "terminology",
        "current_counts", "coverage_semantics", "platform_denominator",
        "current_public_surface", "selection_rationale", "identity_domains",
        "family_shape_axes", "axis_meanings", "canonicalization",
        "schema_validation", "equivalence", "support_matrix",
        "scientific_outcome_rules", "claim_ceiling",
    })
    _require(authority["schema"] ==
             "rtdl.goal5832.protocol_shape_algebra_authority.v1",
             "Goal5832 authority schema mismatch")
    _require(authority["date"] == "2026-08-30", "authority date drift")
    _require(authority["scope"] ==
             "terminology_denominator_three_domain_identity_equivalence_and_claim_ceiling_only",
             "authority scope drift")
    _require(authority["implementation_status"] ==
             "RESEARCH_SPECIFICATION_NOT_GENERIC_GPU_COMPILER",
             "implementation status overclaim or drift")
    terminology = _object(authority["terminology"], "terminology", {
        "build_input_kind", "leaf_primitive_kind", "physical_geometry_kind",
        "fixed_protocol_constructor", "bounded_user_authored_gpu_template",
        "application_semantic_protocol_shape", "protocol_instance",
        "deployment", "composition_batch",
    })
    for key, value in terminology.items():
        _string(value, f"terminology.{key}")
    counts = authority["current_counts"]
    _require(counts == {
        "optix9_build_input_kinds": 6,
        "optix9_leaf_primitive_kinds": 4,
        "rtdl_physical_geometry_kinds": 2,
        "fixed_protocol_constructors": 2,
        "bounded_user_authored_gpu_templates": 1,
        "public_application_specializations": 1,
        "composition_batches": 6,
        "project_authored_systems": 9,
        "project_authored_lanes": 13,
        "prospective_frozen_core_new_shape_exams": 0,
        "external_human_authors": 0,
        "application_semantic_shape_denominator": "OPEN_NO_FINITE_N",
    }, "current count ledger mismatch")

    _require(authority["coverage_semantics"] == {
        "classification": "KIND_PRESENCE_ONLY__NOT_FEATURE_COMPLETE",
        "instantiated_build_input_members": ["TRIANGLES", "CUSTOM_PRIMITIVES"],
        "build_input_ratio": "2/6",
        "leaf_primitive_ratio": "2/4",
        "not_category_closure": True,
        "not_application_semantic_coverage": True,
    }, "coverage semantics drift")

    header_path = repo / authority["platform_denominator"]["authority_path"]
    header = header_path.read_text(encoding="utf-8")
    header_values = re.findall(r"OPTIX_BUILD_INPUT_TYPE_[A-Z_]+\s*=\s*0x[0-9A-Fa-f]+", header)
    expected_header = [
        "OPTIX_BUILD_INPUT_TYPE_TRIANGLES",
        "OPTIX_BUILD_INPUT_TYPE_CUSTOM_PRIMITIVES",
        "OPTIX_BUILD_INPUT_TYPE_INSTANCES",
        "OPTIX_BUILD_INPUT_TYPE_INSTANCE_POINTERS",
        "OPTIX_BUILD_INPUT_TYPE_CURVES",
        "OPTIX_BUILD_INPUT_TYPE_SPHERES",
    ]
    _require(len(header_values) == 6, "pinned OptiX header build-input count drift")
    _require([item.split()[0] for item in header_values] == expected_header,
             "pinned OptiX build-input vocabulary drift")

    actual_geometry = _enum_values(
        repo / "src/rtdsl/v4_typed_physical_schema.py", "GeometryFamily")
    actual_protocol = _enum_values(
        repo / "src/rtdsl/v4_callback_lifecycle.py", "ProtocolFamily")
    _require(actual_geometry == ["custom_aabb", "builtin_triangle"],
             "GeometryFamily source drift")
    _require(actual_protocol == [
        "custom_aabb_bounded_relation_v1", "builtin_triangle_reduction_v1"],
        "ProtocolFamily source drift")

    _require(authority["current_public_surface"] == {
        "scope": "rtdsl.v4 stable surface plus explicitly named root deployment specialization",
        "physical_geometry_kinds": [
            {"id": "custom_aabb",
             "source": "src/rtdsl/v4_typed_physical_schema.py::GeometryFamily.CUSTOM_AABB"},
            {"id": "builtin_triangle",
             "source": "src/rtdsl/v4_typed_physical_schema.py::GeometryFamily.BUILTIN_TRIANGLE"},
        ],
        "fixed_protocol_constructors": [
            {"id": "custom_aabb_bounded_relation_v1",
             "physical_geometry_kind": "custom_aabb"},
            {"id": "builtin_triangle_reduction_v1",
             "physical_geometry_kind": "builtin_triangle"},
        ],
        "bounded_user_authored_gpu_templates": [{
            "id": "builtin_triangle_static_u32x3_two_metadata_v1",
            "physical_geometry_kind": "builtin_triangle",
            "static_gas_only": True,
            "payload_output": "u32x3",
            "primitive_aligned_u32_metadata_views": 2,
            "maximum_trace_depth": 1,
            "maximum_callable_depth": 0,
            "caller_supplies_restricted_source": True,
            "caller_supplies_ptx_sbt_pipeline_native": False,
            "source": "src/rtdsl/v4_public_builtin_triangle.py",
        }],
        "public_application_specializations": [{
            "id": "builtin_triangle_particle_strict_interior_v1",
            "classification": "EXISTING_TEMPLATE_STANDARD_LIBRARY_SPECIALIZATION",
            "new_general_template": False,
            "new_physical_geometry_kind": False,
            "new_fixed_protocol_constructor": False,
            "source": "src/rtdsl/v4_particle_rtdlexe.py",
        }],
        "composition_batches": [
            "M1_TRIANGLE_REDUCTION", "M2_BOUNDED_RELATION",
            "M3_PREPARED_MULTIROUND_SPATIAL", "M4_EXACT_PREDICATE_GLOBAL_WITNESS",
            "M5_GROUPED_EVENT_REDUCTION", "M6_HIERARCHY_FRONTIER"],
        "non_counted_surfaces": [
            "target_neutral_callback_ir_frontend_and_cpu_interpreter",
            "advanced_internal_v4_prepared_provider",
            "historical_non_v4_root_reexports",
            "stable_sort_existing_bounded_relation_instance"],
    }, "current public surface drift")

    public_path = repo / "src/rtdsl/v4.py"
    public_imports, public_exports, _ = _module_surface(public_path)
    authoring_exports = {
        "verify_builtin_triangle_callback_source",
        "build_builtin_triangle_u32x3_physical_plan",
        "compile_builtin_triangle_callback_program",
        "materialize_builtin_triangle_callback_program",
    }
    fixed_exports = {
        "BoundedRelationProtocol", "TriangleReductionProtocol",
        "compile_protocol_program", "materialize_protocol_program",
    }
    _require(authoring_exports <= public_imports.get("v4_public_builtin_triangle", set()),
             "bounded authoring imports missing from public V4 module")
    _require(authoring_exports <= public_exports,
             "bounded authoring names missing from public V4 __all__")
    _require(fixed_exports <= public_imports.get("v4_callback_lifecycle", set()),
             "fixed lifecycle imports missing from public V4 module")
    _require(fixed_exports <= public_exports,
             "fixed lifecycle names missing from public V4 __all__")
    template_path = repo / "src/rtdsl/v4_public_builtin_triangle.py"
    _, template_exports, template_definitions = _module_surface(template_path)
    _require(authoring_exports <= template_exports,
             "bounded authoring names missing from template __all__")
    _require(authoring_exports <= template_definitions,
             "bounded authoring entrypoints are not top-level definitions")
    template_source = template_path.read_text(encoding="utf-8")
    for phrase in ("user-authored restricted", "exactly three ``u32``", "two primitive-aligned"):
        _require(phrase in template_source, f"bounded template fact missing: {phrase}")
    particle_source = (
        repo / "src/rtdsl/v4_particle_rtdlexe.py").read_text(encoding="utf-8")
    _require("STRICT_INTERIOR_STANDARD_LIBRARY_SPECIALIZATION_ONLY" in particle_source,
             "Particle specialization boundary missing")
    _require('"arbitrary_user_dsl_generalization_claimed": False' in particle_source,
             "Particle non-generality boundary missing")
    lazy = _literal_lazy_exports(repo / "src/rtdsl/__init__.py")
    for name in (
            "build_particle_rtdlexe", "install_particle_rtdlexe_deployment",
            "load_particle_rtdlexe"):
        _require(lazy.get(name) == (".v4_particle_rtdlexe", name),
                 f"Particle root public export drift: {name}")

    platform = authority["platform_denominator"]["build_inputs"]
    _require(len(platform) == 6, "authority platform row count mismatch")
    _require(sum(row["leaf_primitive"] for row in platform) == 4,
             "authority leaf-primitive denominator mismatch")
    _require(sum(row["rtdl_public_gpu_kind_presence"] for row in platform) == 2,
             "authority RTDL build-input coverage mismatch")
    for row in platform:
        _object(row, f"platform.{row.get('id', '?')}", {
            "id", "leaf_primitive", "scene_graph_input",
            "rtdl_public_gpu_kind_presence"})
        expected = row["id"] in {"TRIANGLES", "CUSTOM_PRIMITIVES"}
        _require(row["rtdl_public_gpu_kind_presence"] is expected,
                 f"unsupported build input promoted: {row['id']}")

    _require(authority["selection_rationale"] == {
        "custom_primitive_boundary": "callback-produced intersection and attribute path",
        "builtin_triangle_boundary": "platform-produced intersection and builtin hit path",
        "cohort_fit": "the author-written paper cohort mapped to these two physical kinds",
        "selection_was_prospective": False,
        "representative_sample_claimed": False,
        "generalization_evidence_count": 0,
    }, "selection rationale drift")

    domains = authority["identity_domains"]
    _require(list(domains) == ["family_shape", "protocol_instance", "deployment"],
             "identity-domain order or membership drift")
    expected_domain_membership = {
        "family_shape": {
            "contains": [
                "physical_build_and_scene_graph", "callback_role_topology",
                "typed_views", "role_effects",
                "hit_channel_producer_consumer_ownership",
                "buffer_gas_ias_sbt_bindings", "result_operator_pipeline",
                "continuation_status_commit_automaton", "identity_bind_set",
                "numeric_and_resource_limits"],
            "excludes": [
                "application_names", "dataset_names", "record_spelling",
                "nominal_semantic_parameter_values", "target_identity",
                "provider_binary", "actual_executable"],
        },
        "protocol_instance": {
            "contains": [
                "family_shape_identity", "typed_parameter_values",
                "nominal_semantic_values", "callback_source_identity",
                "callback_ir_identity", "effect_identity", "abi_identity",
                "proof_authorities"],
            "excludes": [
                "target_identity", "provider_binary", "actual_executable"],
        },
        "deployment": {
            "contains": [
                "protocol_instance_identity", "target_profile_identity",
                "physical_schema_identity", "provider_identity",
                "generated_device_source_identity", "generated_host_source_identity",
                "provider_binary_identity", "actual_executable_identity"],
            "excludes": [],
        },
    }
    for name, domain in domains.items():
        _object(domain, f"identity_domains.{name}", {
            "schema", "domain_separator", "contains", "excludes"})
        _require(domain["schema"] == _SCHEMAS[name], f"{name} schema drift")
        _require(domain["domain_separator"] == _DOMAINS[name].decode("ascii"),
                 f"{name} domain separator drift")
        _require({
            "contains": domain["contains"], "excludes": domain["excludes"]
        } == expected_domain_membership[name], f"{name} membership drift")
    _require(authority["family_shape_axes"] == ["G", "R", "V", "E", "H", "B", "C", "X", "L"],
             "family-shape axes drift")
    _require(set(authority["axis_meanings"]) == set(authority["family_shape_axes"]),
             "family-shape axis meanings drift")
    for axis, meaning in authority["axis_meanings"].items():
        _string(meaning, f"axis_meanings.{axis}")

    _require(authority["canonicalization"] == {
        "encoding": "UTF8_JSON_CANONICAL_ASCII_ESCAPES",
        "duplicate_keys": "REJECT",
        "unknown_normative_keys": "REJECT_BY_SCHEMA",
        "nan_infinity": "REJECT",
        "json_floats": "REJECT_USE_EXACT_BIT_TEXT",
        "bool_as_integer": "REJECT_BY_TYPED_SCHEMA",
        "local_binder_alpha_normalization": [
            "parameter_id", "node_id", "buffer_id", "channel_id", "event_id",
            "state_id"],
        "set_sorted_fields": [
            "capabilities", "allowed_effects", "required_effects",
            "terminal_states", "identity_bind_set", "authorities"],
        "order_preserved_fields": [
            "callback_arguments", "graph_nodes_and_edges",
            "buffer_channel_ordinals", "result_operator_pipeline",
            "continuation_transitions"],
        "fuzzy_or_manual_equivalence": "FORBIDDEN",
    }, "canonicalization contract drift")
    _require(authority["schema_validation"] == {
        "family_shape": "EXACT_RECURSIVE_TYPED_AND_CROSS_REFERENCE_VALIDATION_IMPLEMENTED",
        "protocol_instance": "EXACT_TYPED_BINDINGS_AND_AUTHORITY_SET_VALIDATION_IMPLEMENTED",
        "deployment": "EXACT_TARGET_PROVIDER_GENERATED_AND_EXECUTABLE_BINDING_VALIDATION_IMPLEMENTED",
        "schema_only_or_unknown_key_documents": "REJECT",
        "bool_as_integer": "REJECT",
        "role_effect_compatibility": "ENFORCED",
        "instance_against_shape_typed_binding": "ENFORCED_BY_EXPLICIT_CROSS_VALIDATOR",
    }, "schema-validation contract drift")
    _require(authority["equivalence"] == {
        "same_family_shape": "domain-separated canonical bytes equal after local-binder alpha normalization and set-only sorting",
        "same_protocol_instance": "family shape plus typed parameters, nominal semantics, Callback IR, ABI, and proof bindings equal",
        "same_deployment": "protocol instance plus target, provider, generated artifacts, native binary, and actual executable equal",
        "nominal_semantics_may_be_erased_from_instance_identity": False,
        "target_changes_family_shape": False,
        "application_or_dataset_name_changes_family_shape": False,
        "role_or_channel_ownership_change_changes_family_shape": True,
        "continuation_or_result_operator_order_change_changes_family_shape": True,
    }, "equivalence contract drift")

    expected_support = [
        {"feature": "custom_aabb_leaf_primitive", "vocabulary": "SUPPORTED",
         "verifier": "SUPPORTED", "provider_codegen": "SUPPORTED_FIXED_ROUTE",
         "public_lifecycle": "SUPPORTED_FIXED_CONSTRUCTOR", "true_gpu_evidence": "SUPPORTED"},
        {"feature": "builtin_triangle_leaf_primitive", "vocabulary": "SUPPORTED",
         "verifier": "SUPPORTED", "provider_codegen": "SUPPORTED",
         "public_lifecycle": "SUPPORTED_FIXED_AND_BOUNDED_AUTHORING", "true_gpu_evidence": "SUPPORTED"},
        {"feature": "curves_leaf_primitive", "vocabulary": "UNSUPPORTED",
         "verifier": "UNSUPPORTED", "provider_codegen": "UNSUPPORTED",
         "public_lifecycle": "UNSUPPORTED", "true_gpu_evidence": "NONE"},
        {"feature": "spheres_leaf_primitive", "vocabulary": "UNSUPPORTED",
         "verifier": "UNSUPPORTED", "provider_codegen": "UNSUPPORTED",
         "public_lifecycle": "UNSUPPORTED", "true_gpu_evidence": "NONE"},
        {"feature": "instances_scene_graph", "vocabulary": "UNSUPPORTED",
         "verifier": "UNSUPPORTED", "provider_codegen": "UNSUPPORTED",
         "public_lifecycle": "UNSUPPORTED", "true_gpu_evidence": "NONE"},
        {"feature": "instance_pointer_scene_graph", "vocabulary": "UNSUPPORTED",
         "verifier": "UNSUPPORTED", "provider_codegen": "UNSUPPORTED",
         "public_lifecycle": "UNSUPPORTED", "true_gpu_evidence": "NONE"},
        {"feature": "single_static_gas_trace_depth_one_callable_depth_zero",
         "vocabulary": "SUPPORTED", "verifier": "SUPPORTED",
         "provider_codegen": "SUPPORTED", "public_lifecycle": "SUPPORTED",
         "true_gpu_evidence": "SUPPORTED"},
        {"feature": "graph_depth_greater_than_one",
         "vocabulary": "PARTIAL_INTEGER_FIELD_EXISTS",
         "verifier": "REJECTED_BY_CURRENT_BOUND", "provider_codegen": "UNSUPPORTED",
         "public_lifecycle": "UNSUPPORTED", "true_gpu_evidence": "NONE"},
        {"feature": "trace_depth_greater_than_one_or_callable_depth_positive",
         "vocabulary": "PARTIAL_RESOURCE_FIELD_EXISTS",
         "verifier": "REJECTED_BY_CURRENT_BOUND", "provider_codegen": "UNSUPPORTED",
         "public_lifecycle": "UNSUPPORTED", "true_gpu_evidence": "NONE"},
        {"feature": "arbitrary_verified_callback_ir_to_gpu",
         "vocabulary": "CALLBACK_IR_EXISTS", "verifier": "TARGET_NEUTRAL_ONLY",
         "provider_codegen": "UNSUPPORTED_GENERAL_ROUTE",
         "public_lifecycle": "UNSUPPORTED", "true_gpu_evidence": "NONE"},
    ]
    _require(authority["support_matrix"] == expected_support,
             "support matrix overclaim or drift")

    rules = authority["scientific_outcome_rules"]
    required_rules = {
        "new_app_existing_shape": "REUSE_NOT_NEW_SHAPE_EVIDENCE",
        "new_shape_cpu_only": "NO_GPU_EXTENSION_EVIDENCE",
        "copy_paste_route": "IMPLEMENTATION_COVERAGE_NOT_PARAMETRICITY",
        "core_changes_after_freeze": "PROSPECTIVE_EXAM_FAIL",
        "repair_same_challenge": "NOT_PROSPECTIVE_SUCCESS",
        "unexpressible_shape": "UNMAPPED_NO_COERCION",
    }
    _require(rules == required_rules, "scientific outcome rules drift")
    ceiling = authority["claim_ceiling"]
    expected_supported = [
        "current_scope_is_exactly_two_physical_geometry_kinds",
        "current_surface_has_two_fixed_protocol_constructors",
        "current_surface_has_one_bounded_user_authored_triangle_template",
        "platform_kind_presence_is_two_of_six_build_inputs_and_two_of_four_leaf_primitives_not_feature_complete",
        "application_semantic_protocol_shape_universe_is_open",
        "protocol_shape_instance_and_deployment_are_separate_normative_identities",
        "future_family_parametric_claim_must_be_scoped_to_shapes_expressible_by_a_separately_implemented_schema",
    ]
    expected_forbidden = [
        "all_rt_protocols", "arbitrary_repurposed_applications",
        "complete_optix_coverage", "universal_callback_ir_to_gpu",
        "family_parametric_gpu_compiler_implemented",
        "prospective_new_shape_generalization", "third_party_usability",
    ]
    _require(ceiling == {
        "supported_claims": expected_supported,
        "forbidden_claims": expected_forbidden,
        "prospective_generalization_count": 0,
        "external_author_count": 0,
        "goal5832_product_or_gpu_bytes_changed": False,
    }, "claim ceiling overclaim or drift")
    _require(set(expected_supported).isdisjoint(expected_forbidden),
             "supported and forbidden claims conflict")

    paper = (repo / "paper/cgo2027/main.tex").read_text(encoding="utf-8")
    for required in (
        "two fixed protocol constructors",
        "two of six OptiX~9 build-input enum kinds",
        "kind presence rather than",
        "application-semantic protocol shapes has no finite coverage denominator",
        "one bounded user-authored built-in-triangle",
        "prospective frozen-core extension exams remain zero",
    ):
        _require(required in paper, f"paper scope statement missing: {required}")
    for forbidden in (
        "exactly two closed public protocol families",
        "Caller-supplied restricted source and Callback IR are not GPU extension points",
        "There are exactly two closed public GPU protocol families",
    ):
        _require(forbidden not in paper, f"misleading paper statement remains: {forbidden}")
    _validate_custody_manifests(repo)


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    args = parser.parse_args()
    authority = load_json_exact(args.authority)
    validate_scope_authority(authority, args.repo)
    print("GOAL5832_PROTOCOL_SHAPE_AUTHORITY_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
