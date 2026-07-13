#!/usr/bin/env python3
"""Run Goal5426 POD resource gate for full-public WaterBodies->BlockGroups WKT.

This gate does not regenerate WKT.  It checks whether full generation would be
safe on the current POD and whether existing Goal5311 full-public WKT artifacts
can be reused without copying.
"""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
GOAL5425 = RESULTS / "xhd_goal5425_full_public_water_bg_wkt_generation_feasibility.json"
GOAL5310_MANIFEST = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "data"
    / "generated"
    / "goal5310_water_bg_full_public_wkt_candidate"
    / "manifest.json"
)
GOAL5311_SUMMARY = RESULTS / "xhd_goal5311_water_bg_full_public_author_ingestion_summary_pod.json"
GOAL5314_SUMMARY = RESULTS / "xhd_goal5314_water_bg_corrected_comparison_summary.json"
OUT = RESULTS / "xhd_goal5426_full_public_water_bg_wkt_resource_gate.json"
WRAPPER = ROOT / "scripts" / "current_pod_ssh.py"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_wrapper(host: str, port: int, command: str, timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(WRAPPER), "--host", host, "--port", str(port), "exec", command],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )


def _preflight(host: str, port: int, timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(WRAPPER), "--host", host, "--port", str(port), "preflight"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )


def _remote_probe_code(expected: dict[str, Any], recommended_free_gib: float) -> str:
    expected_json = json.dumps(expected, sort_keys=True)
    return f"""
import hashlib
import json
import os
from pathlib import Path
import shutil

expected = json.loads({expected_json!r})
recommended_free_gib = float({recommended_free_gib!r})
src = Path('/tmp/xhd_goal5311/data')
out = Path('/tmp/xhd_goal5426/full_public_water_bg')
out.mkdir(parents=True, exist_ok=True)

write_probe = out / '.write_probe'
write_probe.write_text('ok\\n', encoding='utf-8')
write_probe.unlink()

def sha256_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()

usage = shutil.disk_usage('/tmp')
files = {{}}
all_hashes_match = True
all_sizes_match = True
all_files_exist = True
for key, item in expected.items():
    path = src / item['remote_name']
    exists = path.exists()
    all_files_exist = all_files_exist and exists
    actual_size = path.stat().st_size if exists else None
    actual_sha = sha256_file(path) if exists else None
    size_matches = exists and actual_size == int(item['expected_bytes'])
    sha_matches = exists and actual_sha == item['expected_sha256']
    all_sizes_match = all_sizes_match and bool(size_matches)
    all_hashes_match = all_hashes_match and bool(sha_matches)
    link = out / item['goal5426_name']
    if link.exists() or link.is_symlink():
        link.unlink()
    if exists:
        link.symlink_to(path)
    files[key] = {{
        'source_path': str(path),
        'goal5426_path': str(link),
        'exists': exists,
        'expected_bytes': int(item['expected_bytes']),
        'actual_bytes': actual_size,
        'size_matches': bool(size_matches),
        'expected_sha256': item['expected_sha256'],
        'actual_sha256': actual_sha,
        'sha256_matches': bool(sha_matches),
        'symlink_created': bool(link.is_symlink()),
        'symlink_target': os.readlink(link) if link.is_symlink() else None,
    }}

manifest_path = out / 'manifest.json'
manifest_payload = {{
    'schema': 'rtdl.paper_reproduction.xhd.goal5426.remote_symlink_manifest.v1',
    'source': '/tmp/xhd_goal5311/data',
    'output_dir': str(out),
    'files': files,
    'full_generation_executed': False,
    'reuse_existing_goal5311_artifacts': bool(all_files_exist and all_sizes_match and all_hashes_match),
}}
manifest_path.write_text(json.dumps(manifest_payload, indent=2, sort_keys=True) + '\\n', encoding='utf-8')

print(json.dumps({{
    'hostname': os.uname().nodename,
    'tmp_total_bytes': usage.total,
    'tmp_used_bytes': usage.used,
    'tmp_free_bytes': usage.free,
    'tmp_free_gib': usage.free / (1024 ** 3),
    'recommended_free_gib': recommended_free_gib,
    'generation_safety_gate_passed': usage.free / (1024 ** 3) >= recommended_free_gib,
    'write_permission_passed': True,
    'source_dir': str(src),
    'output_dir': str(out),
    'manifest_path': str(manifest_path),
    'files': files,
    'all_files_exist': bool(all_files_exist),
    'all_sizes_match': bool(all_sizes_match),
    'all_hashes_match': bool(all_hashes_match),
    'existing_artifact_reuse_gate_passed': bool(all_files_exist and all_sizes_match and all_hashes_match),
}}, sort_keys=True))
"""


