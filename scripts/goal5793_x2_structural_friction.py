#!/usr/bin/env python3
"""Frozen structural-friction measurements for every Goal5793 lineage.

These measurements describe integration responsibility and abstraction
leakage.  They are not a human usability or productivity study.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any, Mapping, Sequence

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


SCHEMA = "rtdl.goal5793.x2.structural_friction_lineage.v1"
STAGE_ORDER = (
    "SOURCE_PROJECTION",
    "SEMANTIC_AUTHORITY",
    "PHYSICAL_GUARANTEE",
    "CALLBACK_IR",
    "EFFECTS",
    "ABI",
    "PTX",
    "WRAPPER",
    "LAYOUT",
    "NATIVE",
    "ADMISSION",
    "COMPILE",
    "EXECUTION_RECEIPT",
)

PUBLIC_CALLABLES = frozenset(
    {
        "rtdsl.v4_semantically_admitted_compiler.admit_builtin_triangle_compilation",
        "rtdsl.v4_semantically_admitted_compiler.admit_triangle_reduction_compilation",
        "rtdsl.v4_semantically_admitted_compiler.admit_bounded_relation_compilation",
        "rtdsl.v4_semantically_admitted_compiler.compile_semantically_admitted_builtin_triangle",
        "rtdsl.v4_semantically_admitted_compiler.compile_semantically_admitted_triangle_reduction",
        "rtdsl.v4_semantically_admitted_compiler.compile_semantically_admitted_bounded_relation",
        "rtdsl.v4_semantically_admitted_compiler.run_semantically_admitted_builtin_triangle",
        "rtdsl.v4_semantically_admitted_compiler.run_semantically_admitted_triangle_reduction",
        "rtdsl.v4_semantically_admitted_compiler.run_semantically_admitted_bounded_relation",
        "rtdsl.v4_callback_frontend.parse_callback_source",
        "rtdsl.v4_callback_frontend.verify_callback_source",
    }
)
PRIVATE_CALLABLES = frozenset(
    {
        "rtdsl.v4_semantic_physical_admission._issue_compiler_physical_guarantee_registry",
        "rtdsl.optix_runtime._load_optix_library",
        "scripts.goal5793_x1_registry_derivation.build_registry_authority",
        "scripts.goal5793_x1_generic_examiner.examine",
    }
)
RAW_TOKEN_REGISTRY = (
    "OptiX",
    "optix",
    "CUDA",
    "cuda",
    "cuMem",
    "cuLaunchKernel",
    "optixLaunch",
    "optixTrace",
    "OptixDeviceContext",
    "OptixPipeline",
    "OptixShaderBindingTable",
    "cudaMalloc",
    "cudaMemcpy",
    "cudaFree",
    "<optix.h>",
    "<cuda.h>",
    "<cuda_runtime.h>",
)


class FrictionError(ValueError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _safe_relative(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value or re.match(r"^[A-Za-z]:", value):
        raise FrictionError("UNSAFE_APP_SOURCE_PATH")
    path = PurePosixPath(value)
    if path.is_absolute() or path.as_posix() != value or ".." in path.parts or "." in path.parts:
        raise FrictionError("UNSAFE_APP_SOURCE_PATH")
    return value


def _metric(value: Any, unit: str, pins: list[dict[str, Any]]) -> dict[str, Any]:
    if not pins:
        raise FrictionError("VALUE_METRIC_SOURCE_PINS_EMPTY")
    return {"status": "VALUE", "value": value, "unit": unit, "reason": None, "source_pins": pins}


def _na(unit: str, reason: str, pins: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    if not isinstance(reason, str) or not reason:
        raise FrictionError("NA_METRIC_REASON_EMPTY")
    return {"status": "NA", "value": None, "unit": unit, "reason": reason, "source_pins": pins or []}


def _resolve_calls(text: str, path: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    try:
        tree = ast.parse(text, filename=path)
    except SyntaxError as exc:
        raise FrictionError("APP_SOURCE_PYTHON_AST_INVALID") from exc
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                aliases[alias.asname or alias.name.split(".")[0]] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                aliases[alias.asname or alias.name] = f"{node.module}.{alias.name}"

    def expression_name(node: ast.AST) -> str | None:
        parts: list[str] = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            root = aliases.get(current.id, current.id)
            return ".".join([root, *reversed(parts)]) if parts else root
        return None

    public: list[dict[str, Any]] = []
    private: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = expression_name(node.func)
        row = {"path": path, "line": node.lineno, "column": node.col_offset, "callable": name}
        if name in PUBLIC_CALLABLES:
            public.append(row)
        elif name in PRIVATE_CALLABLES or (name is not None and any(part.startswith("_") for part in name.split("."))):
            private.append(row)
        else:
            unresolved.append(row)
    key = lambda row: (row["path"].encode("utf-8"), row["line"], row["column"], str(row["callable"]).encode("utf-8"))
    return sorted(public, key=key), sorted(private, key=key), sorted(unresolved, key=key)


def _raw_tokens(text: str, path: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        for token in RAW_TOKEN_REGISTRY:
            start = 0
            while True:
                index = line.find(token, start)
                if index < 0:
                    break
                before = line[index - 1] if index else ""
                after_index = index + len(token)
                after = line[after_index] if after_index < len(line) else ""
                word_token = token[0].isalnum() and token[-1].isalnum()
                if not word_token or (not (before.isalnum() or before == "_") and not (after.isalnum() or after == "_")):
                    rows.append({"path": path, "line": line_number, "column": index, "token": token})
                start = index + max(1, len(token))
    rows.sort(key=lambda row: (row["path"].encode("utf-8"), row["line"], row["column"], row["token"].encode("utf-8")))
    return rows


def _validate_scalar_paths(values: Any, reason: str) -> list[str]:
    if not isinstance(values, list) or any(not isinstance(item, str) or not item for item in values):
        raise FrictionError(reason)
    if len(set(values)) != len(values):
        raise FrictionError(reason)
    return sorted(values, key=lambda value: value.encode("utf-8"))


def measure_lineage(source_root: Path, lineage: Mapping[str, Any]) -> dict[str, Any]:
    required = {
        "schema",
        "lineage_id",
        "predecessor_lineage_ids",
        "app_owned_files",
        "generated_paths",
        "authority_scalar_paths",
        "stage_records",
        "failures",
        "baseline",
    }
    if set(lineage) != required or lineage.get("schema") != SCHEMA:
        raise FrictionError("FRICTION_LINEAGE_SCHEMA_MISMATCH")
    lineage_id = lineage["lineage_id"]
    if not isinstance(lineage_id, str) or not lineage_id:
        raise FrictionError("FRICTION_LINEAGE_ID_INVALID")
    predecessors = lineage["predecessor_lineage_ids"]
    if not isinstance(predecessors, list) or any(not isinstance(value, str) or not value for value in predecessors):
        raise FrictionError("FRICTION_PREDECESSOR_SCHEMA_INVALID")
    if len(set(predecessors)) != len(predecessors):
        raise FrictionError("FRICTION_PREDECESSOR_DUPLICATE")
    generated = {_safe_relative(value) for value in lineage["generated_paths"]}
    files = lineage["app_owned_files"]
    if not isinstance(files, list) or not files:
        raise FrictionError("FRICTION_APP_FILE_SET_EMPTY")
    seen: set[str] = set()
    pins: list[dict[str, Any]] = []
    physical_line_count = 0
    public_calls: list[dict[str, Any]] = []
    private_calls: list[dict[str, Any]] = []
    unresolved_calls: list[dict[str, Any]] = []
    raw_tokens: list[dict[str, Any]] = []
    for identity in files:
        if not isinstance(identity, Mapping) or set(identity) != {"path", "bytes", "sha256"}:
            raise FrictionError("FRICTION_APP_FILE_IDENTITY_SCHEMA_INVALID")
        relative = _safe_relative(identity["path"])
        if relative in seen or relative in generated:
            raise FrictionError("FRICTION_APP_FILE_DUPLICATE_OR_GENERATED")
        seen.add(relative)
        path = source_root.joinpath(*PurePosixPath(relative).parts)
        if not path.is_file() or path.is_symlink():
            raise FrictionError("FRICTION_APP_FILE_MISSING_OR_NONREGULAR")
        raw = path.read_bytes()
        if len(raw) != identity["bytes"] or hashlib.sha256(raw).hexdigest() != identity["sha256"]:
            raise FrictionError("FRICTION_APP_FILE_IDENTITY_MISMATCH")
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise FrictionError("FRICTION_APP_FILE_NOT_STRICT_UTF8") from exc
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        physical_line_count += sum(bool(line.strip(" \t\v\f")) for line in normalized.split("\n"))
        if relative.endswith(".py"):
            pub, priv, unresolved = _resolve_calls(normalized, relative)
            public_calls.extend(pub)
            private_calls.extend(priv)
            unresolved_calls.extend(unresolved)
        raw_tokens.extend(_raw_tokens(normalized, relative))
        pins.append({"path": relative, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    pins.sort(key=lambda row: row["path"].encode("utf-8"))
    authorities = lineage["authority_scalar_paths"]
    if not isinstance(authorities, Mapping) or set(authorities) != {"manual", "defaulted", "derived", "unresolved"}:
        raise FrictionError("FRICTION_AUTHORITY_FIELDS_SCHEMA_MISMATCH")
    authority_sets = {key: _validate_scalar_paths(authorities[key], "FRICTION_AUTHORITY_FIELD_PATH_INVALID") for key in authorities}
    if len(set().union(*map(set, authority_sets.values()))) != sum(len(values) for values in authority_sets.values()):
        raise FrictionError("FRICTION_AUTHORITY_FIELD_CLASS_OVERLAP")
    stage_records = lineage["stage_records"]
    if not isinstance(stage_records, list):
        raise FrictionError("FRICTION_STAGE_RECORDS_SCHEMA_MISMATCH")
    by_stage: dict[str, Mapping[str, Any]] = {}
    for record in stage_records:
        if not isinstance(record, Mapping) or set(record) != {"stage", "status", "artifact", "reason"}:
            raise FrictionError("FRICTION_STAGE_RECORD_SCHEMA_MISMATCH")
        stage = record["stage"]
        if stage not in STAGE_ORDER or stage in by_stage:
            raise FrictionError("FRICTION_STAGE_INVALID_OR_DUPLICATE")
        if record["status"] not in ("PRESENT", "ABSENT"):
            raise FrictionError("FRICTION_STAGE_STATUS_INVALID")
        if record["status"] == "PRESENT":
            artifact = record["artifact"]
            if not isinstance(artifact, Mapping) or set(artifact) != {"path", "bytes", "sha256"} or record["reason"] is not None:
                raise FrictionError("FRICTION_PRESENT_STAGE_SCHEMA_INVALID")
        elif record["artifact"] is not None or not isinstance(record["reason"], str) or not record["reason"]:
            raise FrictionError("FRICTION_ABSENT_STAGE_REASON_INVALID")
        by_stage[stage] = record
    normalized_stages = [
        dict(by_stage.get(stage, {"stage": stage, "status": "ABSENT", "artifact": None, "reason": "NOT_REACHED_OR_NOT_EMITTED"}))
        for stage in STAGE_ORDER
    ]
    failures = lineage["failures"]
    if not isinstance(failures, list):
        raise FrictionError("FRICTION_FAILURE_SCHEMA_MISMATCH")
    normalized_failures: list[dict[str, str]] = []
    for failure in failures:
        if not isinstance(failure, Mapping) or set(failure) != {"stage", "reason"} or failure["stage"] not in STAGE_ORDER:
            raise FrictionError("FRICTION_FAILURE_SCHEMA_MISMATCH")
        normalized_failures.append({"stage": failure["stage"], "reason": str(failure["reason"])})
    normalized_failures.sort(key=lambda row: (STAGE_ORDER.index(row["stage"]), row["reason"].encode("utf-8")))
    baseline = lineage["baseline"]
    if not isinstance(baseline, Mapping) or set(baseline) != {"status", "reason", "source_pins"}:
        raise FrictionError("FRICTION_BASELINE_SCHEMA_MISMATCH")
    if baseline["status"] not in ("EXACT_FUNCTIONALLY_MATCHED", "NA"):
        raise FrictionError("FRICTION_BASELINE_STATUS_INVALID")
    if baseline["status"] == "NA" and (not isinstance(baseline["reason"], str) or not baseline["reason"]):
        raise FrictionError("FRICTION_BASELINE_NA_REASON_INVALID")
    if baseline["status"] == "EXACT_FUNCTIONALLY_MATCHED" and (baseline["reason"] is not None or not baseline["source_pins"]):
        raise FrictionError("FRICTION_BASELINE_EXACT_SCHEMA_INVALID")
    metrics = {
        "app_owned_file_count": _metric(len(pins), "files", pins),
        "app_owned_nonblank_physical_source_lines": _metric(physical_line_count, "lines", pins),
        "public_api_calls": _metric(len(public_calls), "unique_static_call_sites", pins),
        "private_api_calls": _metric(len(private_calls), "unique_static_call_sites", pins),
        "unresolved_api_calls": _metric(len(unresolved_calls), "unique_static_call_sites", pins),
        "manual_authority_fields": _metric(len(authority_sets["manual"]), "unique_scalar_leaf_paths", pins),
        "raw_cuda_optix_tokens": _metric(len(raw_tokens), "lexical_occurrences", pins),
        "generated_stage_inventory": _metric(normalized_stages, "stage_records", pins),
        "first_diagnostic_failure_location": (
            _metric(normalized_failures[0], "stage_enum_or_NA", pins)
            if normalized_failures
            else _na("stage_enum_or_NA", "NO_RECORDED_FAILURE", pins)
        ),
        "author_or_direct_baseline": (
            _metric(dict(baseline), "exact_source_responsibility_comparison", list(baseline["source_pins"]))
            if baseline["status"] == "EXACT_FUNCTIONALLY_MATCHED"
            else _na("exact_source_responsibility_comparison", str(baseline["reason"]), list(baseline["source_pins"]))
        ),
    }
    result: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.structural_friction_measurement.v1",
        "lineage_id": lineage_id,
        "predecessor_lineage_ids": sorted(predecessors, key=lambda value: value.encode("utf-8")),
        "source_pins": pins,
        "metrics": metrics,
        "details": {
            "public_api_call_sites": public_calls,
            "private_api_call_sites": private_calls,
            "unresolved_api_call_sites": unresolved_calls,
            "raw_cuda_optix_token_sites": raw_tokens,
            "authority_scalar_paths": authority_sets,
            "stage_records": normalized_stages,
            "failures": normalized_failures,
        },
        "interpretation": "STRUCTURAL_INTEGRATION_RESPONSIBILITY_AND_ABSTRACTION_LEAKAGE_ONLY__NOT_HUMAN_USABILITY_OR_PRODUCTIVITY",
        "supports_easy_productive_simpler_less_code_or_better_than_cuda_claim": False,
        "measurement_sha256": "",
    }
    result["measurement_sha256"] = seal_document(
        result,
        seal_field="measurement_sha256",
        domain="rtdl.goal5793.x2.structural_friction_measurement",
        version=1,
    )
    return result


def rows_digest(rows: Sequence[Mapping[str, Any]]) -> str:
    ordered = sorted(rows, key=lambda row: str(row["lineage_id"]).encode("utf-8"))
    if len({row["lineage_id"] for row in ordered}) != len(ordered):
        raise FrictionError("FRICTION_LINEAGE_ID_DUPLICATE")
    return hashlib.sha256(canonical_json_bytes(ordered)).hexdigest()

