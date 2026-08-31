#!/usr/bin/env python3
"""Append-only structural-friction measurement successor.

V2 excludes prose from CUDA/OptiX lexical counts, recognizes idiomatic
identifier/header families, fixes dotted-import resolution, and limits the
"unresolved" counter to RTDL/project namespaces.  It remains structural
evidence only, never a human usability or productivity result.
"""

from __future__ import annotations

import ast
import io
from pathlib import Path, PurePosixPath
import re
import tokenize
from typing import Any, Mapping

from scripts.goal5793_x1_canonical import seal_document
from scripts import goal5793_x2_structural_friction as v1


SCHEMA = "rtdl.goal5793.x2.structural_friction_lineage.v1"
MEASUREMENT_DOMAIN = "rtdl.goal5793.x2.structural_friction_measurement.v2"


def _resolve_calls(text: str, path: str):
    try:
        tree = ast.parse(text, filename=path)
    except SyntaxError as exc:
        raise v1.FrictionError("APP_SOURCE_PYTHON_AST_INVALID") from exc
    aliases: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    aliases[alias.asname] = alias.name
                else:
                    root = alias.name.split(".", 1)[0]
                    aliases[root] = root
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

    public = []
    private = []
    unresolved_rtdl = []
    excluded_non_rtdl = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = expression_name(node.func)
        row = {"path": path, "line": node.lineno, "column": node.col_offset, "callable": name}
        if name in v1.PUBLIC_CALLABLES:
            public.append(row)
        elif name in v1.PRIVATE_CALLABLES or (
            name is not None
            and (name.startswith("rtdsl.") or name.startswith("scripts.goal5793"))
            and any(part.startswith("_") for part in name.split("."))
        ):
            private.append(row)
        elif name is not None and (name.startswith("rtdsl.") or name.startswith("scripts.goal5793")):
            unresolved_rtdl.append(row)
        else:
            excluded_non_rtdl.append(row)
    key = lambda row: (row["path"].encode("utf-8"), row["line"], row["column"], str(row["callable"]).encode("utf-8"))
    return tuple(sorted(rows, key=key) for rows in (public, private, unresolved_rtdl, excluded_non_rtdl))


def _identifier_class(token: str) -> str | None:
    if token.startswith("CUDA_"):
        return "CUDA_MACRO_OR_ENUM_PREFIX"
    if token.startswith("OPTIX_"):
        return "OPTIX_MACRO_OR_ENUM_PREFIX"
    if token.startswith("cuda"):
        return "CUDA_RUNTIME_IDENTIFIER_PREFIX"
    if token.startswith("optix"):
        return "OPTIX_FUNCTION_IDENTIFIER_PREFIX"
    if token.startswith("Optix"):
        return "OPTIX_TYPE_IDENTIFIER_PREFIX"
    if re.match(r"^(?:cu|CU)[A-Z]", token):
        return "CUDA_DRIVER_IDENTIFIER_PREFIX"
    return None


def _mask_c_comments_and_literals(text: str) -> str:
    output = list(text)
    index = 0
    state = "CODE"
    quote = ""
    while index < len(text):
        char = text[index]
        nxt = text[index + 1] if index + 1 < len(text) else ""
        if state == "CODE":
            if char == "/" and nxt == "/":
                output[index] = output[index + 1] = " "
                state = "LINE_COMMENT"; index += 2; continue
            if char == "/" and nxt == "*":
                output[index] = output[index + 1] = " "
                state = "BLOCK_COMMENT"; index += 2; continue
            if char in ('"', "'"):
                quote = char; output[index] = " "; state = "LITERAL"; index += 1; continue
        elif state == "LINE_COMMENT":
            if char == "\n":
                state = "CODE"
            else:
                output[index] = " "
            index += 1; continue
        elif state == "BLOCK_COMMENT":
            if char == "*" and nxt == "/":
                output[index] = output[index + 1] = " "; state = "CODE"; index += 2; continue
            if char != "\n": output[index] = " "
            index += 1; continue
        elif state == "LITERAL":
            if char == "\\" and nxt:
                output[index] = " "; output[index + 1] = " "; index += 2; continue
            if char == quote:
                output[index] = " "; state = "CODE"
            elif char != "\n":
                output[index] = " "
            index += 1; continue
        index += 1
    return "".join(output)