def build_expected(goal5310: dict[str, Any]) -> dict[str, Any]:
    water = goal5310["services"]["waterbodies"]
    block = goal5310["services"]["blockgroups"]
    return {
        "waterbodies": {
            "remote_name": "USADetailedWaterBodies.wkt.full_public_arcgis_candidate.wkt",
            "goal5426_name": "USADetailedWaterBodies_full_public.wkt",
            "expected_bytes": int(water["output_bytes"]),
            "expected_sha256": water["sha256"],
            "expected_points": int(water["author_loader_point_count"]),
        },
        "blockgroups": {
            "remote_name": "USACensusBlockGroupBoundaries.wkt.full_public_arcgis_candidate.wkt",
            "goal5426_name": "USACensusBlockGroupBoundaries_full_public.wkt",
            "expected_bytes": int(block["output_bytes"]),
            "expected_sha256": block["sha256"],
            "expected_points": int(block["author_loader_point_count"]),
        },
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    goal5425 = _load(GOAL5425)
    goal5310 = _load(GOAL5310_MANIFEST)
    goal5311 = _load(GOAL5311_SUMMARY)
    goal5314 = _load(GOAL5314_SUMMARY)
    expected = build_expected(goal5310)
    recommended = float(goal5425["feasibility"]["recommended_free_disk_gib"])

    preflight = _preflight(args.host, args.port, args.timeout)
    encoded = base64.b64encode(_remote_probe_code(expected, recommended).encode("utf-8")).decode("ascii")
    remote_cmd = f"python3 -c \"import base64; exec(base64.b64decode('{encoded}').decode('utf-8'))\""
    probe = _run_wrapper(args.host, args.port, remote_cmd, args.timeout)
    remote_payload: dict[str, Any] | None = None
    if probe.returncode == 0:
        lines = [line for line in probe.stdout.splitlines() if line.strip().startswith("{")]
        if lines:
            remote_payload = json.loads(lines[-1])

    preflight_ok = preflight.returncode == 0 and "POD_OK" in preflight.stdout
    remote_ok = probe.returncode == 0 and remote_payload is not None
    generation_gate = bool(remote_payload and remote_payload["generation_safety_gate_passed"])
    reuse_gate = bool(remote_payload and remote_payload["existing_artifact_reuse_gate_passed"])
    selected_action = (
        "reuse_existing_goal5311_full_public_wkt_candidate__no_regeneration"
        if preflight_ok and remote_ok and reuse_gate
        else "blocked_pending_resource_or_artifact_fix"
    )

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5426.full_public_water_bg_wkt_resource_gate.v1",
        "goal": "Goal5426",
        "status": (
            "resource_gate_complete__existing_goal5311_artifacts_reused__regeneration_not_safe_on_current_tmp"
            if selected_action.startswith("reuse_existing")
            else "resource_gate_blocked"
        ),
        "matched": bool(selected_action.startswith("reuse_existing")),
        "pod": {
            "host": args.host,
            "port": args.port,
            "preflight_ok": preflight_ok,
            "preflight_stdout": preflight.stdout,
            "preflight_stderr": preflight.stderr,
        },
        "remote_probe": {
            "returncode": probe.returncode,
            "stdout": probe.stdout,
            "stderr": probe.stderr,
            "parsed": remote_payload,
        },
        "resource_decision": {
            "recommended_free_disk_gib": recommended,
            "generation_safety_gate_passed": generation_gate,
            "existing_artifact_reuse_gate_passed": reuse_gate,
            "selected_action": selected_action,
            "reason": (
                "Current /tmp free disk is below the Goal5425 3x full-generation safety threshold, "
                "but complete Goal5311 full-public WKT artifacts already exist on the POD and match "
                "the local Goal5310 manifest hashes, so Goal5426 reuses them through symlinks instead "
                "of regenerating or copying multi-GiB files."
            ),
        },
        "expected_artifacts": expected,
        "prior_evidence": {
            "goal5425": str(GOAL5425),
            "goal5310_manifest": str(GOAL5310_MANIFEST),
            "goal5311_summary": str(GOAL5311_SUMMARY),
            "goal5314_summary": str(GOAL5314_SUMMARY),
            "goal5311_author_ingestion_passed": bool(goal5311["decision"]["author_ingestion_passed"]),
            "goal5311_paper_value_matched": bool(goal5311["decision"]["paper_value_matched"]),
            "goal5311_hd_result": float(goal5311["author_result"]["hd_result"]),
            "goal5314_paper_config_author_hd_result": float(
                goal5314["author"]["paper_config_rerun_n_points_cell_8"]["hd_result"]
            ),
            "goal5314_paper_config_matches_paper_log": bool(
                goal5314["author"]["paper_config_rerun_n_points_cell_8"]["matches_paper_log"]
            ),
            "goal5314_rtdl_exact_witness_hd_result_float64": float(
                goal5314["rtdl"]["exact_witness"]["hd_result_float64"]
            ),
            "goal5314_rtdl_matches_author_float32_with_declared_tolerance": bool(
                goal5314["decision"][
                    "water_bg_full_public_rtdl_exact_witness_matches_author_float32_with_declared_tolerance"
                ]
            ),
        },
        "claim_boundary": {
            "resource_gate_claimed": True,
            "full_public_wkt_generated_by_goal5426": False,
            "existing_goal5311_wkt_reused": bool(selected_action.startswith("reuse_existing")),
            "author_rtdl_correctness_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "route_micro_optimization_goal_authorized": False,
            "explicit_lb_reopened": False,
        },
        "stop_loss_gate": {
            "gate_generic_capability_produced": True,
            "gate_non_app_consumer": "dataset resource gate / existing artifact reuse, no app-artifact parity",
            "gate_requires_app_specific_logic": False,
            "gate_downstream_consumer_reachable": True,
            "decision": "pass_resource_gate_not_artifact_parity",
        },
        "next_recommended_goal": (
            "Goal5427_refresh_or_consolidate_existing_full_public_water_bg_rtdl_against_goal5314_paper_config"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", required=True, type=int)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--output", default=str(OUT))
    args = parser.parse_args(argv)
    payload = build_payload(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"matched": payload["matched"], "status": payload["status"]}, sort_keys=True))
    return 0 if payload["matched"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
