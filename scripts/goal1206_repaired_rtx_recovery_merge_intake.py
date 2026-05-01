#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from scripts.goal1205_repaired_rtx_pod_intake import build_intake, to_markdown


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-05-01"
DEFAULT_ORIGINAL_DIR = (
    ROOT
    / "docs/reports/goal1204_live_pod_2026-05-01/extracted/docs/reports/goal1204_repaired_rtx_pod"
)
DEFAULT_RECOVERY_DIR = (
    ROOT
    / "docs/reports/goal1204_embree4_usr_recovery_live_pod_2026-05-01/extracted/docs/reports/goal1204_embree4_usr_recovery"
)
DEFAULT_OUTPUT_JSON = ROOT / "docs/reports/goal1206_repaired_rtx_recovery_merge_intake_2026-05-01.json"
DEFAULT_OUTPUT_MD = ROOT / "docs/reports/goal1206_repaired_rtx_recovery_merge_intake_2026-05-01.md"


RECOVERY_MAP = {
    "db_embree_100000_chunked_repair_usr_recovery": "db_embree_100000_chunked_repair",
    "db_embree_300000_chunked_repair_usr_recovery": "db_embree_300000_chunked_repair",
    "road_hazard_embree_control_40000_usr_recovery": "road_hazard_embree_control_40000",
}


def _copy_recovery_file(recovery_dir: Path, merged_dir: Path, source_label: str, target_label: str, suffix: str) -> bool:
    source = recovery_dir / f"{source_label}{suffix}"
    if not source.exists():
        return False
    shutil.copy2(source, merged_dir / f"{target_label}{suffix}")
    return True


def build_merged_intake(original_dir: Path = DEFAULT_ORIGINAL_DIR, recovery_dir: Path = DEFAULT_RECOVERY_DIR) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        merged = Path(tmp) / "merged"
        shutil.copytree(original_dir, merged)
        copied: list[str] = []
        for source_label, target_label in RECOVERY_MAP.items():
            for suffix in (".json", ".status.json", ".log"):
                if _copy_recovery_file(recovery_dir, merged, source_label, target_label, suffix):
                    copied.append(f"{source_label}{suffix}->{target_label}{suffix}")
        payload = build_intake(merged)
    payload["goal"] = "Goal1206 repaired RTX recovery merge intake"
    payload["date"] = DATE
    payload["original_input_dir"] = str(original_dir)
    payload["recovery_input_dir"] = str(recovery_dir)
    payload["recovery_copied_files"] = copied
    payload["recovery_boundary"] = (
        "Goal1206 merges the original Goal1204 pod evidence with Embree4 /usr recovery controls. "
        "It is an evidence intake only and does not authorize public wording without review."
    )
    return payload


def to_merged_markdown(payload: dict) -> str:
    text = to_markdown(payload)
    lines = [
        text,
        "",
        "## Recovery Merge",
        "",
        payload["recovery_boundary"],
        "",
        f"- original input: `{payload['original_input_dir']}`",
        f"- recovery input: `{payload['recovery_input_dir']}`",
        f"- recovery copied files: `{len(payload['recovery_copied_files'])}`",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Merge Goal1204 original and Embree4 recovery artifacts, then intake.")
    parser.add_argument("--original-dir", type=Path, default=DEFAULT_ORIGINAL_DIR)
    parser.add_argument("--recovery-dir", type=Path, default=DEFAULT_RECOVERY_DIR)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args(argv)
    payload = build_merged_intake(args.original_dir, args.recovery_dir)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_merged_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "decisions": payload["decisions"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
