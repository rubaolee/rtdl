from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts import goal4591_m192_v3_c_abi_host_external_runtime_gate as goal4591
from scripts import goal4592_m193_v3_c_abi_cuda_buffer_metadata_gate as goal4592
from scripts import goal4593_m194_v3_python_ctypes_cuda_metadata_bridge as goal4593


PACKET_VERSION = "rtdl.v3_0.binding_device_interop_matrix.goal4605.v1"
OUT_JSON = Path("docs/reports/goal4605_v3_0_m206_binding_device_interop_matrix_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4605_v3_0_m206_binding_device_interop_matrix_2026-06-17.md")

MATRIX_DOC = Path("docs/learn/v3_0_binding_and_device_interop_matrix.md")
LEARN_README = Path("docs/learn/README.md")
SOURCE_TREE_DOCTOR_DOC = Path("docs/learn/source_tree_doctor.md")
SOURCE_TREE_DOCTOR = Path("scripts/rtdl_source_tree_doctor.py")
BENCHMARK_INDEX = Path("docs/learn/benchmark_evidence_index.md")
C_ABI_DRAFT = Path("docs/learn/v3_0_c_abi_draft.md")
ZERO_COPY_DOC = Path("docs/learn/v3_0_zero_copy_interop_contract.md")
EMBEDDING_README = Path("examples/current/embedding/README.md")
HEADER = Path("include/rtdl/rtdl.h")
PY_CUDA_EXAMPLE = Path("examples/current/embedding/python_ctypes_cuda_buffer_metadata_client.py")

REPORTS = {
    "host_external_runtime": Path("docs/reports/goal4591_v3_0_m192_c_abi_host_external_runtime_gate_2026-06-17.json"),
    "cuda_buffer_metadata": Path("docs/reports/goal4592_v3_0_m193_c_abi_cuda_buffer_metadata_gate_2026-06-17.json"),
    "python_cuda_metadata_bridge": Path("docs/reports/goal4593_v3_0_m194_python_ctypes_cuda_metadata_bridge_2026-06-17.json"),
    "metadata_readiness": Path("docs/reports/goal4594_v3_0_m195_embeddability_metadata_readiness_refresh_2026-06-17.json"),
    "delivery_archive_cmake": Path("docs/reports/goal4603_v3_0_m204_embeddability_delivery_archive_cmake_refresh_2026-06-17.json"),
    "toolchain_support": Path("docs/reports/goal4604_v3_0_m205_toolchain_support_matrix_2026-06-17.json"),
    "dlpack_like_metadata": Path(
        "docs/reports/goal4607_v3_0_m208_python_ctypes_dlpack_like_metadata_bridge_2026-06-17.json"
    ),
    "archive_python_ctypes": Path(
        "docs/reports/goal4608_v3_0_m209_archive_stage_python_ctypes_smoke_2026-06-17.json"
    ),
    "archive_c_examples": Path("docs/reports/goal4609_v3_0_m210_archive_stage_c_examples_smoke_2026-06-17.json"),
    "independent_context_concurrency": Path(
        "docs/reports/goal4610_v3_0_m211_c_abi_independent_context_concurrency_smoke_2026-06-17.json"
    ),
}


def _read(root: Path, path: Path) -> str:
    return (root / path).read_text(encoding="utf-8")


def _load_report(root: Path, path: Path) -> dict[str, Any]:
    return json.loads(_read(root, path))


def _report_accepts(packet: dict[str, Any]) -> bool:
    return tuple(packet.get("failed_checks", ())) == ()


def _run_live_smokes(root: Path) -> dict[str, Any]:
    host = goal4591.build_packet(root, run_compile=True)
    cuda = goal4592.build_packet(root, run_compile=True)
    py_cuda = goal4593.build_packet(root, run_smoke=True)
    return {
        "host_external_runtime": {
            "ok": _report_accepts(host),
            "status": host["status"],
            "failed_checks": host["failed_checks"],
        },
        "cuda_buffer_metadata": {
            "ok": _report_accepts(cuda),
            "status": cuda["status"],
            "failed_checks": cuda["failed_checks"],
        },
        "python_cuda_metadata_bridge": {
            "ok": _report_accepts(py_cuda),
            "status": py_cuda["status"],
            "failed_checks": py_cuda["failed_checks"],
            "stdout": (
                ((py_cuda.get("python_ctypes_cuda_metadata_smoke") or {}).get("run_result") or {}).get("stdout")
            ),
        },
    }


