#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON_OUT = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_major_performance_mandate_gate_2026-06-22.json"
)
MANDATE_DOC = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_redo_mandate_major_version_performance_2026-06-22.md"
)
PAIRED_BENCHMARK_DOC = (
    ROOT / "docs" / "rebuild" / "v3" / "v2_14_vs_v3_same_rt_hardware_paired_benchmark_2026-06-20.md"
)
SERIOUS_PAIRED_BENCHMARK_DOC = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_serious_v2x_paired_benchmark_2026-06-22.md"
)
SERIOUS_PAIRED_BENCHMARK_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_serious_v2x_paired_20260622_074100"
    / "summary.json"
)
CLAIM_GRADE_DOC = ROOT / "docs" / "rebuild" / "v3" / "v3_claim_grade_all_benchmark_results_2026-06-20.md"
DOSSIER_DOC = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_user_facing_performance_dossier_2026-06-22.md"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    mandate = _read(MANDATE_DOC)
    paired = _read(PAIRED_BENCHMARK_DOC)
    serious_paired = _read(SERIOUS_PAIRED_BENCHMARK_DOC)
    serious_payload = _read_json(SERIOUS_PAIRED_BENCHMARK_JSON)
    claim_grade = _read(CLAIM_GRADE_DOC)
    dossier = _read(DOSSIER_DOC)
    combined = "\n".join([mandate, paired, serious_paired, claim_grade, dossier])
    release_bar = serious_payload.get("release_consideration_bar", {})
    serious_rerun_completed = bool(release_bar.get("all_required_suites_finished"))
    serious_release_bar_failed = serious_payload.get("release_consideration_eligible") is False

    checks = {
        "mandate_doc_exists": MANDATE_DOC.exists(),
        "major_release_requires_broad_v2x_speedup": (
            "V3 major release requires broad V2.x performance superiority" in mandate
        ),
        "all_benchmark_apps_required": "all benchmark apps" in mandate.lower(),
        "current_same_rt_geomean_is_1_012x": "1.012x" in combined,
        "serious_paired_doc_exists": SERIOUS_PAIRED_BENCHMARK_DOC.exists(),
        "serious_paired_json_exists": SERIOUS_PAIRED_BENCHMARK_JSON.exists(),
        "serious_all_required_suites_finished": serious_rerun_completed,
        "serious_all_promoted_apps_covered": release_bar.get("missing_promoted_apps") == [],
        "serious_primary_metric_sources_match": (
            release_bar.get("primary_metric_source_mismatch_count") == 0
        ),
        "serious_release_bar_failed": serious_release_bar_failed,
        "current_evidence_says_not_major_broad_speedup": (
            "not a major broad speedup claim" in combined.lower()
            or "serious_paired_evidence_not_release" in combined
        ),
        "broad_claim_currently_not_authorized": (
            "broad_v3_faster_than_v2_claim_authorized: false" in combined
        ),
        "scoped_rows_not_enough_for_v3_major": (
            "current scoped 13-row surface is not sufficient to define V3" in mandate
        ),
    }
    failed_checks = [name for name, passed in checks.items() if not passed]
    status = "redo_required" if not failed_checks else "fail"
    serious_blocker = (
        "serious_all_app_paired_evidence_failed_release_bar"
        if serious_rerun_completed
        else "all_benchmark_apps_need_serious_pod_rerun"
    )

    return {
        "tool": "v3_phoenix_major_performance_mandate_gate",
        "gate": "phoenix_v3_major_version_performance_mandate",
        "status": status,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "blocking_reasons": [
            "broad_v2x_performance_not_proven",
            serious_blocker,
            "current_scoped_13_row_surface_not_v3_major_release",
        ],
        "failed_checks": failed_checks,
        "checks": checks,
        "evidence": {
            "mandate_doc": str(MANDATE_DOC.relative_to(ROOT)),
            "paired_benchmark_doc": str(PAIRED_BENCHMARK_DOC.relative_to(ROOT)),
            "serious_paired_benchmark_doc": str(SERIOUS_PAIRED_BENCHMARK_DOC.relative_to(ROOT)),
            "serious_paired_benchmark_json": str(SERIOUS_PAIRED_BENCHMARK_JSON.relative_to(ROOT)),
            "claim_grade_doc": str(CLAIM_GRADE_DOC.relative_to(ROOT)),
            "dossier_doc": str(DOSSIER_DOC.relative_to(ROOT)),
            "current_same_rt_geomean_summary": "1.012x is treated as insufficient for a V3 major-version claim.",
            "serious_same_rt_geomean_v3_speedup_vs_v2": serious_payload.get("v3_geomean_speedup_vs_v2"),
            "serious_same_rt_same_metric_comparison_count": serious_payload.get(
                "same_metric_comparison_count"
            ),
            "serious_same_rt_app_geomean_speedup_vs_v2": serious_payload.get(
                "app_geomean_speedup_vs_v2", {}
            ),
            "serious_same_rt_release_consideration_eligible": serious_payload.get(
                "release_consideration_eligible"
            ),
            "serious_same_rt_release_bar": release_bar,
            "required_next_evidence": (
                "generic runtime redesign and retest against the completed serious "
                "same-RT-hardware all-app paired benchmark bar; do not repeat the same "
                "suite as a substitute for fixing the failed performance contracts"
            ),
        },
        "decision_audit": {
            "decision": "Downgrade the scoped Phoenix V3 surface to redo_required because V3 must justify itself as a major version against V2.x performance.",
            "was_i_foolish": "Yes. Treating scoped row evidence as enough for V3 confused an internal capability packet with a major-version user promise.",
            "foolish_actions": "I let external scoped release review and row-scoped wins stand in for the user's real requirement: V3 must solve V2.x's performance problem broadly enough to deserve existing.",
            "other_path": "Keep publishing only row-scoped claims. That is honest but too small for a major V3 and would disappoint users who expect a language release to be clearly better.",
            "different_path_now": "Block release, keep the 13 rows as reusable internal evidence, and rebuild the generic runtime contracts that failed the completed serious all-app V3-vs-V2.x benchmark bar.",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phoenix V3 major-version performance mandate gate.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 2 if payload["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
