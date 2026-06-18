from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


PACKET_VERSION = "rtdl.v3_0.embeddability_architecture_status_refresh.goal4590.v1"
OUT_JSON = Path("docs/reports/goal4590_v3_0_m191_embeddability_architecture_status_refresh_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4590_v3_0_m191_embeddability_architecture_status_refresh_2026-06-17.md")
ARCHITECTURE_DOC = Path("docs/learn/v3_0_embeddability_architecture_strategy.md")
SHIPPING_REFRESH = Path("docs/reports/goal4589_v3_0_m190_embeddability_shipping_readiness_refresh_2026-06-17.json")


def _current_progress_goal_number(doc: str) -> int | None:
    match = re.search(r"As of Goal(\d+)", doc)
    return int(match.group(1)) if match else None


def build_packet(root: Path = Path(".")) -> dict:
    doc = (root / ARCHITECTURE_DOC).read_text(encoding="utf-8")
    shipping = json.loads((root / SHIPPING_REFRESH).read_text(encoding="utf-8"))
    progress_goal = _current_progress_goal_number(doc)
    checks = {
        "architecture_doc_status_at_or_beyond_goal4589": progress_goal is not None
        and progress_goal >= 4589,
        "architecture_doc_names_stage_archive_target": "make package-c-api-stage" in doc
        and "rtdl-c-api-stage-0.1.3.tar.gz" in doc,
        "architecture_doc_names_prefix_stage_target": "make stage-c-api-prefix" in doc
        and "Prefix-layout `pkg-config` proof" in doc,
        "architecture_doc_names_python_ctypes_examples": "Python `ctypes` lifecycle" in doc
        and "Python `ctypes` host AABB2 query" in doc,
        "architecture_doc_names_prefix_python_ctypes_smoke": "Prefix-stage Python `ctypes` smoke" in doc,
        "architecture_doc_preserves_blocked_generated_binding_boundary": "generated language bindings" in doc
        and "minimal binding base" in doc,
        "architecture_doc_preserves_sdk_and_stable_abi_boundary": "packaged SDK wording" in doc
        and "frozen ABI compatibility" in doc,
        "shipping_refresh_stage_archive_validated": (
            shipping["status_matrix"]["source_tree_stage_archive"] == "validated_extract_compile_run"
        ),
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4590 / V3 M191",
        "status": "embeddability_architecture_status_refresh_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "claim_boundary": {
            "stable_abi_authorized": False,
            "packaged_sdk_authorized": False,
            "generated_language_binding_authorized": False,
            "device_buffer_c_abi_authorized": False,
            "optix_embree_c_abi_query_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4590 refreshes the main V3 embeddability architecture strategy "
            "so its current-progress section reflects the current Goal4597 state: C "
            "dlopen/direct-link, staged pkg-config, Python ctypes lifecycle/query "
            "examples, relocatable stage, source-tree stage archive, prefix-stage "
            "pkg-config, source-tree doctor prefix coverage, and prefix-stage "
            "Python ctypes smoke are validated, while stable ABI, packaged SDK, "
            "system install, generated bindings, device-buffer C ABI, OptiX/Embree "
            "C ABI execution, external CUDA stream, and release claims remain "
            "blocked."
        ),
    }


def write_report(packet: dict, path: Path) -> None:
    lines = [
        "# Goal4590 / V3 M191 Embeddability Architecture Status Refresh",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "| --- | --- |",
    ]
    for name, passed in packet["checks"].items():
        lines.append(f"| `{name}` | `{passed}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This refreshes architecture status wording only.",
            "- It does not authorize stable ABI, packaged SDK, generated bindings, device-buffer C ABI, OptiX/Embree C ABI execution, or release claims.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    packet = build_packet()
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