def build_packet(root: Path = Path("."), *, run_live_smoke: bool = False) -> dict[str, Any]:
    matrix_doc = _read(root, MATRIX_DOC)
    learn = _read(root, LEARN_README)
    doctor_doc = _read(root, SOURCE_TREE_DOCTOR_DOC)
    doctor = _read(root, SOURCE_TREE_DOCTOR)
    index = _read(root, BENCHMARK_INDEX)
    c_abi = _read(root, C_ABI_DRAFT)
    zero_copy = _read(root, ZERO_COPY_DOC)
    embedding = _read(root, EMBEDDING_README)
    header = _read(root, HEADER)
    py_cuda_example = _read(root, PY_CUDA_EXAMPLE)
    reports = {name: _load_report(root, path) for name, path in REPORTS.items()}
    live_smokes = _run_live_smokes(root) if run_live_smoke else None

    metadata_status = reports["metadata_readiness"]["status_matrix"]
    delivery_status = reports["delivery_archive_cmake"]["status_matrix"]
    py_cuda_status = reports["python_cuda_metadata_bridge"]["support_matrix"]
    cuda_status = reports["cuda_buffer_metadata"]["support_matrix"]
    dlpack_like_status = reports["dlpack_like_metadata"]["support_matrix"]

    checks = {
        "matrix_doc_exists": (root / MATRIX_DOC).exists(),
        "matrix_doc_lists_current_binding_surfaces": all(
            token in matrix_doc
            for token in (
                "C dynamic-load client",
                "C direct-link client",
                "C examples from archive stage",
                "Python `ctypes` host AABB2 query",
                "Python `ctypes` examples from archive stage",
                "Independent-context host-route concurrency",
                "CUDA buffer descriptor import/export",
                "`__cuda_array_interface__` to C ABI descriptor",
                "DLPack-like object to C ABI descriptor",
                "DLPack",
            )
        ),
        "matrix_doc_blocks_device_claims": all(
            token in matrix_doc
            for token in (
                "Device-buffer query route",
                "External CUDA stream ordering",
                "Generated language bindings",
                "Do not say DLPack support",
                "true zero-copy support",
            )
        ),
        "learn_readme_links_matrix": "V3.0 Binding And Device Interop Matrix" in learn,
        "doctor_doc_mentions_binding_matrix": "binding/device interop matrix" in doctor_doc,
        "doctor_script_requires_binding_matrix": "v3_0_binding_and_device_interop_matrix.md" in doctor
        and "V3.0 Binding And Device Interop Matrix" in doctor,
        "benchmark_index_links_goal4605": "Goal4605 binding/device interop matrix" in index,
        "c_abi_draft_keeps_cuda_descriptor_metadata_only": "CUDA buffer descriptors can be imported" in c_abi
        and "no current query route consumes device buffers" in c_abi,
        "zero_copy_doc_blocks_true_zero_copy": "public speedup and public true-zero-copy claims remain blocked"
        in zero_copy,
        "embedding_readme_blocks_device_execution": "does not validate CUDA pointer ownership" in embedding
        and "device" in embedding
        and "execution" in embedding,
        "header_keeps_external_cuda_runtime_unsupported": "CUDA/HIP/Metal/Vulkan" in header
        and "external stream semantics remain unsupported" in header,
        "python_cuda_example_rejects_host_query_route": "__cuda_array_interface__" in py_cuda_example
        and "query_route_rejected=invalid argument" in py_cuda_example,
        "all_source_reports_accept": all(_report_accepts(packet) for packet in reports.values()),
        "host_runtime_metadata_validated": metadata_status["host_external_runtime_metadata"] == "validated",
        "cuda_descriptor_validated_metadata_only": (
            metadata_status["cuda_buffer_descriptor_import_export"] == "validated_metadata_only"
            and cuda_status["cuda_buffer_descriptor_import_export"] == "validated_metadata_only"
        ),
        "python_cuda_metadata_bridge_validated": (
            metadata_status["python_ctypes_cuda_metadata_bridge"] == "validated"
            and py_cuda_status["cuda_array_interface_to_c_abi_descriptor"] == "validated_metadata_only"
        ),
        "python_dlpack_like_metadata_bridge_validated": (
            dlpack_like_status["dlpack_like_to_c_abi_descriptor"] == "validated_metadata_only"
            and dlpack_like_status["dlpack_like_descriptor_host_aabb2_query_route"]
            == "rejected_invalid_argument"
        ),
        "archive_python_ctypes_examples_validated": reports["archive_python_ctypes"][
            "archive_stage_python_smoke"
        ]["ok"]
        and reports["archive_python_ctypes"]["claim_boundary"]["archive_python_ctypes_stage_authorized"]
        is True,
        "archive_c_examples_validated": reports["archive_c_examples"]["archive_stage_c_examples_smoke"]["ok"]
        and reports["archive_c_examples"]["claim_boundary"]["archive_c_examples_stage_authorized"] is True,
        "independent_context_concurrency_validated": reports["independent_context_concurrency"][
            "concurrency_smoke"
        ]["ok"]
        and reports["independent_context_concurrency"]["claim_boundary"][
            "independent_context_host_route_concurrency_authorized"
        ]
        is True,
        "delivery_cmake_pkg_config_handoff_validated": (
            delivery_status["prefix_pkg_config"] == "validated"
            and delivery_status["prefix_cmake_find_package"] == "validated_imported_target"
            and delivery_status["archive_cmake_find_package"]
            == "validated_extracted_archive_imported_target"
        ),
        "device_and_stream_routes_blocked": (
            metadata_status["device_buffer_query_route"] == "blocked"
            and metadata_status["external_cuda_stream_ordering"] == "blocked"
            and delivery_status["dlpack_zero_copy"] == "blocked"
        ),
        "generated_bindings_blocked": delivery_status["generated_language_bindings"] == "blocked",
    }
    if live_smokes is not None:
        checks.update(
            {
                "live_host_external_runtime_smoke_ok": live_smokes["host_external_runtime"]["ok"],
                "live_cuda_buffer_metadata_smoke_ok": live_smokes["cuda_buffer_metadata"]["ok"],
                "live_python_cuda_metadata_bridge_smoke_ok": live_smokes["python_cuda_metadata_bridge"]["ok"],
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4605 / V3 M206",
        "status": "binding_device_interop_matrix_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "reports": {name: path.as_posix() for name, path in REPORTS.items()},
        "live_smokes": live_smokes,
        "status_matrix": {
            "c_source_tree_examples": "validated_dynamic_and_direct_link",
            "c_archive_examples": "validated_direct_link_dlopen_host_runtime_cuda_metadata",
            "pkg_config_stage": delivery_status["prefix_pkg_config"],
            "cmake_prefix_find_package": delivery_status["prefix_cmake_find_package"],
            "cmake_archive_find_package": delivery_status["archive_cmake_find_package"],
            "python_ctypes_lifecycle_and_host_aabb2": delivery_status["python_ctypes_prefix_examples"],
            "python_ctypes_archive_examples": "validated_lifecycle_host_aabb2_cuda_metadata_dlpack_like",
            "host_aabb2_c_abi_query": delivery_status["host_aabb2_c_abi_query"],
            "independent_context_host_route_concurrency": "validated_source_tree_smoke",
            "host_external_runtime_metadata": metadata_status["host_external_runtime_metadata"],
            "cuda_buffer_descriptor_import_export": metadata_status["cuda_buffer_descriptor_import_export"],
            "cuda_array_interface_to_c_abi_descriptor": py_cuda_status[
                "cuda_array_interface_to_c_abi_descriptor"
            ],
            "cuda_descriptor_host_aabb2_query_route": py_cuda_status[
                "cuda_descriptor_host_aabb2_query_route"
            ],
            "dlpack_like_to_c_abi_descriptor": dlpack_like_status["dlpack_like_to_c_abi_descriptor"],
            "dlpack_like_descriptor_host_aabb2_query_route": dlpack_like_status[
                "dlpack_like_descriptor_host_aabb2_query_route"
            ],
            "dlpack": "design_contract_only",
            "device_buffer_query_route": metadata_status["device_buffer_query_route"],
            "external_cuda_stream_ordering": metadata_status["external_cuda_stream_ordering"],
            "generated_language_bindings": metadata_status["generated_language_bindings"],
            "public_true_zero_copy_claim": metadata_status["public_true_zero_copy_claim"],
            "stable_abi": metadata_status["stable_abi"],
            "release": metadata_status["release"],
        },
        "claim_boundary": {
            "source_tree_c_handoff_authorized": True,
            "archive_c_examples_stage_authorized": True,
            "pkg_config_stage_handoff_authorized": True,
            "cmake_stage_handoff_authorized": True,
            "python_ctypes_examples_authorized": True,
            "archive_python_ctypes_stage_authorized": True,
            "host_aabb2_c_abi_query_authorized": True,
            "independent_context_host_route_concurrency_authorized": True,
            "cuda_metadata_descriptor_authorized": True,
            "cuda_array_interface_metadata_bridge_authorized": True,
            "dlpack_like_metadata_bridge_authorized": True,
            "device_buffer_query_route_authorized": False,
            "dlpack_zero_copy_authorized": False,
            "external_cuda_stream_authorized": False,
            "generated_language_binding_authorized": False,
            "stable_abi_authorized": False,
            "packaged_sdk_authorized": False,
            "release_authorized": False,
            "performance_wording_authorized": False,
            "public_true_zero_copy_claim_authorized": False,
        },
        "conclusion": (
            "Goal4605 consolidates the current V3 binding and device interop "
            "state. The source tree has executable C and Python ctypes examples, "
            "pkg-config and CMake staged handoffs, a host AABB2 C ABI query route, "
            "host-runtime metadata, and CUDA descriptor metadata including a "
            "`__cuda_array_interface__`-style Python bridge, DLPack-like metadata "
            "bridging, extracted archive Python ctypes smoke, and extracted archive "
            "C examples smoke, and independent-context host-route concurrency "
            "smoke. The device side is "
            "still deliberately fail-closed: no DLPack adapter, device-buffer "
            "query route, external CUDA stream ordering, generated binding, "
            "stable ABI, SDK, release, performance claim, or true-zero-copy claim "
            "is authorized by this matrix."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    smokes = packet["live_smokes"] or {}
    lines = [
        "# Goal4605 / V3 M206 Binding And Device Interop Matrix",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Current Matrix",
        "",
        "| Surface | Status |",
        "| --- | --- |",
    ]
    for name, status in packet["status_matrix"].items():
        lines.append(f"| `{name}` | `{status}` |")
    lines.extend(
        [
            "",
            "## Live Smokes",
            "",
            "| Smoke | OK |",
            "| --- | --- |",
        ]
    )
    for name, result in smokes.items():
        lines.append(f"| `{name}` | `{result.get('ok')}` |")
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for name, passed in packet["checks"].items():
        lines.append(f"| `{name}` | `{passed}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Current C/Python examples, staged pkg-config, and staged CMake handoffs are authorized as source-tree evidence.",
            "- CUDA descriptor import/export and `__cuda_array_interface__` descriptor bridging are metadata-only.",
            "- DLPack, device-buffer query routes, external CUDA stream ordering, generated bindings, stable ABI, packaged SDK, release, performance, and true-zero-copy wording remain blocked.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-live-smoke", action="store_true")
    args = parser.parse_args(argv)
    packet = build_packet(run_live_smoke=not args.no_live_smoke)
    if not args.no_write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        write_report(packet, OUT_REPORT)
    print(
        json.dumps(
            {
                "failed_checks": packet["failed_checks"],
                "status": "accept" if not packet["failed_checks"] else "reject",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not packet["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
