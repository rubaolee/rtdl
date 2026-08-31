#!/usr/bin/env python3
"""Rebuild Goal5792's programming-responsibility evidence from frozen source.

This audit deliberately measures structural integration obligations, not lines
of code, developer time, or productivity.  Its V2 sites are the actually
executed direct-arm branches in the frozen Goal5785 formal frontdoor; because
that file is an evaluation harness, the result may not be relabelled as an
application-author task study.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
from typing import Any


ARCHIVE_REL = (
    "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816/"
    "EXECUTION_SOURCE.tar.gz"
)
ARCHIVE_SHA256 = "75bd1ce4647de8a198110dbb9be12b3f9a04e8b7ca53946227ddbbc78ac3ba41"
LEDGER_REL = "history/internal_docs/goal5787_programming_responsibility_ledger_20260816.json"
LEDGER_SHA256 = "70cea137f9f21430f23c72145ac8684ce3a7be9d3af95bf2e3d0561c9504e245"
FRONTDOOR = "scripts/goal5776_real_scale_frontdoors.py"
FRONTDOOR_SHA256 = "9a25226ac7384e3494d7a5c6366a7e326406fdfe1af1a163561a66938ba504c7"
V1_RESULT_REL = "history/internal_docs/goal5792_source_backed_responsibility_audit_result_20260820.json"
V1_RESULT_SHA256 = "3193d9c735bb2255006ae0efe86127059a35bf7491e7cea9664e0058715e3265"
V2_RESULT_REL = "history/internal_docs/goal5792_source_backed_responsibility_audit_result_v2_20260820.json"
V2_RESULT_SHA256 = "4a4779a2e8f3f517528d84ea1373f0dabd7a48f31204826d29711b1b08673c65"


FORBIDDEN_V4_APP_BYTES = (
    b"optixModuleCreate",
    b"optixProgramGroupCreate",
    b"optixPipelineCreate",
    b"OptixShaderBindingTable",
    b"optixSbtRecordPackHeader",
    b"optixLaunch(",
    b"cudaMalloc(",
    b".version 7.",
    b".address_size 64",
    b"__raygen__",
    b"__closesthit__",
    b"__anyhit__",
)


APP_SPECS: dict[str, dict[str, Any]] = {
    "particle_tracking": {
        "v4_path": "Paper-reproduction-apps/goal5753-held-out-particle-tracking/v4_whole_app.py",
        "v2_function": "_run_particle",
        "v2_calls": (
            "optix_runtime.pack_triangles_3d_from_arrays",
            "optix_runtime.pack_rays_3d_from_arrays",
            "optix_runtime.prepare_optix_static_triangle_scene_3d",
            "optix_runtime._load_optix_library",
            "OptixTraversalAuditSession.open",
            "audit.finish",
        ),
        "v4_call": "app.prepare_v4",
    },
    "triangle_counting": {
        "v4_path": "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py",
        "v2_function": "_run_triangle",
        "v2_calls": (
            "optix_runtime._load_optix_library",
            "benchmark.run_rt_graph_segmented_optix_scalar_summary",
            "OptixTraversalAuditSession.open",
            "audit.finish",
        ),
        "v4_call": "v4_app.prepare_v4_segmented",
    },
    "raydb": {
        "v4_path": "Paper-reproduction-apps/raydb-paper/v4_whole_app.py",
        "v2_function": "_run_raydb",
        "v2_calls": (
            "runner.run_packet",
            "OptixTraversalAuditSession.open",
            "audit.finish",
        ),
        "v4_call": "app.run_v4_real_scale_packet",
    },
    "librts": {
        "v4_path": "Paper-reproduction-apps/librts-paper/v4_whole_app.py",
        "v2_function": "_run_librts",
        "v2_calls": (
            "rt.prepare_aabb_index_2d_columns",
            "_load_optix_library",
            "OptixTraversalAuditSession.open",
            "audit.finish",
        ),
        "v4_call": "app.prepare_v4_real_scale_count",
    },
    "x_hd": {
        "v4_path": "Paper-reproduction-apps/x-hd-paper/v4_whole_app.py",
        "v2_function": "_run_xhd",
        "v2_calls": (
            "prepare_certified_nearest_global_witness_3d_optix",
            "_load_optix_library",
            "OptixTraversalAuditSession.open",
            "audit.finish",
        ),
        "v4_call": "app.prepare_v4",
    },
    "rtnn": {
        "v4_path": "Paper-reproduction-apps/rtnn-paper/v4_whole_app.py",
        "v2_function": "_run_rtnn",
        "v2_calls": (
            "prepare_direct_optix_bounded_selection_3d",
            "_load_optix_library",
            "OptixTraversalAuditSession.open",
            "audit.finish",
        ),
        "v4_call": "app.prepare_v4",
    },
    "rt_dbscan": {
        "v4_path": "Paper-reproduction-apps/rt-dbscan-paper/v4_whole_app.py",
        "v2_function": "_run_rtdbscan",
        "v2_calls": (
            "rt.prepare_optix_numba_radius_graph_grouped_stream_continuation_3d",
            "rt.radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns",
            "optix_runtime._load_optix_library",
            "OptixTraversalAuditSession.open",
            "audit.finish",
        ),
        "v4_call": "app.prepare_v4",
    },
    "rayjoin": {
        "v4_path": "Paper-reproduction-apps/rayjoin-paper/v4_whole_app.py",
        "v2_function": "_run_rayjoin",
        "v2_calls": (
            "legacy.prepared_six_batch_args",
            "legacy.run_v2_prepared_six_batch",
            "OptixTraversalAuditSession.open",
            "audit.finish",
        ),
        "v4_call": "app.run_v4_real_scale_six_batch",
    },
    "rt_barneshut": {
        "v4_path": "Paper-reproduction-apps/rt-barneshut-paper/v4_whole_app.py",
        "v2_function": "_run_rt_barneshut",
        "v2_calls": (
            "prepare_aggregate_frontier_reduce_explicit_native_3d",
            "_load_optix_library",
            "OptixTraversalAuditSession.open",
            "audit.finish",
        ),
        "v4_call": "app.prepare_v4",
    },
}


LEDGER_OBLIGATION_DISPOSITIONS = {
    "hand-written PTX/CUDA callback ABI plumbing": {
        "classification": "NOT_ESTABLISHED_AS_APPLICATION_OWNED_BY_FROZEN_V2_FRONTDOOR",
        "reason": "The executed V2 frontdoor calls shared physical APIs and contains no embedded PTX/CUDA callback ABI or raw device entrypoint.",
    },
    "manual OptiX module, program-group, pipeline and SBT assembly": {
        "classification": "NOT_ESTABLISHED_AS_APPLICATION_OWNED_BY_FROZEN_V2_FRONTDOOR",
        "reason": "The executed V2 frontdoor contains no module/program-group/pipeline/SBT construction symbol; that work was already below its direct API.",
    },
    "manual payload/register layout coordination": {
        "classification": "NOT_ESTABLISHED_AS_APPLICATION_OWNED_BY_FROZEN_V2_FRONTDOOR",
        "reason": "The executed V2 frontdoor contains no payload-register declaration or coordination surface.",
    },
    "manual launch-status buffer and error-envelope plumbing": {
        "classification": "NOT_ESTABLISHED_AS_APPLICATION_OWNED_BY_FROZEN_V2_FRONTDOOR",
        "reason": "The executed V2 frontdoor does not allocate or interpret callback status records; status handling was already inside shared physical owners.",
    },
    "manual program/traversable provenance receipt integration": {
        "classification": "PARTIALLY_SOURCE_BACKED__RECEIPT_CONSTRUCTION_MOVED_BEHIND_V4_RUNTIME",
        "reason": "All nine V2 branches explicitly open and finish OptixTraversalAuditSession; V4 runtimes construct the receipt, while the formal frontdoor still consumes and binds it.",
    },
    "manual cache/native/source identity binding": {
        "classification": "PARTIALLY_SOURCE_BACKED__IDENTITY_FIELDS_EMITTED_BY_V4_RUNTIME",
        "reason": "V4 runtime/owner receipts emit native and source identities, but the formal frontdoor still supplies target/native/input authority and therefore does not prove complete removal from the application integration boundary.",
    },
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_sha(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return _sha(encoded)


def _member_bytes(archive: tarfile.TarFile, name: str) -> bytes:
    pure = PurePosixPath(name)
    if pure.is_absolute() or ".." in pure.parts or pure.as_posix() != name:
        raise RuntimeError(f"unsafe requested member name: {name}")
    matches = [member for member in archive.getmembers() if member.name == name]
    if len(matches) != 1 or not matches[0].isfile():
        raise RuntimeError(f"missing unique regular source member: {name}")
    handle = archive.extractfile(matches[0])
    if handle is None:
        raise RuntimeError(f"unreadable source member: {name}")
    return handle.read()


def _dotted_name(node: ast.AST) -> str | None:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


def _calls(function: ast.FunctionDef) -> tuple[str, ...]:
    values = {
        name
        for node in ast.walk(function)
        if isinstance(node, ast.Call)
        for name in [_dotted_name(node.func)]
        if name is not None
    }
    return tuple(sorted(values))


def _imports(module: ast.Module) -> tuple[str, ...]:
    values: set[str] = set()
    for node in ast.walk(module):
        if isinstance(node, ast.ImportFrom) and node.module:
            values.add(node.module)
        elif isinstance(node, ast.Import):
            values.update(alias.name for alias in node.names)
    return tuple(sorted(value for value in values if value == "rtdsl" or value.startswith("rtdsl.")))


def _source_module_path(import_name: str) -> str:
    if import_name == "rtdsl":
        return "src/rtdsl/__init__.py"
    return "src/" + import_name.replace(".", "/") + ".py"


def _classify_imports(imports: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    generated_markers = (
        "callback_abi", "callback_ir", "optix_compiler", "standard_library",
        "lowering", "v4_hierarchy_frontier",
    )
    runtime_markers = ("optix_runtime", "prepared_runtime", "device_runtime")
    return {
        "generation_or_lowering": tuple(sorted(
            item for item in imports if any(marker in item for marker in generated_markers)
        )),
        "runtime_or_composition": tuple(sorted(
            item for item in imports if any(marker in item for marker in runtime_markers)
            or item == "rtdsl"
        )),
    }


def build_result(root: Path) -> dict[str, Any]:
    root = root.resolve()
    archive_path = root / ARCHIVE_REL
    ledger_path = root / LEDGER_REL
    v1_result_path = root / V1_RESULT_REL
    v2_result_path = root / V2_RESULT_REL
    archive_bytes = archive_path.read_bytes()
    ledger_bytes = ledger_path.read_bytes()
    v1_result_bytes = v1_result_path.read_bytes()
    v2_result_bytes = v2_result_path.read_bytes()
    if _sha(archive_bytes) != ARCHIVE_SHA256:
        raise RuntimeError("frozen Goal5785 execution-source SHA mismatch")
    if _sha(ledger_bytes) != LEDGER_SHA256:
        raise RuntimeError("frozen Goal5787 responsibility-ledger SHA mismatch")
    if _sha(v1_result_bytes) != V1_RESULT_SHA256:
        raise RuntimeError("Goal5792 responsibility-audit v1 predecessor SHA mismatch")
    if _sha(v2_result_bytes) != V2_RESULT_SHA256:
        raise RuntimeError("Goal5792 responsibility-audit v2 predecessor SHA mismatch")
    ledger = json.loads(ledger_bytes)
    ledger_apps = {row["app"]: row for row in ledger["applications"]}
    if set(ledger_apps) != set(APP_SPECS):
        raise RuntimeError("responsibility ledger application set drifted")
    if set(ledger["manual_optix_obligations_removed_from_application_programmer"]) != set(LEDGER_OBLIGATION_DISPOSITIONS):
        raise RuntimeError("legacy removed-obligation set drifted")

    rows: list[dict[str, Any]] = []
    with tarfile.open(archive_path, "r:gz") as archive:
        frontdoor_bytes = _member_bytes(archive, FRONTDOOR)
        if _sha(frontdoor_bytes) != FRONTDOOR_SHA256:
            raise RuntimeError("frozen Goal5776 frontdoor SHA mismatch")
        frontdoor_low_level_hits = [
            token.decode("ascii") for token in FORBIDDEN_V4_APP_BYTES
            if token in frontdoor_bytes
        ]
        if frontdoor_low_level_hits:
            raise RuntimeError(f"frontdoor low-level assembly vocabulary drifted: {frontdoor_low_level_hits}")
        frontdoor_ast = ast.parse(frontdoor_bytes, filename=FRONTDOOR)
        functions = {
            node.name: node
            for node in frontdoor_ast.body
            if isinstance(node, ast.FunctionDef)
        }

        for app_name, spec in APP_SPECS.items():
            function = functions.get(spec["v2_function"])
            if function is None:
                raise RuntimeError(f"missing V2/V4 frontdoor function: {spec['v2_function']}")
            calls = _calls(function)
            missing_calls = sorted(set(spec["v2_calls"]) - set(calls))
            if missing_calls or spec["v4_call"] not in calls:
                raise RuntimeError(
                    f"{app_name} frontdoor obligations drifted: "
                    f"missing={missing_calls}, v4={spec['v4_call'] in calls}"
                )

            v4_bytes = _member_bytes(archive, spec["v4_path"])
            forbidden_hits = [
                token.decode("ascii") for token in FORBIDDEN_V4_APP_BYTES
                if token in v4_bytes
            ]
            if forbidden_hits:
                raise RuntimeError(
                    f"{app_name} V4 application contains manual low-level API bytes: {forbidden_hits}"
                )
            v4_ast = ast.parse(v4_bytes, filename=spec["v4_path"])
            imports = _imports(v4_ast)
            shared_paths: list[dict[str, Any]] = []
            for import_name in imports:
                member_path = _source_module_path(import_name)
                member = _member_bytes(archive, member_path)
                shared_paths.append({
                    "import": import_name,
                    "path": member_path,
                    "sha256": _sha(member),
                    "bytes": len(member),
                })
            import_classes = _classify_imports(imports)
            ledger_row = ledger_apps[app_name]
            rows.append({
                "app": app_name,
                "paper_algorithm": ledger_row["paper_algorithm"],
                "v2_executed_direct_site": {
                    "path": FRONTDOOR,
                    "file_sha256": FRONTDOOR_SHA256,
                    "function": spec["v2_function"],
                    "start_line": function.lineno,
                    "end_line": function.end_lineno,
                    "required_direct_obligation_calls": list(spec["v2_calls"]),
                    "required_calls_present": True,
                    "site_is_evaluation_harness": True,
                    "site_is_application_developer_task_measurement": False,
                },
                "v4_application_site": {
                    "path": spec["v4_path"],
                    "sha256": _sha(v4_bytes),
                    "bytes": len(v4_bytes),
                    "frontdoor_call": spec["v4_call"],
                    "manual_low_level_optix_cuda_ptx_api_hits": [],
                    "rtdsl_imports": list(imports),
                    "private_optix_runtime_import_present": "rtdsl.optix_runtime" in imports,
                },
                "v4_shared_system_sites": shared_paths,
                "generated_or_lowered_stages": list(import_classes["generation_or_lowering"]),
                "runtime_or_composed_stages": list(import_classes["runtime_or_composition"]),
                "application_owned_responsibilities": ledger_row["application_owned"],
                "system_owned_responsibilities": ledger_row["system_owned"],
                "v4_composition": ledger_row["v4_composition"],
                "trusted_partner_boundary": ledger_row["legacy_partner_caveat"],
                "classification": "SOURCE_BACKED_STRUCTURAL_INTEGRATION_RESPONSIBILITY_SHIFT",
                "native_runtime_loading_behind_registered_v4_interface": app_name != "raydb",
                "native_runtime_loading_exception": (
                    None if app_name != "raydb" else
                    "RayDB directly imports and calls the private _load_optix_library helper."
                ),
                "developer_productivity_or_task_time_evidence": False,
            })

    result: dict[str, Any] = {
        "schema": "rtdl.goal5792.source_backed_responsibility_audit.v3",
        "goal": 5792,
        "status": "PASS__NINE_APP_SOURCE_BACKED_STRUCTURAL_AUDIT__LEGACY_LEDGER_CLAIMS_NARROWED",
        "inputs": {
            "goal5785_execution_source": {
                "path": ARCHIVE_REL,
                "sha256": ARCHIVE_SHA256,
                "bytes": len(archive_bytes),
            },
            "goal5787_hand_authored_ledger": {
                "path": LEDGER_REL,
                "sha256": LEDGER_SHA256,
                "bytes": len(ledger_bytes),
                "treated_as_claim_inventory_not_empirical_result": True,
            },
            "executed_v2_v4_frontdoor": {
                "path": FRONTDOOR,
                "sha256": FRONTDOOR_SHA256,
                "bytes": len(frontdoor_bytes),
                "manual_low_level_optix_cuda_ptx_api_hits": [],
            },
            "v1_predecessor": {
                "path": V1_RESULT_REL,
                "sha256": V1_RESULT_SHA256,
                "bytes": len(v1_result_bytes),
                "superseded_for_final_goal5792_use": True,
                "reason": "v1 source-backed the nine structural rows but did not disposition every global removed-obligation claim from the legacy ledger.",
            },
            "v2_predecessor": {
                "path": V2_RESULT_REL,
                "sha256": V2_RESULT_SHA256,
                "bytes": len(v2_result_bytes),
                "superseded_for_final_goal5792_use": True,
                "reason": "v2 recorded the RayDB private-loader exception but its blanket supported wording still claimed native runtime loading moved behind registered interfaces for all nine applications.",
            },
        },
        "summary": {
            "application_count": len(rows),
            "v2_direct_executed_site_count": len(rows),
            "v4_application_site_count": len(rows),
            "v4_application_manual_low_level_api_hit_count": 0,
            "v2_sites_are_evaluation_harness_count": len(rows),
            "application_developer_task_measurement_count": 0,
            "developer_time_measurement_count": 0,
            "raw_loc_primary_metric_used": False,
            "productivity_multiplier_claimed": False,
            "structural_responsibility_shift_supported": True,
            "application_productivity_improvement_supported": False,
            "raydb_private_optix_runtime_import_present": True,
            "native_runtime_loading_behind_registered_v4_interface_count": 8,
            "native_runtime_loading_exception_count": 1,
            "native_runtime_loading_exception_applications": ["raydb"],
            "legacy_removed_obligation_count": len(LEDGER_OBLIGATION_DISPOSITIONS),
            "legacy_removed_obligation_fully_source_backed_count": 0,
            "legacy_removed_obligation_partially_source_backed_count": 2,
            "legacy_removed_obligation_not_established_count": 4,
        },
        "legacy_removed_obligation_dispositions": [
            {
                "obligation": obligation,
                **LEDGER_OBLIGATION_DISPOSITIONS[obligation],
            }
            for obligation in ledger["manual_optix_obligations_removed_from_application_programmer"]
        ],
        "rows": rows,
        "claim_boundary": {
            "supported": (
                "Across all nine frozen Goal5785 V2/V4 frontdoors, V4 establishes a "
                "source-backed structural integration-responsibility shift in physical-owner "
                "preparation and traversal-receipt construction. Native runtime loading is "
                "behind registered V4 interfaces for eight of nine applications; RayDB remains "
                "the explicit private-loader exception."
            ),
            "legacy_ledger_successor_wording": (
                "The frozen comparison supports a nine-application structural shift in direct "
                "physical-owner and receipt-construction integration, and an eight-of-nine "
                "runtime-load encapsulation result. It does not establish that V2 application "
                "authors manually assembled PTX, OptiX pipelines/SBTs, payload registers, or status buffers."
            ),
            "not_supported": [
                "developer hours saved",
                "numeric productivity multiplier",
                "raw LOC reduction as a primary result",
                "all application code is generated",
                "all trusted native physical partners are eliminated",
                "the evaluation harness is an application-developer task study",
                "the functional RC is the Goal5785 performance source",
            ],
            "particle_caveat_corrected": (
                "V4 does not invent the paper algorithm or hardware traversal primitive; "
                "built-in triangle traversal is a trusted physical partner, while V4 "
                "generates and composes the restricted callback and execution bindings."
            ),
            "raydb_hygiene_observation": (
                "The V4 RayDB application still imports the private OptiX library loader; "
                "this is a source-backed interface-hygiene exception, not manual pipeline/SBT assembly."
            ),
        },
        "authorization": {
            "authorizes_gpu_or_pod": False,
            "authorizes_registered_timing": False,
            "authorizes_product_or_native_changes": False,
            "authorizes_publication_or_submission": False,
        },
    }
    result["result_sha256"] = _canonical_sha(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = build_result(Path(args.root))
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