def _raw_code_tokens(text: str, path: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if path.endswith(".py"):
        try:
            tokens = tokenize.generate_tokens(io.StringIO(text).readline)
            for token in tokens:
                if token.type != tokenize.NAME:
                    continue
                category = _identifier_class(token.string)
                if category:
                    rows.append({"path": path, "line": token.start[0], "column": token.start[1], "token": token.string, "token_class": category})
        except (tokenize.TokenError, IndentationError) as exc:
            raise v1.FrictionError("APP_SOURCE_PYTHON_TOKENIZE_INVALID") from exc
    else:
        code = _mask_c_comments_and_literals(text)
        for line_number, line in enumerate(code.splitlines(), 1):
            header_matches = list(re.finditer(r"<(?:cuda|optix)[^>]*>", line, flags=re.IGNORECASE))
            for match in header_matches:
                rows.append({"path": path, "line": line_number, "column": match.start(), "token": match.group(0), "token_class": "CUDA_OPTIX_HEADER"})
            # A header spelling is one lexical occurrence.  Mask it before
            # scanning identifiers so ``<optix_stubs.h>`` is not counted a
            # second time as the substring ``optix_stubs``.
            identifier_line = list(line)
            for header in header_matches:
                identifier_line[header.start():header.end()] = " " * (header.end() - header.start())
            for match in re.finditer(r"[A-Za-z_][A-Za-z0-9_]*", "".join(identifier_line)):
                category = _identifier_class(match.group(0))
                if category:
                    rows.append({"path": path, "line": line_number, "column": match.start(), "token": match.group(0), "token_class": category})
    rows.sort(key=lambda row: (row["path"].encode("utf-8"), row["line"], row["column"], row["token"].encode("utf-8")))
    return rows


def measure_lineage(source_root: Path, lineage: Mapping[str, Any]) -> dict[str, Any]:
    base = v1.measure_lineage(source_root, lineage)
    public: list[dict[str, Any]] = []
    private: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    raw_tokens: list[dict[str, Any]] = []
    for identity in lineage["app_owned_files"]:
        relative = v1._safe_relative(identity["path"])
        raw = source_root.joinpath(*PurePosixPath(relative).parts).read_bytes()
        text = raw.decode("utf-8", errors="strict").replace("\r\n", "\n").replace("\r", "\n")
        if relative.endswith(".py"):
            pub, priv, unr, exc = _resolve_calls(text, relative)
            public.extend(pub); private.extend(priv); unresolved.extend(unr); excluded.extend(exc)
        raw_tokens.extend(_raw_code_tokens(text, relative))
    pins = base["source_pins"]
    for key in ("public_api_calls", "private_api_calls", "unresolved_api_calls", "raw_cuda_optix_tokens"):
        base["metrics"].pop(key, None)
    for key in ("public_api_call_sites", "private_api_call_sites", "unresolved_api_call_sites", "raw_cuda_optix_token_sites"):
        base["details"].pop(key, None)
    base["schema"] = "rtdl.goal5793.x2.structural_friction_measurement.v2"
    base["successor_of"] = {
        "path": "scripts/goal5793_x2_structural_friction.py",
        "review_findings": ["P2_1_RAW_TOKEN_LEXER", "P2_2_CALL_CLASSIFICATION"],
        "reviewed_bytes_edited": False,
    }
    base["metrics"].update(
        {
            "public_rtdl_api_call_sites": v1._metric(len(public), "unique_static_rtdl_call_sites", pins),
            "private_rtdl_api_call_sites": v1._metric(len(private), "unique_static_rtdl_call_sites", pins),
            "unresolved_rtdl_api_call_sites": v1._metric(len(unresolved), "unique_static_rtdl_call_sites", pins),
            "non_rtdl_call_sites_excluded_from_api_metric": v1._metric(len(excluded), "unique_static_non_rtdl_call_sites", pins),
            "raw_cuda_optix_code_tokens": v1._metric(len(raw_tokens), "code_only_lexical_occurrences", pins),
        }
    )
    base["details"].update(
        {
            "public_rtdl_api_call_sites": public,
            "private_rtdl_api_call_sites": private,
            "unresolved_rtdl_api_call_sites": unresolved,
            "non_rtdl_call_sites_excluded_from_api_metric": excluded,
            "raw_cuda_optix_code_token_sites": raw_tokens,
        }
    )
    base["measurement_definition"] = {
        "raw_token_scope": "CODE_TOKENS_ONLY__COMMENTS_AND_STRING_LITERALS_EXCLUDED",
        "raw_token_prefix_families": ["CUDA_", "OPTIX_", "cuda*", "optix*", "Optix*", "cu[A-Z]*", "CU[A-Z]*", "<cuda*>", "<optix*>"],
        "unresolved_scope": "ONLY_RTDSL_OR_SCRIPTS_GOAL5793_NAMESPACES",
        "builtins_stdlib_and_other_third_party_calls_excluded_from_unresolved": True,
        "public_private_unresolved_metrics_comparable_to_direct_cuda_optix_baseline": False,
        "reason": "RTDL_CALL_CLASSIFICATION_HAS_NO_SYMMETRIC_PUBLIC_API_VOCABULARY_FOR_A_DIRECT_CUDA_OPTIX_LINEAGE",
    }
    base["interpretation"] = "STRUCTURAL_INTEGRATION_RESPONSIBILITY_AND_ABSTRACTION_LEAKAGE_ONLY__NOT_HUMAN_USABILITY_OR_PRODUCTIVITY__NOT_CROSS_LINEAGE_API_QUALITY"
    base["supports_easy_productive_simpler_less_code_or_better_than_cuda_claim"] = False
    base["measurement_sha256"] = ""
    base["measurement_sha256"] = seal_document(base, seal_field="measurement_sha256", domain=MEASUREMENT_DOMAIN, version=2)
    return base
