#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "docs" / "reports" / "goal807_segment_polygon_optix_mode_gate_local_2026-04-23.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _record_map(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(record["label"]): record for record in payload.get("records", [])}


def _all_required_ok(records: dict[str, dict[str, Any]]) -> bool:
    for label in ("cpu_python_reference", "optix_host_indexed", "optix_native"):
        if records.get(label, {}).get("status") != "ok":
            return False
    return True


def _all_required_parity(records: dict[str, dict[str, Any]]) -> bool:
    for label in ("optix_host_indexed", "optix_native"):
        if not records.get(label, {}).get("parity_vs_cpu_python_reference"):
            return False
    return True


def _recommended_status(payload: dict[str, Any], records: dict[str, dict[str, Any]]) -> str:
    if not _all_required_ok(records):
        return "needs_real_optix_artifact"
    if not _all_required_parity(records):
        return "blocked_by_gate_failure"
    if payload.get("include_postgis"):
        postgis = records.get("postgis", {})
        if postgis.get("status") != "ok":
            return "blocked_by_gate_failure"
        if not postgis.get("parity_vs_cpu_python_reference"):
            return "blocked_by_gate_failure"
    return "ready_for_review"


def build_packet(payload: dict[str, Any]) -> dict[str, Any]:
    records = _record_map(payload)
    status = _recommended_status(payload, records)
    return {
        "goal": "Goal864 segment/polygon gate review packet",
        "date": "2026-04-23",
        "source_goal": payload.get("goal"),
        "dataset": payload.get("dataset"),
        "include_postgis": payload.get("include_postgis"),
        "gate_status": payload.get("status"),
        "strict_pass": payload.get("strict_pass"),
        "recommended_status": status,
        "required_records_ok": _all_required_ok(records),
        "required_parity_ok": _all_required_parity(records),
        "postgis_required_for_promotion": bool(payload.get("include_postgis")),
        "strict_failures": list(payload.get("strict_failures", [])),
        "records": [
            {
                "label": record.get("label"),
                "status": record.get("status"),
                "sec": record.get("sec"),
                "optix_mode": record.get("optix_mode"),
                "parity_vs_cpu_python_reference": record.get("parity_vs_cpu_python_reference"),
                "row_digest": record.get("row_digest"),
                "error_type": record.get("error_type"),
                "error": record.get("error"),
                "postgis_query_sec": record.get("postgis_query_sec"),
            }
            for record in payload.get("records", [])
        ],
        "boundary": (
            "This packet interprets a Goal807 gate artifact only. It does not promote "
            "segment/polygon to an active RTX claim path and does not authorize a public speedup claim."
        ),
    }


def to_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Goal864 Segment/Polygon Gate Review Packet",
        "",
        f"- source goal: `{packet['source_goal']}`",
        f"- dataset: `{packet['dataset']}`",
        f"- include_postgis: `{packet['include_postgis']}`",
        f"- gate status: `{packet['gate_status']}`",
        f"- recommended status: `{packet['recommended_status']}`",
        f"- required records ok: `{packet['required_records_ok']}`",
        f"- required parity ok: `{packet['required_parity_ok']}`",
        "",
        "## Records",
        "",
        "| Label | Status | OptiX mode | Seconds | Parity vs CPU | Error |",
        "|---|---|---|---:|---:|---|",
    ]
    for record in packet["records"]:
        error = record.get("error_type") or record.get("error") or ""
        sec = record.get("sec")
        lines.append(
            f"| {record['label']} | {record['status']} | {record.get('optix_mode', '') or ''} | "
            f"{'' if not isinstance(sec, (int, float)) else f'{sec:.6f}'} | "
            f"{record.get('parity_vs_cpu_python_reference')} | {error} |"
        )
    lines.extend(["", "## Strict Failures", ""])
    if packet["strict_failures"]:
        for failure in packet["strict_failures"]:
            lines.append(f"- {failure}")
    else:
        lines.append("- none")
    lines.extend(["", "## Boundary", "", packet["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a review packet from a Goal807 segment/polygon gate artifact.")
    parser.add_argument("--input-json", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-json", type=Path, default=ROOT / "docs" / "reports" / "goal864_segment_polygon_gate_review_packet_2026-04-23.json")
    parser.add_argument("--output-md", type=Path, default=ROOT / "docs" / "reports" / "goal864_segment_polygon_gate_review_packet_2026-04-23.md")
    args = parser.parse_args(argv)

    payload = _load_json(args.input_json)
    packet = build_packet(payload)
    packet["source_path"] = str(args.input_json)
    args.output_json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(packet) + "\n", encoding="utf-8")
    print(json.dumps({"output_json": str(args.output_json), "output_md": str(args.output_md), "recommended_status": packet["recommended_status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
