from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.embeddability_strategy_intake.goal4549.v1"
OUT_JSON = Path("docs/reports/goal4549_v3_0_m150_embeddability_strategy_intake_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4549_v3_0_m150_embeddability_strategy_intake_2026-06-17.md")
DOC = Path("docs/learn/v3_0_embeddability_architecture_strategy.md")
ROOT_DRAFT = Path("rtdl_embeddability_architecture_strategy.md")
LEARN_README = Path("docs/learn/README.md")


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    doc_text = (root / DOC).read_text(encoding="utf-8")
    readme_text = (root / LEARN_README).read_text(encoding="utf-8")
    checks = {
        "root_draft_removed": not (root / ROOT_DRAFT).exists(),
        "doc_in_learn_tree": (root / DOC).exists(),
        "status_is_review_input": "not a frozen ABI contract" in doc_text,
        "boundary_blocks_claims": "does not by itself authorize" in doc_text
        and "performance claims" in doc_text,
        "zero_copy_primary_path_recorded": "DLPack" in doc_text
        and "__cuda_array_interface__" in doc_text,
        "callable_fusion_is_optional": "optional advanced track" in doc_text
        and "Numba-only" in doc_text,
        "stable_c_abi_directive_recorded": "Freeze a draft C ABI" in doc_text
        and "opaque handles" in doc_text,
        "learn_readme_links_doc": "v3_0_embeddability_architecture_strategy.md" in readme_text,
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4549 / V3 M150",
        "status": "embeddability_strategy_intake_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "document": DOC.as_posix(),
        "claim_boundary": {
            "stable_c_abi_implemented": False,
            "dlpack_implemented": False,
            "external_stream_context_implemented": False,
            "device_callable_fusion_implemented": False,
            "release_authorized": False,
            "performance_claim_authorized": False,
        },
        "conclusion": (
            "Goal4549 intakes the independent V3 embeddability strategy as a "
            "tracked learn-tree design input. The doc is useful because it "
            "prioritizes a stable C ABI and zero-copy framework interop before "
            "optional device-callable fusion, but it remains guidance rather "
            "than an implemented or released V3 contract."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4549 / V3 M150 Embeddability Strategy Intake",
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
            "- No stable C ABI, DLPack path, external stream/context path, or device-callable fusion is implemented by this intake.",
            "- No release or performance claim is authorized.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    packet = build_packet()
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
