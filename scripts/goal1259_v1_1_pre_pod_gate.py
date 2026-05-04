#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-04"
GOAL = "Goal1259 v1.1 pre-pod local gate"
DEFAULT_OUTPUT_JSON = ROOT / "docs/reports/goal1259_v1_1_pre_pod_gate_2026-05-04.json"
DEFAULT_OUTPUT_MD = ROOT / "docs/reports/goal1259_v1_1_pre_pod_gate_2026-05-04.md"

TRIAGE = ROOT / "docs/reports/goal1256_v1_1_embree_optix_triage_2026-05-04.md"
PACKET_JSON = ROOT / "docs/reports/goal1257_v1_1_embree_optix_pod_packet_2026-05-04.json"
PACKET_MD = ROOT / "docs/reports/goal1257_v1_1_embree_optix_pod_packet_2026-05-04.md"
INTAKE_JSON = ROOT / "docs/reports/goal1258_v1_1_embree_optix_pod_intake_2026-05-04.json"
INTAKE_MD = ROOT / "docs/reports/goal1258_v1_1_embree_optix_pod_intake_2026-05-04.md"
PACKET_SCRIPT = ROOT / "scripts/goal1257_v1_1_embree_optix_pod_packet.py"
EXECUTOR = ROOT / "scripts/goal1257_v1_1_embree_optix_pod_executor.sh"
INTAKE_SCRIPT = ROOT / "scripts/goal1258_v1_1_embree_optix_pod_intake.py"
PACKET_TEST = ROOT / "tests/goal1257_v1_1_embree_optix_pod_packet_test.py"
INTAKE_TEST = ROOT / "tests/goal1258_v1_1_embree_optix_pod_intake_test.py"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_object_exists(rev: str) -> bool:
    completed = subprocess.run(
        ["git", "cat-file", "-e", f"{rev}^{{commit}}"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return completed.returncode == 0


def _check_file(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "bytes": path.stat().st_size if path.exists() else 0,
    }


def build_gate() -> dict[str, Any]:
    files = {
        "triage": _check_file(TRIAGE),
        "packet_json": _check_file(PACKET_JSON),
        "packet_md": _check_file(PACKET_MD),
        "intake_json": _check_file(INTAKE_JSON),
        "intake_md": _check_file(INTAKE_MD),
        "packet_script": _check_file(PACKET_SCRIPT),
        "executor": _check_file(EXECUTOR),
        "intake_script": _check_file(INTAKE_SCRIPT),
        "packet_test": _check_file(PACKET_TEST),
        "intake_test": _check_file(INTAKE_TEST),
    }
    blockers: list[str] = []
    for name, row in files.items():
        if not row["exists"]:
            blockers.append(f"missing_{name}")

    packet = _load(PACKET_JSON) if PACKET_JSON.exists() else {}
    intake = _load(INTAKE_JSON) if INTAKE_JSON.exists() else {}
    archive_path = Path(packet.get("archive", {}).get("archive_path", ""))
    archive_exists = archive_path.exists()
    archive_sha_ok = False
    if archive_exists:
        archive_sha_ok = _sha256(archive_path) == packet.get("archive", {}).get("archive_sha256")
    if not packet.get("valid"):
        blockers.append("packet_not_valid")
    if not archive_exists:
        blockers.append("archive_missing")
    if archive_exists and not archive_sha_ok:
        blockers.append("archive_sha_mismatch")
    source_commit = str(packet.get("source_commit", ""))
    if not source_commit or not _git_object_exists(source_commit):
        blockers.append("packet_source_commit_missing")

    expected_targets = [
        "database_analytics",
        "graph_analytics",
        "polygon_pair_overlap_area_rows",
        "polygon_set_jaccard",
    ]
    target_rows = packet.get("pod_batch", {}).get("target_rows")
    if target_rows != expected_targets:
        blockers.append("packet_target_rows_mismatch")
    if packet.get("pod_batch", {}).get("active_backends") != ["embree", "optix"]:
        blockers.append("active_backends_mismatch")
    if packet.get("pod_batch", {}).get("frozen_backends") != ["vulkan", "hiprt", "apple_rt"]:
        blockers.append("frozen_backends_mismatch")
    run_command = packet.get("commands", {}).get("run_on_pod", "")
    expected_sha = packet.get("archive", {}).get("archive_sha256", "")
    if expected_sha and f"EXPECTED_SHA256={expected_sha}" not in run_command:
        blockers.append("run_command_missing_archive_sha")

    intake_missing_count = len(intake.get("missing_artifacts", [])) if isinstance(intake.get("missing_artifacts"), list) else None
    if intake.get("public_wording_authorized") is not False:
        blockers.append("intake_public_wording_boundary_missing")
    if intake.get("valid") is not False or intake_missing_count != 17:
        blockers.append("intake_placeholder_not_waiting_for_pod")

    ready_for_pod = not blockers
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": ready_for_pod,
        "ready_for_pod": ready_for_pod,
        "blockers": blockers,
        "files": files,
        "packet": {
            "valid": packet.get("valid"),
            "source_commit": source_commit,
            "source_commit_exists": bool(source_commit and _git_object_exists(source_commit)),
            "archive_path": str(archive_path),
            "archive_exists": archive_exists,
            "archive_sha_ok": archive_sha_ok,
            "target_rows": target_rows,
            "active_backends": packet.get("pod_batch", {}).get("active_backends"),
            "frozen_backends": packet.get("pod_batch", {}).get("frozen_backends"),
        },
        "intake": {
            "valid": intake.get("valid"),
            "missing_artifact_count": intake_missing_count,
            "public_wording_authorized": intake.get("public_wording_authorized"),
        },
        "next_action": (
            "Start one RTX Linux pod and run Goal1257 packet commands."
            if ready_for_pod
            else "Fix local blockers before starting a pod."
        ),
        "boundary": (
            "Goal1259 is a local pre-pod gate. It does not run cloud, change public docs, "
            "authorize release, or authorize public RTX speedup wording."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1259 v1.1 Pre-Pod Local Gate",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{payload['valid']}`",
        f"Ready for pod: `{payload['ready_for_pod']}`",
        "",
        payload["boundary"],
        "",
        "## Blockers",
        "",
    ]
    if payload["blockers"]:
        lines.extend(f"- `{blocker}`" for blocker in payload["blockers"])
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Packet",
            "",
            f"- source commit: `{payload['packet']['source_commit']}`",
            f"- source commit exists: `{payload['packet']['source_commit_exists']}`",
            f"- archive sha ok: `{payload['packet']['archive_sha_ok']}`",
            f"- target rows: `{', '.join(payload['packet']['target_rows'] or [])}`",
            f"- active backends: `{', '.join(payload['packet']['active_backends'] or [])}`",
            f"- frozen backends: `{', '.join(payload['packet']['frozen_backends'] or [])}`",
            "",
            "## Intake Placeholder",
            "",
            f"- valid before pod: `{payload['intake']['valid']}`",
            f"- missing artifact count: `{payload['intake']['missing_artifact_count']}`",
            f"- public wording authorized: `{payload['intake']['public_wording_authorized']}`",
            "",
            "## Next Action",
            "",
            payload["next_action"],
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Goal1259 v1.1 local pre-pod gate.")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args(argv)
    payload = build_gate()
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"ready_for_pod": payload["ready_for_pod"], "blockers": payload["blockers"]}, sort_keys=True))
    return 0 if payload["ready_for_pod"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
