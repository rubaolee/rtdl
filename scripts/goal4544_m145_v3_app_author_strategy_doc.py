from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.app_author_strategy_doc.goal4544.v1"
OUT_JSON = Path("docs/reports/goal4544_v3_0_m145_app_author_strategy_doc_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4544_v3_0_m145_app_author_strategy_doc_2026-06-17.md")
DOC = Path("docs/learn/v3_0_app_author_implementation_strategy.md")
LEARN_INDEX = Path("docs/learn/README.md")
EVIDENCE_INDEX = Path("docs/learn/benchmark_evidence_index.md")
PARTNER_BOUNDARIES = Path("docs/partner_acceleration_boundaries.md")
V2_14_HISTORY = Path("docs/history/learn/v2_14_app_author_implementation_strategy.md")

REQUIRED_APP_LABELS = (
    "Hausdorff / X-HD",
    "Spatial RayJoin",
    "RT-DBSCAN",
    "Robot collision",
    "Contact manifold",
    "RayDB-style",
    "Barnes-Hut",
    "LibRTS spatial index",
    "RTNN",
    "Triangle counting",
)

REQUIRED_PHRASES = (
    "all ten benchmark apps are closed current targets",
    "no current target requires immediate pod execution",
    "Start with the smallest app-agnostic primitive",
    "keep partner continuation explicit",
    "Do not expose arbitrary raw callbacks as the stable user API",
    "RT-native hierarchical traversal is not implemented",
    "same data and timing protocol",
    "RTDL does not promise miracles",
)

FORBIDDEN_PHRASES = (
    "release authorized",
    "public speedup authorized",
    "automatic optimizer promise",
    "raw OptiX callbacks are a stable user API",
    "RT-native Barnes-Hut traversal is implemented",
    "all apps are broad RT-core wins",
)


def _read(root: Path, path: Path) -> str:
    return (root / path).read_text(encoding="utf-8")


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    doc = _read(root, DOC)
    learn_index = _read(root, LEARN_INDEX)
    evidence_index = _read(root, EVIDENCE_INDEX)
    partner_boundaries = _read(root, PARTNER_BOUNDARIES)
    missing_apps = tuple(label for label in REQUIRED_APP_LABELS if label not in doc)
    missing_phrases = tuple(phrase for phrase in REQUIRED_PHRASES if phrase not in doc)
    forbidden_hits = tuple(phrase for phrase in FORBIDDEN_PHRASES if phrase in doc)
    checks = {
        "doc_exists": (root / DOC).is_file(),
        "learn_index_links_doc": "v3_0_app_author_implementation_strategy.md" in learn_index,
        "evidence_index_links_doc": "v3_0_app_author_implementation_strategy.md" in evidence_index,
        "partner_boundaries_links_doc": "v3_0_app_author_implementation_strategy.md"
        in partner_boundaries,
        "all_ten_app_labels_present": not missing_apps,
        "required_boundary_phrases_present": not missing_phrases,
        "forbidden_phrases_absent": not forbidden_hits,
        "mentions_goal4614_and_goal4543": "Goal4614" in doc and "Goal4543" in doc,
        "v2_14_snapshot_archived_not_in_learn": "v2_14_app_author_implementation_strategy.md"
        not in learn_index
        and (root / V2_14_HISTORY).is_file(),
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4544 / V3 M145",
        "status": "v3_app_author_strategy_doc_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "doc": DOC.as_posix(),
        "missing_app_labels": missing_apps,
        "missing_required_phrases": missing_phrases,
        "forbidden_phrase_hits": forbidden_hits,
        "claim_boundary": {
            "runtime_executed": False,
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_rt_core_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "raw_optix_callback_api_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        },
        "conclusion": (
            "Goal4544 maintains a V3 current-scope app-author implementation strategy. "
            "It tells users how to choose primitives, partners, backends, and new "
            "primitive candidates after Goal4614/Goal4543, while preserving the "
            "blocked boundaries for release, public speedup, broad RT-core, paper "
            "reproduction, automatic partner selection, raw OptiX callback APIs, "
            "stable SDK/device-buffer/true-zero-copy wording, and app-specific "
            "native-engine logic."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4544 / V3 M145 App-Author Strategy Doc",
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
            "- No runtime was executed.",
            "- No release, public speedup, broad RT-core, paper-reproduction, automatic partner-selection, raw OptiX callback API, or app-specific native-engine wording is authorized.",
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
