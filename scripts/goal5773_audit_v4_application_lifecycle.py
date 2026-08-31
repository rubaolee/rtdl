#!/usr/bin/env python3
"""Read-only audit of the V4 paper-frontdoor compilation/preparation lifecycle.

The audit identifies work lexically nested inside each public
``run_v4_complete`` endpoint.  It deliberately reports calls and source lines,
not seconds or predicted savings, and does not import or execute an app route.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_FILES = (
    "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py",
    "Paper-reproduction-apps/raydb-paper/v4_whole_app.py",
    "Paper-reproduction-apps/librts-paper/v4_whole_app.py",
    "Paper-reproduction-apps/rtnn-paper/v4_whole_app.py",
    "Paper-reproduction-apps/rt-dbscan-paper/v4_whole_app.py",
    "Paper-reproduction-apps/x-hd-paper/v4_whole_app.py",
    "Paper-reproduction-apps/rayjoin-paper/v4_whole_app.py",
    "Paper-reproduction-apps/rt-barneshut-paper/v4_whole_app.py",
    "Paper-reproduction-apps/goal5753-held-out-particle-tracking/v4_whole_app.py",
)
CAPABILITY_PROBES = (
    ("callback_artifact_cache", "src/rtdsl/v4_callback_artifact_cache.py",
     ("materialize_callback_artifact", "load_callback_artifact"), True),
    ("formal_callback_partner", "src/rtdsl/v4_callback_partner_runtime.py",
     ("V4PreparedCallbackSession", "prepare_v4_partner_session"), True),
    ("multiround_spatial", "src/rtdsl/v4_multiround_spatial_optix_runtime.py",
     ("PreparedMultiRoundSpatialOwner", "prepare_multiround_spatial_callback"), True),
    ("standard_triangle", "src/rtdsl/v4_triangle_standard_library.py",
     ("compile_standard_triangle_program",), False),
    ("builtin_triangle", "src/rtdsl/v4_builtin_triangle_standard_library.py",
     ("compile_standard_builtin_triangle_program",), False),
    ("bounded_relation", "src/rtdsl/v4_bounded_relation_optix_runtime.py",
     ("run_bounded_relation_callback",), False),
    ("grouped_event_reduction", "src/rtdsl/v4_grouped_event_reduction.py",
     ("compile_grouped_event_reduction", "execute_grouped_event_reduction"), False),
    ("hierarchy_frontier", "src/rtdsl/v4_hierarchy_frontier.py",
     ("compile_hierarchy_frontier", "execute_hierarchy_frontier"), False),
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _call_name(call: ast.Call) -> str:
    value = call.func
    parts = []
    while isinstance(value, ast.Attribute):
        parts.append(value.attr)
        value = value.value
    if isinstance(value, ast.Name):
        parts.append(value.id)
    return ".".join(reversed(parts))


def _audit_file(relative: str) -> dict[str, object]:
    path = ROOT / relative
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=relative)
    functions = [node for node in tree.body
                 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                 and node.name == "run_v4_complete"]
    if len(functions) != 1:
        raise RuntimeError(f"{relative}: expected one run_v4_complete")
    function = functions[0]
    calls = sorted(
        ({"name": _call_name(node), "line": node.lineno}
         for node in ast.walk(function) if isinstance(node, ast.Call)),
        key=lambda row: (int(row["line"]), str(row["name"])),
    )
    compile_calls = [row for row in calls if any(
        token in str(row["name"]).lower()
        for token in ("compile", "generate_")
    )]
    input_calls = [row for row in calls
                   if "build_v4_input" in str(row["name"]).lower()]
    prepare_calls = [row for row in calls if "prepare" in str(row["name"]).lower()]
    execute_calls = [row for row in calls if any(
        token in str(row["name"]).lower()
        for token in ("execute", "run_")
    )]
    cache_calls = [row for row in calls if any(
        token in str(row["name"]).lower()
        for token in ("cache", "load_callback_artifact", "materialize_callback_artifact")
    )]
    return {
        "path": relative,
        "source_sha256": _sha(path),
        "run_v4_complete_start_line": function.lineno,
        "run_v4_complete_end_line": function.end_lineno,
        "compile_calls_inside_complete_endpoint": compile_calls,
        "input_construction_calls_inside_complete_endpoint": input_calls,
        "prepare_calls_inside_complete_endpoint": prepare_calls,
        "execute_calls_inside_complete_endpoint": execute_calls,
        "artifact_cache_calls_inside_complete_endpoint": cache_calls,
        "compile_inside_complete_endpoint": bool(compile_calls),
        "input_construction_inside_complete_endpoint": bool(input_calls),
        "artifact_cache_consumed_inside_complete_endpoint": bool(cache_calls),
    }


def _capability_inventory() -> list[dict[str, object]]:
    rows = []
    for family, relative, expected, prepared in CAPABILITY_PROBES:
        path = ROOT / relative
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        definitions = {
            node.name: node.lineno
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        }
        missing = [name for name in expected if name not in definitions]
        if missing:
            raise RuntimeError(f"{relative}: missing capability symbols {missing!r}")
        rows.append({
            "family": family,
            "path": relative,
            "source_sha256": _sha(path),
            "required_symbol_lines": {
                name: definitions[name] for name in expected
            },
            "explicit_prepared_owner_or_cache_found_in_bounded_v4_module_scan": prepared,
            "absence_is_bounded_source_inventory_not_global_impossibility": not prepared,
        })
    return rows


def audit() -> dict[str, object]:
    rows = [_audit_file(name) for name in APP_FILES]
    capabilities = _capability_inventory()
    result: dict[str, object] = {
        "schema": "rtdl.goal5773.v4_application_lifecycle_source_audit.v1",
        "audit_kind": "read_only_source_fact__not_timing_or_predicted_saving",
        "application_count": len(rows),
        "applications": rows,
        "bounded_generic_capability_inventory": capabilities,
        "families_with_explicit_prepared_owner_or_cache_in_bounded_scan": [
            row["family"] for row in capabilities
            if row["explicit_prepared_owner_or_cache_found_in_bounded_v4_module_scan"]
        ],
        "families_without_explicit_prepared_owner_in_bounded_scan": [
            row["family"] for row in capabilities
            if not row["explicit_prepared_owner_or_cache_found_in_bounded_v4_module_scan"]
        ],
        "all_complete_frontdoors_contain_compile": all(
            row["compile_inside_complete_endpoint"] for row in rows),
        "complete_frontdoors_consuming_artifact_cache_count": sum(
            bool(row["artifact_cache_consumed_inside_complete_endpoint"]) for row in rows),
        "claim_boundary": {
            "seconds_measured": False,
            "saving_predicted": False,
            "eliminability_proven": False,
            "product_source_changed": False,
            "goal5769_formal_source_or_result_changed": False,
            "successor_implementation_authorized_by_this_audit": False,
        },
    }
    body = json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False)
    result["audit_sha256"] = hashlib.sha256(body.encode()).hexdigest()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    value = audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")


if __name__ == "__main__":
    main()
