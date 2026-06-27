#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def _check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def _claim_flags_false(payload: dict[str, Any], keys: tuple[str, ...]) -> bool:
    return all(payload.get(key) is False for key in keys)


def build_payload(artifact_dir: Path) -> dict[str, Any]:
    artifact_dir = artifact_dir.resolve()
    failures: list[str] = []

    hardware_path = artifact_dir / "optix_hardware_gate.json"
    env_path = artifact_dir / "gpu_env_gate.json"
    graph_path = artifact_dir / "m5_local_graph_gate.json"
    query_exec_status_path = artifact_dir / "rayjoin_query_exec_status.txt"
    pip_summary_path = artifact_dir / "m5_pip_point_location_parity_filtered_100k" / "summary.json"
    overlay_path = artifact_dir / "m5_overlay_active_count_same_contract.json"

    for path in (hardware_path, env_path, graph_path, query_exec_status_path, pip_summary_path, overlay_path):
        _check(path.exists(), f"missing required artifact: {path.name}", failures)

    hardware = _read_json(hardware_path) if hardware_path.exists() else {}
    env_gate = _read_json(env_path) if env_path.exists() else {}
    graph_gate = _read_json(graph_path) if graph_path.exists() else {}
    query_exec_status = _read_text(query_exec_status_path) if query_exec_status_path.exists() else "missing-artifact"
    pip_summary = _read_json(pip_summary_path) if pip_summary_path.exists() else {}
    overlay = _read_json(overlay_path) if overlay_path.exists() else {}

    _check(hardware.get("status") == "pass", "OptiX/RT hardware gate did not pass", failures)
    _check(bool(hardware.get("checks", {}).get("rt_hardware_name_present")), "RT hardware name was not detected", failures)
    _check(env_gate.get("status") == "pass", "GPU Python environment gate did not pass", failures)
    _check(
        graph_gate.get("status") == "m5_local_topology_graphs_ready_pod_and_author_evidence_pending",
        "M5 local topology graph gate did not report the expected ready/pending status",
        failures,
    )
    _check(query_exec_status in {"present", "missing"}, "query_exec status was not recorded as present or missing", failures)

    protocol = pip_summary.get("protocol", {})
    parity_filter = pip_summary.get("parity_filter") or {}
    correctness = pip_summary.get("correctness_sample", {})
    rtdl = pip_summary.get("rtdl", {})
    optix = rtdl.get("optix", {})
    embree = rtdl.get("embree", {})
    comparison = pip_summary.get("comparison", {})
    _check(pip_summary.get("schema") == "rtdl.goal4373.rayjoin_cdb_point_location_compare.v1", "PIP schema mismatch", failures)
    _check(protocol.get("point_count") == 100000, "PIP point count is not 100000", failures)
    _check(protocol.get("parity_filter_requested") is True, "PIP backend-parity query filter was not requested", failures)
    _check(parity_filter.get("status") == "pass", "PIP backend-parity query filter did not pass", failures)
    _check(parity_filter.get("accepted_count") == 100000, "PIP backend-parity query filter did not accept 100000 points", failures)
    _check(protocol.get("optix_repeats") == protocol.get("embree_repeats"), "PIP OptiX/Embree repeat counts differ", failures)
    _check(protocol.get("optix_repeats") == 1000, "PIP repeat count is not 1000", failures)
    _check(protocol.get("row_materialization_in_timed_path") is False, "PIP timed path materializes rows", failures)
    _check(correctness.get("sample_count") == 100000, "PIP correctness sample is not 100000", failures)
    _check(correctness.get("mismatch_count_first_10_materialized") == 0, "PIP correctness sample has mismatches", failures)
    _check(optix.get("counts_stable") is True, "PIP OptiX counts are not stable", failures)
    _check(embree.get("counts_stable") is True, "PIP Embree counts are not stable", failures)
    _check(optix.get("positive_face_count") == embree.get("positive_face_count"), "PIP positive face counts differ", failures)
    _check(optix.get("native_traversal_median_sec") is not None, "PIP OptiX native traversal timing missing", failures)
    _check(embree.get("native_traversal_median_sec") is not None, "PIP Embree native traversal timing missing", failures)
    _check(
        comparison.get("rtdl_optix_speedup_vs_rtdl_embree") is not None,
        "PIP same-contract OptiX/Embree comparison missing",
        failures,
    )
    if query_exec_status == "missing":
        _check(pip_summary.get("rayjoin_rt") is None, "RayJoin author result exists despite missing query_exec status", failures)
    else:
        _check(pip_summary.get("rayjoin_rt") is not None, "RayJoin author result missing despite present query_exec status", failures)

    overlay_comparison = overlay.get("comparison", {})
    overlay_claim_boundary = overlay.get("claim_boundary", {})
    overlay_rows = overlay.get("rows", [])
    overlay_by_backend = {row.get("backend"): row for row in overlay_rows if isinstance(row, dict)}
    _check(overlay.get("status") == "ok", "overlay active-count status is not ok", failures)
    _check(overlay_comparison.get("same_output_contract") is True, "overlay output contract mismatch", failures)
    _check(overlay_comparison.get("active_counts_match") is True, "overlay active counts do not match", failures)
    _check(overlay_comparison.get("all_row_materialization_avoided") is True, "overlay materialized rows in timed path", failures)
    _check(set(overlay_by_backend) == {"embree", "optix"}, "overlay does not contain both Embree and OptiX rows", failures)
    for backend, row in overlay_by_backend.items():
        _check(row.get("native_traversal_median_sec") is not None, f"overlay {backend} native traversal timing missing", failures)
        _check(row.get("output_contract") == "overlay_active_pair_dependency_count", f"overlay {backend} contract mismatch", failures)
    _check(
        _claim_flags_false(
            overlay_claim_boundary,
            (
                "full_polygon_overlay_claim_authorized",
                "rayjoin_section57_full_reproduction_claim_authorized",
                "public_speedup_claim_authorized",
                "rt_core_speedup_claim_authorized",
                "true_zero_copy_claim_authorized",
            ),
        ),
        "overlay claim boundary flags are not all false",
        failures,
    )

    author_status = "complete" if query_exec_status == "present" else "blocked_query_exec_missing"
    evidence_status = "pass" if not failures else "fail"
    if evidence_status == "pass" and author_status != "complete":
        overall_status = "partial_internal_evidence_author_code_blocked"
        status_label = "internal-author-blocked"
    elif evidence_status == "pass":
        overall_status = "internal_evidence_with_author_code"
        status_label = "internal-author-complete"
    else:
        overall_status = "fail"
        status_label = "fail"

    return {
        "tool": "v3_phoenix_m5_topology_intake",
        "artifact_dir": str(artifact_dir),
        "status": evidence_status,
        "overall_status": overall_status,
        "status_label": status_label,
        "generic_capability": "point_location_topology_stream",
        "m5_author_code_comparison_status": author_status,
        "overlay_author_comparison_status": "not_applicable_internal_same_contract_only",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "phoenix_m7_qualified_release_rows": 0,
        "query_exec_status": query_exec_status,
        "failures": failures,
        "checks": {
            "optix_hardware_gate_passed": hardware.get("status") == "pass",
            "gpu_env_gate_passed": env_gate.get("status") == "pass",
            "m5_graph_gate_ready": graph_gate.get("status")
            == "m5_local_topology_graphs_ready_pod_and_author_evidence_pending",
            "pip_same_contract_ready": not any(
                failure.startswith("PIP") or "PIP " in failure for failure in failures
            ),
            "overlay_same_contract_ready": not any(
                failure.startswith("overlay") or "overlay " in failure for failure in failures
            ),
        },
        "headline": (
            "M5 author-code comparison: BLOCKED (query_exec missing). "
            "RTDL same-contract topology evidence is internal only."
            if author_status != "complete"
            else "M5 author-code comparison: present. Evidence remains internal until M7."
        ),
        "metrics": {
            "pip_point_count": protocol.get("point_count"),
            "pip_correctness_sample": correctness.get("sample_count"),
            "pip_positive_face_count": optix.get("positive_face_count"),
            "pip_parity_filter_rejected_count": parity_filter.get("rejected_count"),
            "pip_rtdl_optix_speedup_vs_rtdl_embree": comparison.get("rtdl_optix_speedup_vs_rtdl_embree"),
            "pip_rtdl_optix_native_traversal_speedup_vs_rtdl_embree": comparison.get(
                "rtdl_optix_native_traversal_speedup_vs_rtdl_embree"
            ),
            "pip_rayjoin_rt_speedup_vs_rtdl_optix_native_traversal": comparison.get(
                "rayjoin_rt_speedup_vs_rtdl_optix_native_traversal"
            ),
            "overlay_active_count": overlay_comparison.get("active_count"),
            "overlay_embree_over_optix_timed_median": overlay_comparison.get("embree_over_optix_timed_median"),
        },
        "comparison_methodology": pip_summary.get("comparison_methodology"),
    }


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    metrics = payload["metrics"]
    lines = [
        "# Phoenix V3 M5 Topology Intake",
        "",
        f"Status: {payload['overall_status']}",
        "",
        payload["headline"],
        "",
        "```text",
        "release_authorized: false",
        "public_speedup_claim_authorized: false",
        "Phoenix M7-qualified release rows: 0",
        "```",
        "",
        "## Key Metrics",
        "",
        f"- PIP point count: {metrics['pip_point_count']}",
        f"- PIP correctness sample: {metrics['pip_correctness_sample']}",
        f"- PIP positive face count: {metrics['pip_positive_face_count']}",
        f"- PIP parity-filter rejected count: {metrics['pip_parity_filter_rejected_count']}",
        f"- PIP RTDL OptiX / Embree same-contract ratio: {metrics['pip_rtdl_optix_speedup_vs_rtdl_embree']}",
        f"- PIP native traversal OptiX / Embree ratio: {metrics['pip_rtdl_optix_native_traversal_speedup_vs_rtdl_embree']}",
        f"- PIP RayJoin Query / RTDL OptiX native traversal ratio: {metrics['pip_rayjoin_rt_speedup_vs_rtdl_optix_native_traversal']}",
        f"- Overlay active count: {metrics['overlay_active_count']}",
        f"- Overlay Embree / OptiX timed median ratio: {metrics['overlay_embree_over_optix_timed_median']}",
        "",
        "## Failures",
        "",
    ]
    if payload["failures"]:
        lines.extend(f"- {failure}" for failure in payload["failures"])
    else:
        lines.append("- none")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Phoenix V3 M5 topology pod artifacts.")
    parser.add_argument("--artifact-dir", required=True, type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args.artifact_dir)
    text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    if args.md_out:
        write_markdown(args.md_out, payload)
    print(text)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
