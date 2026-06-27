#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "future" / "v4" / "evidence" / "v4_goal4759_final_review_evidence_manifest_2026-06-26.json"
DEFAULT_MD = ROOT / "future" / "v4" / "v4_goal4759_final_review_evidence_manifest_2026-06-26.md"


ARTIFACTS: tuple[tuple[str, str, str], ...] = (
    ("goal4757_release_packet", "release_review", "tools/_archive/future/v4/v4_goal4757_final_v4_0_release_packet_after_goal4756_2026-06-26.md"),
    ("goal4757_call_for_review", "release_review", "tools/_archive/future/v4/reviews/call_for_review_v4_goal4757_final_v4_0_release_after_goal4756_2026-06-26.md"),
    ("goal4757_forward_message", "release_review", "tools/_archive/future/v4/reviews/v4_goal4757_forward_message_to_external_reviewer_2026-06-26.txt"),
    ("goal4757_external_review_debt", "release_review", "tools/_archive/future/v4/reviews/v4_goal4757_final_release_external_review_debt_2026-06-26.md"),
    ("goal4758_completion_audit", "completion_audit", "tools/_archive/future/v4/v4_goal4758_local_completion_audit_2026-06-26.md"),
    ("goal4756_matrix_analysis_json", "pod_matrix", "tools/_archive/future/v4/evidence/v4_goal4756_final_rt_core_matrix_analysis_2026-06-26.json"),
    ("goal4756_matrix_analysis_md", "pod_matrix", "tools/_archive/future/v4/v4_goal4756_final_rt_core_matrix_analysis_2026-06-26.md"),
    ("goal4756_matrix_readout", "pod_matrix", "tools/_archive/future/v4/v4_goal4756_final_rt_core_matrix_release_readout_2026-06-26.md"),
    ("goal4758_full_v4_gate_log", "local_validation", "tools/_archive/future/v4/evidence/v4_goal4758_full_v4_unittest_discover_with_installed_wheel_script_gate_2026-06-26.log"),
    ("goal4759_full_v4_gate_log", "local_validation", "tools/_archive/future/v4/evidence/v4_goal4759_full_v4_unittest_discover_with_review_manifest_2026-06-26.log"),
    ("goal4758_wheel", "package", "tools/_archive/dist/goal4758_v4_release_candidate/rtdl_source_tree-4.0.0-py3-none-any.whl"),
    ("goal4758_wheel_build_log", "package", "tools/_archive/future/v4/evidence/v4_goal4758_package_wheel_build_2026-06-26.log"),
    ("goal4758_wheel_install_smoke_summary", "package", "tools/_archive/future/v4/evidence/v4_goal4758_wheel_install_smoke_2026-06-26/summary.json"),
    ("goal4769_barnes_hut_author_phase_report", "release_review_delta", "tools/_archive/future/v4/v4_goal4769_rt_barneshut_author_phase_accounting_2026-06-26.md"),
    ("goal4769_barnes_hut_author_phase_stdout", "release_review_delta", "tools/_archive/future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4769_author_phase_print_false_10m_stdout.txt"),
    ("goal4770_barnes_hut_delta_json", "release_review_delta", "tools/_archive/future/v4/evidence/v4_goal4770_rt_barneshut_release_packet_delta_2026-06-26.json"),
    ("goal4770_barnes_hut_delta_md", "release_review_delta", "tools/_archive/future/v4/v4_goal4770_rt_barneshut_release_packet_delta_2026-06-26.md"),
    ("goal4770_barnes_hut_delta_review_debt", "release_review_delta", "tools/_archive/future/v4/reviews/v4_goal4770_rt_barneshut_release_packet_delta_review_debt_2026-06-26.md"),
    ("readme", "public_docs", "README.md"),
    ("current_v4_status", "public_docs", "docs/current_v4_status.md"),
    ("app_level_benchmark_summary", "public_docs", "docs/app_level_benchmark_summary.md"),
    ("performance_wording", "public_docs", "docs/learn/performance_wording.md"),
    ("future_v4_readme", "public_docs", "tools/_archive/future/v4/README.md"),
    ("tier2_operator_catalog", "public_docs", "tools/_archive/future/v4/tier2_operator_catalog.md"),
    ("goal4757_machine_gate", "machine_gates", "src/rtdsl/v4_goal4757_final_release_packet.py"),
    ("goal4758_machine_gate", "machine_gates", "src/rtdsl/v4_goal4758_local_completion_audit.py"),
    ("goal4758_installed_wheel_smoke_script", "machine_gates", "scripts/v4_goal4758_installed_wheel_smoke.py"),
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_record(artifact_id: str, category: str, relpath: str) -> dict[str, Any]:
    path = ROOT / relpath
    if not path.exists():
        return {
            "id": artifact_id,
            "category": category,
            "path": relpath,
            "exists": False,
            "size_bytes": 0,
            "sha256": "",
        }
    return {
        "id": artifact_id,
        "category": category,
        "path": relpath,
        "exists": True,
        "size_bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def build_manifest() -> dict[str, Any]:
    artifacts = [_artifact_record(*item) for item in ARTIFACTS]
    matrix = json.loads((ROOT / "tools/_archive/future/v4/evidence/v4_goal4756_final_rt_core_matrix_analysis_2026-06-26.json").read_text(encoding="utf-8"))
    wheel_smoke = json.loads((ROOT / "tools/_archive/future/v4/evidence/v4_goal4758_wheel_install_smoke_2026-06-26/summary.json").read_text(encoding="utf-8"))

    missing = [artifact["id"] for artifact in artifacts if not artifact["exists"]]
    empty = [artifact["id"] for artifact in artifacts if artifact["exists"] and artifact["size_bytes"] <= 0]
    return {
        "schema": "rtdl.v4.goal4759.final_review_evidence_manifest.v1",
        "status": "ready_for_external_review_not_release_authorization" if not missing and not empty else "incomplete",
        "release_authorized": False,
        "public_tag_authorized": False,
        "external_review_debt_open": True,
        "artifact_count": len(artifacts),
        "missing_artifacts": missing,
        "empty_artifacts": empty,
        "artifacts": artifacts,
        "matrix_summary": matrix["summary"],
        "wheel_install_smoke": {
            "status": wheel_smoke["status"],
            "matrix_apps": wheel_smoke["matrix_apps"],
            "matrix_rows": wheel_smoke["matrix_rows"],
            "measured_partners": wheel_smoke["measured_partners"],
            "cupy_grouped_vector_sum_status": wheel_smoke["cupy_grouped_vector_sum_status"],
            "numba_component_union_status": wheel_smoke["numba_component_union_status"],
            "release_authorized": wheel_smoke["release_authorized"],
            "public_tag_authorized": wheel_smoke["public_tag_authorized"],
        },
        "supplemental_release_review_deltas": (
            "Goal4769 exposed the authors' full RT-BarnesHut phase table.",
            "Goal4770 updates Barnes-Hut release-packet interpretation without rewriting the historical Goal4756 matrix.",
        ),
        "forbidden_claims_still_forbidden": (
            "broad V4 speedup",
            "whole-application speedup",
            "all-benchmark speedup",
            "public true-zero-copy",
            "Tier-3 callback support",
            "raw OptiX callback support",
            "broad CuPy performance",
            "Barnes-Hut new V4-over-V3 speedup",
            "Spatial RayJoin speedup",
        ),
    }


def render_markdown(manifest: dict[str, Any]) -> str:
    lines = [
        "# V4 Goal4759 Final Review Evidence Manifest",
        "",
        f"Status: `{manifest['status']}`",
        "",
        "This manifest is the compact evidence index for external V4.0 release review.",
        "It records file sizes and sha256 hashes for the final packet, POD matrix,",
        "wheel/package evidence, local validation logs, public docs, and machine gates.",
        "",
        "## Summary",
        "",
        f"- artifact count: `{manifest['artifact_count']}`",
        f"- release authorized: `{manifest['release_authorized']}`",
        f"- public tag authorized: `{manifest['public_tag_authorized']}`",
        f"- external review debt open: `{manifest['external_review_debt_open']}`",
        f"- matrix apps: `{manifest['matrix_summary']['app_count']}`",
        f"- matrix has V2/V3/V4 rows: `{manifest['matrix_summary']['all_rows_have_v2_v3_v4']}`",
        f"- matrix regressions: `{manifest['matrix_summary']['regression_apps']}`",
        f"- wheel-install smoke: `{manifest['wheel_install_smoke']['status']}`",
        f"- supplemental release-review deltas: `{len(manifest['supplemental_release_review_deltas'])}`",
        "",
        "Supplemental deltas:",
        "",
        "- Goal4769 exposes the authors' full RT-BarnesHut phase table.",
        "- Goal4770 updates Barnes-Hut release-packet interpretation without",
        "  rewriting the historical Goal4756 matrix.",
        "",
        "## Artifacts",
        "",
        "| ID | Category | Size | SHA256 | Path |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for artifact in manifest["artifacts"]:
        lines.append(
            f"| `{artifact['id']}` | `{artifact['category']}` | `{artifact['size_bytes']}` | "
            f"`{artifact['sha256']}` | `{artifact['path']}` |"
        )
    lines.extend(
        [
            "",
            "## Non-Authorization",
            "",
            "This manifest is not a release verdict. It does not close the external",
            "review debt and does not authorize a public V4.0 tag.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Write the final V4 external-review evidence manifest.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    args = parser.parse_args()

    manifest = build_manifest()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(render_markdown(manifest), encoding="utf-8")
    print(args.json_out)
    print(args.md_out)
    print(manifest["status"])
    return 0 if manifest["status"] == "ready_for_external_review_not_release_authorization" else 1


if __name__ == "__main__":
    raise SystemExit(main())
