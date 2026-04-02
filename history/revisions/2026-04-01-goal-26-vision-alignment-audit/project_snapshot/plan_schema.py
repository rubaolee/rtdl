from __future__ import annotations

import json
from pathlib import Path


def schema_path() -> Path:
    return Path(__file__).resolve().parents[2] / "schemas" / "rtdl_plan.schema.json"


def load_plan_schema() -> dict[str, object]:
    return json.loads(schema_path().read_text(encoding="utf-8"))


def validate_plan_dict(instance: object, schema: dict[str, object] | None = None) -> None:
    schema = schema or load_plan_schema()
    validate_json(instance, schema, root_schema=schema, path="$")


def validate_json(
    instance: object,
    schema: dict[str, object],
    *,
    root_schema: dict[str, object],
    path: str,
) -> None:
    if "$ref" in schema:
        ref = schema["$ref"]
        if not isinstance(ref, str) or not ref.startswith("#/definitions/"):
            raise ValueError(f"{path}: unsupported schema reference {ref!r}")
        definition_name = ref.split("/")[-1]
        definition = root_schema.get("definitions", {}).get(definition_name)
        if not isinstance(definition, dict):
            raise ValueError(f"{path}: missing schema definition {definition_name!r}")
        validate_json(instance, definition, root_schema=root_schema, path=path)
        return

    schema_type = schema.get("type")
    if schema_type is not None:
        _validate_type(instance, schema_type, path)

    if "const" in schema and instance != schema["const"]:
        raise ValueError(f"{path}: expected const value {schema['const']!r}, got {instance!r}")

    if "enum" in schema and instance not in schema["enum"]:
        raise ValueError(f"{path}: expected one of {schema['enum']!r}, got {instance!r}")

    if schema_type == "object":
        _validate_object(instance, schema, root_schema, path)
    elif schema_type == "array":
        _validate_array(instance, schema, root_schema, path)


def _validate_type(instance: object, schema_type: str, path: str) -> None:
    valid = False
    if schema_type == "object":
        valid = isinstance(instance, dict)
    elif schema_type == "array":
        valid = isinstance(instance, list)
    elif schema_type == "string":
        valid = isinstance(instance, str)
    elif schema_type == "integer":
        valid = isinstance(instance, int) and not isinstance(instance, bool)
    elif schema_type == "number":
        valid = isinstance(instance, (int, float)) and not isinstance(instance, bool)
    elif schema_type == "boolean":
        valid = isinstance(instance, bool)
    elif schema_type == "null":
        valid = instance is None

    if not valid:
        raise ValueError(f"{path}: expected {schema_type}, got {type(instance).__name__}")


def _validate_object(
    instance: object,
    schema: dict[str, object],
    root_schema: dict[str, object],
    path: str,
) -> None:
    assert isinstance(instance, dict)
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    additional_properties = schema.get("additionalProperties", True)

    for key in required:
        if key not in instance:
            raise ValueError(f"{path}: missing required key {key!r}")

    if additional_properties is False:
        unexpected = sorted(set(instance.keys()) - set(properties.keys()))
        if unexpected:
            raise ValueError(f"{path}: unexpected keys {unexpected!r}")

    for key, value in instance.items():
        subschema = properties.get(key)
        if isinstance(subschema, dict):
            validate_json(value, subschema, root_schema=root_schema, path=f"{path}.{key}")


def _validate_array(
    instance: object,
    schema: dict[str, object],
    root_schema: dict[str, object],
    path: str,
) -> None:
    assert isinstance(instance, list)
    item_schema = schema.get("items")
    if not isinstance(item_schema, dict):
        return

    for index, item in enumerate(instance):
        validate_json(item, item_schema, root_schema=root_schema, path=f"{path}[{index}]")
